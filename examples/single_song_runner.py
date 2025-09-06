#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块: single_song_runner

单歌曲交互运行器 (MBUX Sound Drive 实现):
- 将 ACC 遥测数据映射到音乐表现力
- 支持多轨道音频控制 (鼓、贝斯、人声、其他)
- 实现平滑的参数过渡和实时响应
- 基于 Mercedes MBUX Sound Drive 概念设计

音乐表现力映射:
- 速度 -> 音乐能量密度 (master presence)
- 油门 -> 节奏推进感 (drums intensity)
- 刹车 -> 音乐呼吸空间 (bass reduction)
- 横向G力 -> 空间宽度 (stereo positioning)
- 转速 -> 音色亮度 (filter modulation)
"""

import json
import os

# 将项目根目录加入模块搜索路径
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData


class MusicalExpressionEngine:
    """
    音乐表现力引擎

    将驾驶输入映射到五个音乐表现状态：
    1. 能量密度 (Energy Density)
    2. 节奏推进 (Rhythmic Push)
    3. 呼吸空间 (Breathing Space)
    4. 空间宽度 (Spatial Width)
    5. 音色亮度 (Tonal Brightness)
    """

    def __init__(self):
        """初始化音乐表现力引擎"""
        # 音乐表现状态
        self.energy_density = 0.0  # 0-1 能量密度
        self.rhythmic_push = 0.0  # 0-1 节奏推进
        self.breathing_space = 0.0  # 0-1 呼吸空间
        self.spatial_width = 0.0  # 0-1 空间宽度
        self.tonal_brightness = 0.0  # 0-1 音色亮度

        # 平滑参数
        self.smoothing_coefficient = 0.12  # 平滑系数

        # 映射参数
        self.max_speed = 300.0  # 最大速度 (km/h)
        self.max_rpm = 8000.0  # 最大转速
        self.max_lateral_g = 3.0  # 最大横向G力

    def update(self, telemetry: TelemetryData) -> Dict[str, float]:
        """
        根据遥测数据更新音乐表现状态

        Args:
            telemetry: ACC遥测数据

        Returns:
            更新后的音乐表现状态字典
        """
        # 计算标准化输入
        speed_norm = min(telemetry.speed / self.max_speed, 1.0)
        throttle_norm = telemetry.throttle
        brake_norm = telemetry.brake
        lateral_g_norm = min(abs(telemetry.lateral_g) / self.max_lateral_g, 1.0)
        rpm_norm = min(telemetry.rpm / self.max_rpm, 1.0)

        # 计算目标值
        target_energy = speed_norm
        target_rhythmic = throttle_norm
        target_breathing = 1.0 - brake_norm
        target_spatial = lateral_g_norm
        target_tonal = rpm_norm

        # 应用平滑过渡
        self.energy_density = self._smooth_parameter(self.energy_density, target_energy)
        self.rhythmic_push = self._smooth_parameter(self.rhythmic_push, target_rhythmic)
        self.breathing_space = self._smooth_parameter(
            self.breathing_space, target_breathing
        )
        self.spatial_width = self._smooth_parameter(self.spatial_width, target_spatial)
        self.tonal_brightness = self._smooth_parameter(
            self.tonal_brightness, target_tonal
        )

        return {
            "energy_density": self.energy_density,
            "rhythmic_push": self.rhythmic_push,
            "breathing_space": self.breathing_space,
            "spatial_width": self.spatial_width,
            "tonal_brightness": self.tonal_brightness,
        }

    def _smooth_parameter(self, current: float, target: float) -> float:
        """
        平滑参数过渡

        Args:
            current: 当前值
            target: 目标值

        Returns:
            平滑后的值
        """
        return current + (target - current) * self.smoothing_coefficient


class SingleSongRunner:
    """
    单歌曲交互运行器

    负责单首歌曲的完整交互流程，包括：
    - 音频加载和播放
    - 遥测数据处理
    - 音乐参数实时映射
    - 多轨道音量控制
    """

    def __init__(self, song_path: str):
        """
        初始化单歌曲运行器

        Args:
            song_path: 歌曲目录路径
        """
        self.song_path = Path(song_path)
        self.song_name = self.song_path.name

        # 音频组件
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

        # 音频轨道
        self.channels = {}
        self.sounds = {}
        self.base_volumes = {}

        # 音乐表现力引擎
        self.expression_engine = MusicalExpressionEngine()

        # 遥测
        self.telemetry = ACCTelemetry()
        self._running = False
        self._thread = None

        # 加载歌曲数据
        self._load_song_data()
        self._load_audio_files()

    def _load_song_data(self):
        """加载歌曲分析数据"""
        analysis_file = self.song_path / "analysis.json"
        if analysis_file.exists():
            with open(analysis_file, "r", encoding="utf-8") as f:
                self.analysis = json.load(f)
        else:
            self.analysis = {
                "duration": 180.0,
                "bpm": 120.0,
                "artist": "Unknown",
                "genre": "Electronic",
            }

    def _load_audio_files(self):
        """加载音频文件"""
        required_stems = ["drums", "bass", "vocals", "other"]

        for stem in required_stems:
            audio_file = self.song_path / f"{stem}.wav"
            if audio_file.exists():
                try:
                    self.sounds[stem] = pygame.mixer.Sound(str(audio_file))
                    self.channels[stem] = pygame.mixer.Channel(len(self.channels))

                    # 设置基础音量
                    self.base_volumes[stem] = 0.8 if stem != "vocals" else 0.9

                    print(f"已加载: {stem}.wav")
                except Exception as e:
                    print(f"加载 {stem}.wav 失败: {e}")
            else:
                print(f"警告: 找不到 {stem}.wav")

    def start(self):
        """开始播放和遥测处理"""
        if not self.sounds:
            print("没有可用的音频文件")
            return

        # 开始播放所有轨道
        for stem, sound in self.sounds.items():
            if stem in self.channels:
                self.channels[stem].play(sound, loops=-1)
                self.channels[stem].set_volume(self.base_volumes[stem])

        self._running = True
        self._thread = threading.Thread(target=self._telemetry_loop, daemon=True)
        self._thread.start()

        print(f"开始播放: {self.song_name}")
        print("按 Ctrl+C 停止")

    def stop(self):
        """停止播放和清理资源"""
        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

        # 停止所有音频
        for channel in self.channels.values():
            channel.stop()

        pygame.mixer.stop()

        # 断开遥测连接
        try:
            self.telemetry.disconnect()
        except Exception as e:
            print(f"关闭遥测连接时发生错误: {e}")

        print(f"停止播放: {self.song_name}")

    def _telemetry_loop(self):
        """遥测数据处理主循环"""
        # 确保连接到ACC
        if not self.telemetry.is_connected():
            print("正在连接到ACC...")
            self.telemetry.connect()

        while self._running:
            try:
                telemetry = self.telemetry.read_data()
                if telemetry:
                    expressions = self.expression_engine.update(telemetry)
                    self._apply_expressions(expressions)

                time.sleep(1 / 60)  # 60Hz 更新频率

            except Exception as e:
                print(f"遥测处理错误: {e}")
                time.sleep(1)

    def _apply_expressions(self, expressions: Dict[str, float]):
        """
        应用音乐表现到音频轨道

        Args:
            expressions: 音乐表现状态字典
        """
        # 主音量控制 (基于速度)
        master_presence = 0.3 + (expressions["energy_density"] * 0.7)

        # 鼓组强度 (基于油门)
        drums_volume = self.base_volumes.get("drums", 0.8) * (
            0.6 + expressions["rhythmic_push"] * 0.4
        )

        # 贝斯呼吸 (基于刹车)
        bass_volume = self.base_volumes.get("bass", 0.8) * (
            0.4 + expressions["breathing_space"] * 0.6
        )

        # 人声稳定 (保持相对稳定)
        vocals_volume = self.base_volumes.get("vocals", 0.9)

        # 其他轨道 (基于空间宽度)
        other_volume = self.base_volumes.get("other", 0.8) * (
            0.5 + expressions["spatial_width"] * 0.5
        )

        # 应用音量
        if "drums" in self.channels:
            self.channels["drums"].set_volume(drums_volume * master_presence)

        if "bass" in self.channels:
            self.channels["bass"].set_volume(bass_volume * master_presence)

        if "vocals" in self.channels:
            self.channels["vocals"].set_volume(vocals_volume * master_presence)

        if "other" in self.channels:
            self.channels["other"].set_volume(other_volume * master_presence)

        # 立体声定位 (基于横向G力)
        pan_position = (expressions["spatial_width"] - 0.5) * 2.0
        pan_position = max(-1.0, min(1.0, pan_position))

        for stem, channel in self.channels.items():
            if stem != "vocals":  # 人声保持居中
                channel.set_volume(
                    channel.get_volume() * (1.0 - abs(pan_position) * 0.3)
                )


def main():
    """测试主函数"""
    # 使用示例
    song_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "songs", "htdemucs", "lose my mind"
    )

    if os.path.exists(song_dir):
        runner = SingleSongRunner(song_dir)
        try:
            runner.start()
            input("按回车键停止...")
        except KeyboardInterrupt:
            pass
        finally:
            runner.stop()
    else:
        print(f"歌曲目录不存在: {song_dir}")
        print("请确保已经使用 batch_song_processor.py 处理了歌曲")


if __name__ == "__main__":
    main()
