#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC遥测数据到音乐参数映射器

这个模块负责将ACC遥测数据转换为音乐参数。
通过分析各种车辆传感器数据，生成对应的音乐元素参数，
包括节奏、旋律、音效和氛围等多个维度。

作者: Assistant
日期: 2024
"""

import math
import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from ..core.telemetry import TelemetryData
from .audio_config import AudioConfig

@dataclass
class MusicParameters:
    """音乐参数数据类"""
    # 节奏参数
    bpm: float = 120.0
    beat_intensity: float = 0.7
    beat_pattern: str = "kick"
    
    # 旋律参数
    base_pitch: int = 60  # MIDI音符
    pitch_offset: float = 0.0  # 半音偏移
    volume: float = 0.7
    
    # 音效参数
    pan: float = 0.0  # 立体声平移 (-1.0 到 1.0)
    distortion: float = 0.0  # 失真强度 (0.0 到 1.0)
    reverb: float = 0.2  # 混响强度 (0.0 到 1.0)
    filter_freq: float = 1000.0  # 滤波器频率 (Hz)
    filter_resonance: float = 0.3  # 滤波器共振
    
    # 氛围参数
    warmth: float = 0.5  # 音色温暖度 (0.0 到 1.0)
    ambient_volume: float = 0.3
    
    # 特殊音效触发
    trigger_turbo_sound: bool = False
    trigger_drs_sound: bool = False
    trigger_warning_sound: bool = False
    trigger_celebration: bool = False
    
    # 时间戳
    timestamp: float = 0.0

class MusicMapper:
    """音乐映射器类
    
    负责将遥测数据转换为音乐参数
    """
    
    def __init__(self, config: AudioConfig):
        """初始化音乐映射器
        
        Args:
            config: 音频配置对象
        """
        self.config = config
        
        # 数据平滑缓存
        self._last_params: Optional[MusicParameters] = None
        self._last_telemetry: Optional[TelemetryData] = None
        
        # 状态跟踪
        self._last_best_lap: int = 0
        self._turbo_boost_threshold: float = 0.5
        self._drs_last_state: int = 0
        
        # 音阶定义
        self._scales = {
            'pentatonic': [0, 2, 4, 7, 9],  # 五声音阶
            'major': [0, 2, 4, 5, 7, 9, 11],  # 大调
            'minor': [0, 2, 3, 5, 7, 8, 10],  # 小调
            'blues': [0, 3, 5, 6, 7, 10],  # 蓝调音阶
            'dorian': [0, 2, 3, 5, 7, 9, 10]  # 多利亚调式
        }
        
        # 调性偏移
        self._key_offsets = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
    
    def map_telemetry_to_music(self, telemetry: TelemetryData) -> MusicParameters:
        """将遥测数据映射为音乐参数
        
        Args:
            telemetry: 遥测数据
            
        Returns:
            MusicParameters: 音乐参数
        """
        params = MusicParameters()
        params.timestamp = time.time()
        
        # 映射节奏参数
        if self.config.enable_rhythm:
            self._map_rhythm_parameters(telemetry, params)
        
        # 映射旋律参数
        if self.config.enable_melody:
            self._map_melody_parameters(telemetry, params)
        
        # 映射音效参数
        if self.config.enable_effects:
            self._map_effects_parameters(telemetry, params)
        
        # 映射氛围参数
        if self.config.enable_ambience:
            self._map_ambience_parameters(telemetry, params)
        
        # 应用平滑处理
        if self._last_params is not None:
            params = self._apply_smoothing(params, self._last_params)
        
        # 更新缓存
        self._last_params = params
        self._last_telemetry = telemetry
        
        return params
    
    def _map_rhythm_parameters(self, telemetry: TelemetryData, params: MusicParameters) -> None:
        """映射节奏参数
        
        Args:
            telemetry: 遥测数据
            params: 音乐参数对象
        """
        # RPM到BPM的映射
        rpm_normalized = self._normalize_value(
            telemetry.rpm,
            self.config.rhythm.rpm_range[0],
            self.config.rhythm.rpm_range[1]
        )
        rpm_normalized *= self.config.rhythm.rpm_sensitivity
        rpm_normalized = max(0.0, min(1.0, rpm_normalized))
        
        params.bpm = self._lerp(
            self.config.rhythm.bpm_range[0],
            self.config.rhythm.bpm_range[1],
            rpm_normalized
        )
        
        # 速度到节拍强度的映射
        speed_normalized = self._normalize_value(
            telemetry.speed,
            self.config.rhythm.speed_range[0],
            self.config.rhythm.speed_range[1]
        )
        speed_normalized *= self.config.rhythm.speed_sensitivity
        speed_normalized = max(0.0, min(1.0, speed_normalized))
        
        params.beat_intensity = self._lerp(
            self.config.rhythm.beat_intensity_range[0],
            self.config.rhythm.beat_intensity_range[1],
            speed_normalized
        )
        
        # 档位到节拍模式的映射
        gear = max(1, min(6, telemetry.gear))
        params.beat_pattern = self.config.rhythm.gear_beat_patterns.get(gear, "kick")
    
    def _map_melody_parameters(self, telemetry: TelemetryData, params: MusicParameters) -> None:
        """映射旋律参数
        
        Args:
            telemetry: 遥测数据
            params: 音乐参数对象
        """
        # 基础音调
        params.base_pitch = self.config.melody.base_pitch
        
        # 转向角度到音调偏移的映射
        steer_normalized = self._normalize_value(
            telemetry.steer_angle,
            self.config.melody.steer_angle_range[0],
            self.config.melody.steer_angle_range[1]
        )
        steer_normalized *= self.config.melody.steer_sensitivity
        steer_normalized = max(-1.0, min(1.0, steer_normalized))
        
        steer_pitch_offset = steer_normalized * self.config.melody.steer_pitch_influence
        
        # 油门到音量的映射
        throttle_normalized = telemetry.throttle * self.config.melody.throttle_sensitivity
        throttle_normalized = max(0.0, min(1.0, throttle_normalized))
        
        params.volume = self._lerp(
            self.config.melody.throttle_volume_range[0],
            self.config.melody.throttle_volume_range[1],
            throttle_normalized
        )
        
        # 刹车到音调下降的映射
        brake_normalized = telemetry.brake * self.config.melody.brake_sensitivity
        brake_pitch_offset = -brake_normalized * self.config.melody.brake_pitch_drop
        
        # 组合音调偏移
        total_pitch_offset = steer_pitch_offset + brake_pitch_offset
        
        # 量化到音阶
        params.pitch_offset = self._quantize_to_scale(total_pitch_offset)
    
    def _map_effects_parameters(self, telemetry: TelemetryData, params: MusicParameters) -> None:
        """映射音效参数
        
        Args:
            telemetry: 遥测数据
            params: 音乐参数对象
        """
        # 横向G力到立体声平移的映射
        lateral_g_normalized = self._normalize_value(
            telemetry.acceleration_x,
            self.config.effects.lateral_g_range[0],
            self.config.effects.lateral_g_range[1]
        )
        lateral_g_normalized *= self.config.effects.effects_sensitivity
        lateral_g_normalized = max(-1.0, min(1.0, lateral_g_normalized))
        
        params.pan = self._lerp(
            self.config.effects.pan_range[0],
            self.config.effects.pan_range[1],
            (lateral_g_normalized + 1.0) / 2.0
        )
        
        # 轮胎滑移到失真效果的映射
        max_wheel_slip = max(
            telemetry.wheel_slip_fl,
            telemetry.wheel_slip_fr,
            telemetry.wheel_slip_rl,
            telemetry.wheel_slip_rr
        )
        
        if max_wheel_slip > self.config.effects.wheel_slip_threshold:
            slip_normalized = min(1.0, max_wheel_slip / 1.0)  # 假设最大滑移为1.0
            params.distortion = self._lerp(
                self.config.effects.distortion_range[0],
                self.config.effects.distortion_range[1],
                slip_normalized
            )
        
        # 速度到混响的映射
        speed_normalized = self._normalize_value(
            telemetry.speed,
            self.config.effects.speed_reverb_range[0],
            self.config.effects.speed_reverb_range[1]
        )
        speed_normalized = max(0.0, min(1.0, speed_normalized))
        
        params.reverb = self._lerp(
            self.config.effects.reverb_range[0],
            self.config.effects.reverb_range[1],
            speed_normalized
        )
        
        # 引擎温度到滤波器频率的映射
        temp_normalized = self._normalize_value(
            telemetry.engine_temp,
            self.config.effects.engine_temp_range[0],
            self.config.effects.engine_temp_range[1]
        )
        temp_normalized = max(0.0, min(1.0, temp_normalized))
        
        params.filter_freq = self._lerp(
            self.config.effects.filter_freq_range[0],
            self.config.effects.filter_freq_range[1],
            temp_normalized
        )
        
        # 特殊音效触发检测
        self._detect_special_effects(telemetry, params)
    
    def _map_ambience_parameters(self, telemetry: TelemetryData, params: MusicParameters) -> None:
        """映射氛围参数
        
        Args:
            telemetry: 遥测数据
            params: 音乐参数对象
        """
        # 引擎温度到音色温暖度的映射
        temp_normalized = self._normalize_value(
            telemetry.engine_temp,
            self.config.ambience.temp_range[0],
            self.config.ambience.temp_range[1]
        )
        temp_normalized = max(0.0, min(1.0, temp_normalized))
        
        params.warmth = self._lerp(
            self.config.ambience.warmth_range[0],
            self.config.ambience.warmth_range[1],
            temp_normalized
        )
        
        # 设置氛围音量
        params.ambient_volume = self.config.ambience.ambient_volume
        
        # 检测圈速表现
        if (self.config.ambience.enable_lap_feedback and 
            self.config.ambience.best_lap_celebration):
            if (telemetry.best_lap > 0 and 
                self._last_best_lap > 0 and 
                telemetry.best_lap < self._last_best_lap):
                params.trigger_celebration = True
            self._last_best_lap = telemetry.best_lap
    
    def _detect_special_effects(self, telemetry: TelemetryData, params: MusicParameters) -> None:
        """检测特殊音效触发条件
        
        Args:
            telemetry: 遥测数据
            params: 音乐参数对象
        """
        # 涡轮增压音效
        if (self.config.effects.enable_turbo_sound and 
            telemetry.turbo_boost > self._turbo_boost_threshold):
            params.trigger_turbo_sound = True
        
        # DRS音效
        if (self.config.effects.enable_drs_sound and 
            telemetry.drs != self._drs_last_state and 
            telemetry.drs > 0):
            params.trigger_drs_sound = True
        self._drs_last_state = telemetry.drs
        
        # 牵引力控制/ABS警告音
        if (self.config.effects.enable_tc_abs_sound and 
            self.config.ambience.enable_warning_sounds):
            if telemetry.tc > 0 or telemetry.abs > 0:
                params.trigger_warning_sound = True
    
    def _quantize_to_scale(self, pitch_offset: float) -> float:
        """将音调偏移量化到指定音阶
        
        Args:
            pitch_offset: 原始音调偏移（半音）
            
        Returns:
            float: 量化后的音调偏移
        """
        scale_notes = self._scales.get(self.config.melody.scale_type, self._scales['pentatonic'])
        key_offset = self._key_offsets.get(self.config.melody.key, 0)
        
        # 转换为相对于C的半音数
        total_semitones = pitch_offset + key_offset
        
        # 找到最接近的音阶音符
        octave = int(total_semitones // 12)
        semitone_in_octave = total_semitones % 12
        
        # 找到音阶中最接近的音符
        closest_note = min(scale_notes, key=lambda note: abs(note - semitone_in_octave))
        
        # 计算量化后的偏移
        quantized_semitones = octave * 12 + closest_note
        
        return quantized_semitones - key_offset
    
    def _apply_smoothing(self, current: MusicParameters, last: MusicParameters, 
                        smoothing_factor: float = 0.1) -> MusicParameters:
        """应用参数平滑处理
        
        Args:
            current: 当前参数
            last: 上一次参数
            smoothing_factor: 平滑因子 (0-1)
            
        Returns:
            MusicParameters: 平滑后的参数
        """
        smoothed = MusicParameters()
        
        # 平滑数值参数
        smoothed.bpm = self._smooth_value(current.bpm, last.bpm, smoothing_factor)
        smoothed.beat_intensity = self._smooth_value(current.beat_intensity, last.beat_intensity, smoothing_factor)
        smoothed.pitch_offset = self._smooth_value(current.pitch_offset, last.pitch_offset, smoothing_factor)
        smoothed.volume = self._smooth_value(current.volume, last.volume, smoothing_factor)
        smoothed.pan = self._smooth_value(current.pan, last.pan, smoothing_factor)
        smoothed.distortion = self._smooth_value(current.distortion, last.distortion, smoothing_factor)
        smoothed.reverb = self._smooth_value(current.reverb, last.reverb, smoothing_factor)
        smoothed.filter_freq = self._smooth_value(current.filter_freq, last.filter_freq, smoothing_factor)
        smoothed.warmth = self._smooth_value(current.warmth, last.warmth, smoothing_factor)
        
        # 非数值参数直接使用当前值
        smoothed.base_pitch = current.base_pitch
        smoothed.beat_pattern = current.beat_pattern
        smoothed.filter_resonance = current.filter_resonance
        smoothed.ambient_volume = current.ambient_volume
        smoothed.timestamp = current.timestamp
        
        # 触发器参数直接使用当前值
        smoothed.trigger_turbo_sound = current.trigger_turbo_sound
        smoothed.trigger_drs_sound = current.trigger_drs_sound
        smoothed.trigger_warning_sound = current.trigger_warning_sound
        smoothed.trigger_celebration = current.trigger_celebration
        
        return smoothed
    
    def _smooth_value(self, current: float, last: float, factor: float) -> float:
        """平滑单个数值
        
        Args:
            current: 当前值
            last: 上一次值
            factor: 平滑因子
            
        Returns:
            float: 平滑后的值
        """
        return last + (current - last) * factor
    
    def _normalize_value(self, value: float, min_val: float, max_val: float) -> float:
        """将值标准化到0-1范围
        
        Args:
            value: 输入值
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            float: 标准化后的值 (0-1)
        """
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)
    
    def _lerp(self, start: float, end: float, t: float) -> float:
        """线性插值
        
        Args:
            start: 起始值
            end: 结束值
            t: 插值参数 (0-1)
            
        Returns:
            float: 插值结果
        """
        return start + (end - start) * t
    
    def update_config(self, config: AudioConfig) -> None:
        """更新配置
        
        Args:
            config: 新的音频配置
        """
        self.config = config
    
    def reset_state(self) -> None:
        """重置映射器状态"""
        self._last_params = None
        self._last_telemetry = None
        self._last_best_lap = 0
        self._drs_last_state = 0
    
    def get_current_parameters(self) -> Optional[MusicParameters]:
        """获取当前音乐参数
        
        Returns:
            Optional[MusicParameters]: 当前音乐参数，如果没有则返回None
        """
        return self._last_params