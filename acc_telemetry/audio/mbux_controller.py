#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块: mbux_controller

将 MBUX Sound Drive 风格的“驾驶即作曲”理念集成到主项目应用中。
本模块提供一个基于遥测数据的音乐控制器, 通过将车辆输入映射为音乐表现力,
生成 MusicParameters 并交给 MusicEngine 播放(当前后端为模拟引擎)。

主要组成:
- MusicalExpressionEngine: 轻量表达引擎, 将速度/油门/刹车/横向G/转速转为音乐表现力状态
- MBUXSoundDriveController: 控制器, 读取遥测, 计算 MusicParameters, 推送到 MusicEngine

注意:
- 本实现聚焦交互逻辑与工程集成, 不做任何 DSP 处理。
- 实际音频后端可在未来替换为专业方案(如 SuperCollider, JUCE 等)。

作者: Assistant
日期: 2024
"""

from __future__ import annotations

import math
import threading
import time
from typing import Any, Dict, Optional

from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData

from .audio_config import AudioConfig
from .music_engine import MusicEngine
from .music_mapper import MusicParameters


class MusicalExpressionEngine:
    """音乐表现力引擎

    将车辆驾驶输入转化为音乐表现力调制, 借鉴 MBUX Sound Drive 的核心理念:
    车辆成为虚拟乐器, 驾驶者成为实时作曲者。
    """

    def __init__(self) -> None:
        """初始化表达引擎"""
        # 表现力状态
        self.energy_density = 0.5  # 能量密度(速度驱动)
        self.rhythmic_push = 0.5  # 节拍推力(油门驱动)
        self.breathing_space = 0.5  # 呼吸空间(刹车驱动)
        self.spatial_width = 0.0  # 立体宽度(横向G驱动)
        self.tonal_brightness = 0.5  # 音色亮度(转速驱动)

        # 平滑滤波
        self.smoothing_factor = 0.12

    # ---------------------------------------------------------------------
    # 更新与取值
    # ---------------------------------------------------------------------
    def update(
        self, speed: float, throttle: float, brake: float, lat_g: float, rpm: float
    ) -> None:
        """根据驾驶输入更新表现力状态"""
        # 能量密度: 低速轻柔, 高速饱满
        if speed <= 50:
            target_energy = 0.2 + 0.3 * (speed / 50.0)
        elif speed <= 230:
            target_energy = 0.5 + 0.3 * ((speed - 50) / 70.0)
        else:
            target_energy = 0.8 + 0.2 * min(1.0, (speed - 230) / 80.0)
        self.energy_density = self._smooth(self.energy_density, target_energy)

        # 节拍推力: 油门
        target_push = 0.3 + 0.7 * max(0.0, min(1.0, throttle))
        self.rhythmic_push = self._smooth(self.rhythmic_push, target_push)

        # 呼吸空间: 刹车越强, 给出更多呼吸
        target_breathing = 1.0 - 0.4 * max(0.0, min(1.0, brake))
        self.breathing_space = self._smooth(self.breathing_space, target_breathing)

        # 立体宽度: 横向G
        target_width = max(-1.0, min(1.0, lat_g / 3.0))
        self.spatial_width = self._smooth(self.spatial_width, target_width, factor=0.08)

        # 音色亮度: 转速
        rpm_norm = max(0.0, min(1.0, (rpm - 2000) / 6000))
        target_brightness = 0.4 + 0.6 * rpm_norm
        self.tonal_brightness = self._smooth(self.tonal_brightness, target_brightness)

    def get_master_presence(self, speed: float) -> float:
        """基于速度的主存在感(替代传统主音量)"""
        if speed <= 30:
            base_presence = 0.25 + 0.15 * (speed / 30.0)
        elif speed <= 80:
            base_presence = 0.4 + 0.3 * ((speed - 30) / 50.0)
        else:
            progress = min(1.0, (speed - 80) / 60.0)
            base_presence = 0.7 + 0.25 * math.sqrt(progress)
        return max(0.2, min(0.95, base_presence * (0.8 + 0.2 * self.energy_density)))

    def get_spatial_position(self, base_pan: float) -> float:
        """将机械声像转化为空间表达"""
        musical_pan = base_pan + self.spatial_width * 0.3
        time_breath = 0.1 * math.sin(time.time() * 0.5)
        final_position = musical_pan + time_breath
        return max(-1.0, min(1.0, final_position))

    # ---------------------------------------------------------------------
    # 工具
    # ---------------------------------------------------------------------
    def _smooth(
        self, current: float, target: float, factor: Optional[float] = None
    ) -> float:
        alpha = factor if factor is not None else self.smoothing_factor
        return current * (1 - alpha) + target * alpha


class MBUXSoundDriveController:
    """MBUX 风格音乐控制器

    - 周期性读取 ACC 遥测
    - 通过 MusicalExpressionEngine 计算表现力
    - 将结果映射为 MusicParameters 并推送到 MusicEngine
    """

    def __init__(
        self, config: Optional[AudioConfig] = None, engine: Optional[MusicEngine] = None
    ) -> None:
        """初始化控制器

        Args:
            config: 音频配置(可选), 未传入则使用默认
            engine: 音乐引擎(可选), 未传入则内部创建
        """
        self.config = config or AudioConfig()
        self.engine = engine or MusicEngine(self.config)

        self.expr = MusicalExpressionEngine()
        self.telemetry = ACCTelemetry()

        self._running = False
        self._thread: Optional[threading.Thread] = None

        # 状态属性
        self.paused_due_to_no_data = False

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    def start(self) -> None:
        """启动控制器与音乐引擎"""
        if self._running:
            return
        self._running = True
        self.engine.start()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止控制器并清理资源"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        try:
            self.telemetry.close()
        finally:
            self.engine.stop()

    def get_status(self) -> Dict[str, Any]:
        """
        获取控制器状态

        Returns:
            Dict[str, Any]: 控制器状态字典
        """
        engine_status = self.engine.get_status()

        return {
            "is_running": self._running,
            "paused_due_to_no_data": self.paused_due_to_no_data,
            "engine_status": engine_status,
            "expression_engine": {
                "energy_density": self.expr.energy_density,
                "rhythmic_push": self.expr.rhythmic_push,
                "breathing_space": self.expr.breathing_space,
                "spatial_width": self.expr.spatial_width,
                "tonal_brightness": self.expr.tonal_brightness,
            },
            "config": {
                "auto_pause_timeout": getattr(self.config, "auto_pause_timeout", 0.5),
                "enable_fade_transition": getattr(
                    self.config, "enable_fade_transition", True
                ),
                "fade_duration": getattr(self.config, "fade_duration", 0.2),
                "update_rate": self.config.update_rate,
            },
        }

    # ------------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------------
    def _loop(self) -> None:
        """读取遥测并驱动音乐引擎"""
        last_params_time = 0.0
        target_hz = max(10, int(self.config.update_rate))  # 防御性: 至少10Hz
        interval = 1.0 / target_hz

        # 额外: 跟踪最近一次成功遥测时间, 控制自动暂停/恢复
        last_data_ts = 0.0

        # 使用配置化的超时时间
        pause_timeout = getattr(self.config, "auto_pause_timeout", 0.5)
        enable_fade = getattr(self.config, "enable_fade_transition", True)
        fade_duration = getattr(self.config, "fade_duration", 0.2)

        while self._running:
            try:
                data = self.telemetry.get_telemetry()
                now = time.time()

                if data is None:
                    # 无遥测数据: 在配置的超时时间后暂停
                    if (
                        now - last_data_ts
                    ) > pause_timeout and not self.paused_due_to_no_data:
                        if enable_fade:
                            self.engine.fade_pause(fade_duration)
                        else:
                            self.engine.pause()
                        self.paused_due_to_no_data = True

                        # 可选的调试日志
                        if getattr(self.config, "enable_verbose_logging", False):
                            print(
                                f"[MBUXController] 因无遥测数据暂停音乐 (超时: {pause_timeout}s)"
                            )
                    time.sleep(0.05)
                    continue

                # 有数据: 如因无数据而暂停过, 则恢复
                last_data_ts = now
                if self.paused_due_to_no_data:
                    if enable_fade:
                        self.engine.fade_resume(fade_duration)
                    else:
                        self.engine.resume()
                    self.paused_due_to_no_data = False

                    # 可选的调试日志
                    if getattr(self.config, "enable_verbose_logging", False):
                        print("[MBUXController] 遥测恢复，恢复音乐播放")

                # 更新表现力
                self._update_expression(data)

                # 产生参数并推送
                params = self._make_music_params(data)
                params.timestamp = now
                self.engine.update_parameters(params)
                self.engine.set_master_volume(params.volume)

                # 控制速率
                elapsed = now - last_params_time
                sleep_time = max(0.0, interval - elapsed)
                time.sleep(sleep_time)
                last_params_time = now

            except Exception as e:
                # 简单打印并继续, 避免线程退出
                print(f"[MBUXController] 循环错误: {e}")
                time.sleep(0.05)

    # ------------------------------------------------------------------
    # 计算逻辑
    # ------------------------------------------------------------------
    def _update_expression(self, d: TelemetryData) -> None:
        """根据遥测更新表现力引擎"""
        lat_g = d.acceleration_x  # 横向 G
        self.expr.update(d.speed, d.throttle, d.brake, lat_g, float(d.rpm))

    def _make_music_params(self, d: TelemetryData) -> MusicParameters:
        """将表达引擎状态与遥测映射为 MusicParameters"""
        # 1) BPM: 结合速度与转速
        speed_norm = max(0.0, min(1.0, d.speed / 260.0))
        rpm_norm = max(0.0, min(1.0, (d.rpm - 2000) / 6000))
        bpm = 90.0 + 50.0 * speed_norm + 20.0 * rpm_norm

        # 2) 主存在感与空间
        presence = self.expr.get_master_presence(d.speed)
        base_pan = d.acceleration_x / 4.0
        pan = self.expr.get_spatial_position(base_pan)

        # 3) 基础音高: 以 C4 为基, 随转速轻微上扬
        base_pitch = 58 + int(8 * rpm_norm)  # 约 C#4 ~ G4

        # 4) 音色亮度/混响/失真
        brightness = self.expr.tonal_brightness
        reverb_amount = 0.15 + 0.5 * (
            1.0 - self.expr.breathing_space
        )  # 刹车更多 -> 空间感更强

        # 使用轮胎滑移估计粗糙的失真量(如无该值, 也不会报错)
        slip_vals = [
            getattr(d, n, 0.0)
            for n in (
                "wheel_slip_fl",
                "wheel_slip_fr",
                "wheel_slip_rl",
                "wheel_slip_rr",
            )
        ]
        slip_avg = sum(slip_vals) / len(slip_vals)
        distortion_amount = max(0.0, min(0.8, slip_avg))

        # 5) 一次性触发事件
        trigger_turbo = bool(d.turbo_boost and d.turbo_boost > 0.8)
        trigger_drs = bool(getattr(d, "drs", 0) == 1)
        warn_low_fuel = bool(d.fuel < 5.0)
        trigger_warning = warn_low_fuel

        # 组装
        return MusicParameters(
            bpm=bpm,
            volume=presence,
            base_pitch=base_pitch,
            pan=pan,
            brightness=brightness,
            reverb_amount=max(0.0, min(1.0, reverb_amount)),
            distortion_amount=max(0.0, min(1.0, distortion_amount)),
            trigger_turbo_sound=trigger_turbo,
            trigger_drs_sound=trigger_drs,
            trigger_warning_sound=trigger_warning,
            trigger_celebration=False,
        )
