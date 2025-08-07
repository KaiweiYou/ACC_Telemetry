#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC遥测交互音乐配置模块

定义音乐生成的各种参数、映射规则和用户配置选项。
提供灵活的配置系统，允许用户自定义音乐生成的各个方面。

作者: Assistant
日期: 2024
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional
import json
import os

@dataclass
class RhythmConfig:
    """节奏配置类"""
    # BPM范围映射
    bpm_range: Tuple[int, int] = (60, 180)
    rpm_range: Tuple[int, int] = (1000, 8000)
    
    # 节拍强度映射
    beat_intensity_range: Tuple[float, float] = (0.3, 1.0)
    speed_range: Tuple[float, float] = (0, 300)  # km/h
    
    # 节拍模式（根据档位）
    gear_beat_patterns: Dict[int, str] = field(default_factory=lambda: {
        1: "kick",      # 低档位：重踢鼓
        2: "kick_snare", # 中档位：踢鼓+军鼓
        3: "full_kit",   # 高档位：完整鼓组
        4: "electronic", # 更高档位：电子鼓
        5: "complex",    # 最高档位：复杂节拍
        6: "race_mode"   # 赛车模式
    })
    
    # 敏感度设置
    rpm_sensitivity: float = 1.0
    speed_sensitivity: float = 1.0

@dataclass
class MelodyConfig:
    """旋律配置类"""
    # 音调范围（MIDI音符）
    pitch_range: Tuple[int, int] = (36, 84)  # C2 to C6
    base_pitch: int = 60  # C4
    
    # 转向角度到音调的映射
    steer_angle_range: Tuple[float, float] = (-540, 540)  # 度
    steer_pitch_influence: float = 12  # 半音数
    
    # 油门刹车到音量和音调的映射
    throttle_volume_range: Tuple[float, float] = (0.3, 1.0)
    brake_pitch_drop: float = 6  # 刹车时音调下降的半音数
    
    # 音阶设置
    scale_type: str = "pentatonic"  # pentatonic, major, minor, blues
    key: str = "C"  # 调性
    
    # 敏感度设置
    steer_sensitivity: float = 1.0
    throttle_sensitivity: float = 1.0
    brake_sensitivity: float = 1.0

@dataclass
class EffectsConfig:
    """音效配置类"""
    # 立体声平移（基于横向G力）
    pan_range: Tuple[float, float] = (-1.0, 1.0)
    lateral_g_range: Tuple[float, float] = (-3.0, 3.0)
    
    # 失真效果（基于轮胎滑移）
    distortion_range: Tuple[float, float] = (0.0, 0.8)
    wheel_slip_threshold: float = 0.1
    
    # 混响效果（基于速度）
    reverb_range: Tuple[float, float] = (0.1, 0.6)
    speed_reverb_range: Tuple[float, float] = (50, 250)  # km/h
    
    # 滤波器（基于引擎温度）
    filter_freq_range: Tuple[float, float] = (200, 8000)  # Hz
    engine_temp_range: Tuple[float, float] = (70, 120)  # 摄氏度
    
    # 特殊音效开关
    enable_turbo_sound: bool = True
    enable_drs_sound: bool = True
    enable_tc_abs_sound: bool = True
    
    # 敏感度设置
    effects_sensitivity: float = 1.0

@dataclass
class AmbienceConfig:
    """氛围配置类"""
    # 引擎温度到音色温暖度
    warmth_range: Tuple[float, float] = (0.2, 0.9)
    temp_range: Tuple[float, float] = (70, 120)
    
    # 圈速表现到音乐情绪
    enable_lap_feedback: bool = True
    best_lap_celebration: bool = True
    
    # 危险状况警告音
    enable_warning_sounds: bool = True
    warning_volume: float = 0.7
    
    # 背景氛围音
    ambient_volume: float = 0.3
    ambient_type: str = "engine_hum"  # engine_hum, wind, road

@dataclass
class AudioConfig:
    """音频系统总配置类"""
    # 子配置
    rhythm: RhythmConfig = field(default_factory=RhythmConfig)
    melody: MelodyConfig = field(default_factory=MelodyConfig)
    effects: EffectsConfig = field(default_factory=EffectsConfig)
    ambience: AmbienceConfig = field(default_factory=AmbienceConfig)
    
    # 全局音频设置
    master_volume: float = 0.8
    sample_rate: int = 44100
    buffer_size: int = 512
    
    # 更新频率
    update_rate: int = 60  # Hz
    
    # 音频输出设备
    output_device: Optional[str] = None  # None表示默认设备
    
    # 启用的音乐层
    enable_rhythm: bool = True
    enable_melody: bool = True
    enable_effects: bool = True
    enable_ambience: bool = True
    
    # 预设配置
    current_preset: str = "default"
    
    def save_to_file(self, filepath: str) -> None:
        """保存配置到文件
        
        Args:
            filepath: 配置文件路径
        """
        try:
            config_dict = {
                'rhythm': {
                    'bpm_range': self.rhythm.bpm_range,
                    'rpm_range': self.rhythm.rpm_range,
                    'beat_intensity_range': self.rhythm.beat_intensity_range,
                    'speed_range': self.rhythm.speed_range,
                    'gear_beat_patterns': self.rhythm.gear_beat_patterns,
                    'rpm_sensitivity': self.rhythm.rpm_sensitivity,
                    'speed_sensitivity': self.rhythm.speed_sensitivity
                },
                'melody': {
                    'pitch_range': self.melody.pitch_range,
                    'base_pitch': self.melody.base_pitch,
                    'steer_angle_range': self.melody.steer_angle_range,
                    'steer_pitch_influence': self.melody.steer_pitch_influence,
                    'throttle_volume_range': self.melody.throttle_volume_range,
                    'brake_pitch_drop': self.melody.brake_pitch_drop,
                    'scale_type': self.melody.scale_type,
                    'key': self.melody.key,
                    'steer_sensitivity': self.melody.steer_sensitivity,
                    'throttle_sensitivity': self.melody.throttle_sensitivity,
                    'brake_sensitivity': self.melody.brake_sensitivity
                },
                'effects': {
                    'pan_range': self.effects.pan_range,
                    'lateral_g_range': self.effects.lateral_g_range,
                    'distortion_range': self.effects.distortion_range,
                    'wheel_slip_threshold': self.effects.wheel_slip_threshold,
                    'reverb_range': self.effects.reverb_range,
                    'speed_reverb_range': self.effects.speed_reverb_range,
                    'filter_freq_range': self.effects.filter_freq_range,
                    'engine_temp_range': self.effects.engine_temp_range,
                    'enable_turbo_sound': self.effects.enable_turbo_sound,
                    'enable_drs_sound': self.effects.enable_drs_sound,
                    'enable_tc_abs_sound': self.effects.enable_tc_abs_sound,
                    'effects_sensitivity': self.effects.effects_sensitivity
                },
                'ambience': {
                    'warmth_range': self.ambience.warmth_range,
                    'temp_range': self.ambience.temp_range,
                    'enable_lap_feedback': self.ambience.enable_lap_feedback,
                    'best_lap_celebration': self.ambience.best_lap_celebration,
                    'enable_warning_sounds': self.ambience.enable_warning_sounds,
                    'warning_volume': self.ambience.warning_volume,
                    'ambient_volume': self.ambience.ambient_volume,
                    'ambient_type': self.ambience.ambient_type
                },
                'global': {
                    'master_volume': self.master_volume,
                    'sample_rate': self.sample_rate,
                    'buffer_size': self.buffer_size,
                    'update_rate': self.update_rate,
                    'output_device': self.output_device,
                    'enable_rhythm': self.enable_rhythm,
                    'enable_melody': self.enable_melody,
                    'enable_effects': self.enable_effects,
                    'enable_ambience': self.enable_ambience,
                    'current_preset': self.current_preset
                }
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"保存配置文件失败: {e}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'AudioConfig':
        """从文件加载配置
        
        Args:
            filepath: 配置文件路径
            
        Returns:
            AudioConfig: 加载的配置对象
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 创建配置对象
            config = cls()
            
            # 加载节奏配置
            if 'rhythm' in config_dict:
                rhythm_data = config_dict['rhythm']
                config.rhythm = RhythmConfig(
                    bpm_range=tuple(rhythm_data.get('bpm_range', (60, 180))),
                    rpm_range=tuple(rhythm_data.get('rpm_range', (1000, 8000))),
                    beat_intensity_range=tuple(rhythm_data.get('beat_intensity_range', (0.3, 1.0))),
                    speed_range=tuple(rhythm_data.get('speed_range', (0, 300))),
                    gear_beat_patterns=rhythm_data.get('gear_beat_patterns', {}),
                    rpm_sensitivity=rhythm_data.get('rpm_sensitivity', 1.0),
                    speed_sensitivity=rhythm_data.get('speed_sensitivity', 1.0)
                )
            
            # 加载旋律配置
            if 'melody' in config_dict:
                melody_data = config_dict['melody']
                config.melody = MelodyConfig(
                    pitch_range=tuple(melody_data.get('pitch_range', (36, 84))),
                    base_pitch=melody_data.get('base_pitch', 60),
                    steer_angle_range=tuple(melody_data.get('steer_angle_range', (-540, 540))),
                    steer_pitch_influence=melody_data.get('steer_pitch_influence', 12),
                    throttle_volume_range=tuple(melody_data.get('throttle_volume_range', (0.3, 1.0))),
                    brake_pitch_drop=melody_data.get('brake_pitch_drop', 6),
                    scale_type=melody_data.get('scale_type', 'pentatonic'),
                    key=melody_data.get('key', 'C'),
                    steer_sensitivity=melody_data.get('steer_sensitivity', 1.0),
                    throttle_sensitivity=melody_data.get('throttle_sensitivity', 1.0),
                    brake_sensitivity=melody_data.get('brake_sensitivity', 1.0)
                )
            
            # 加载音效配置
            if 'effects' in config_dict:
                effects_data = config_dict['effects']
                config.effects = EffectsConfig(
                    pan_range=tuple(effects_data.get('pan_range', (-1.0, 1.0))),
                    lateral_g_range=tuple(effects_data.get('lateral_g_range', (-3.0, 3.0))),
                    distortion_range=tuple(effects_data.get('distortion_range', (0.0, 0.8))),
                    wheel_slip_threshold=effects_data.get('wheel_slip_threshold', 0.1),
                    reverb_range=tuple(effects_data.get('reverb_range', (0.1, 0.6))),
                    speed_reverb_range=tuple(effects_data.get('speed_reverb_range', (50, 250))),
                    filter_freq_range=tuple(effects_data.get('filter_freq_range', (200, 8000))),
                    engine_temp_range=tuple(effects_data.get('engine_temp_range', (70, 120))),
                    enable_turbo_sound=effects_data.get('enable_turbo_sound', True),
                    enable_drs_sound=effects_data.get('enable_drs_sound', True),
                    enable_tc_abs_sound=effects_data.get('enable_tc_abs_sound', True),
                    effects_sensitivity=effects_data.get('effects_sensitivity', 1.0)
                )
            
            # 加载氛围配置
            if 'ambience' in config_dict:
                ambience_data = config_dict['ambience']
                config.ambience = AmbienceConfig(
                    warmth_range=tuple(ambience_data.get('warmth_range', (0.2, 0.9))),
                    temp_range=tuple(ambience_data.get('temp_range', (70, 120))),
                    enable_lap_feedback=ambience_data.get('enable_lap_feedback', True),
                    best_lap_celebration=ambience_data.get('best_lap_celebration', True),
                    enable_warning_sounds=ambience_data.get('enable_warning_sounds', True),
                    warning_volume=ambience_data.get('warning_volume', 0.7),
                    ambient_volume=ambience_data.get('ambient_volume', 0.3),
                    ambient_type=ambience_data.get('ambient_type', 'engine_hum')
                )
            
            # 加载全局配置
            if 'global' in config_dict:
                global_data = config_dict['global']
                config.master_volume = global_data.get('master_volume', 0.8)
                config.sample_rate = global_data.get('sample_rate', 44100)
                config.buffer_size = global_data.get('buffer_size', 512)
                config.update_rate = global_data.get('update_rate', 60)
                config.output_device = global_data.get('output_device')
                config.enable_rhythm = global_data.get('enable_rhythm', True)
                config.enable_melody = global_data.get('enable_melody', True)
                config.enable_effects = global_data.get('enable_effects', True)
                config.enable_ambience = global_data.get('enable_ambience', True)
                config.current_preset = global_data.get('current_preset', 'default')
            
            return config
            
        except FileNotFoundError:
            # 文件不存在时返回默认配置
            return cls()
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")
    
    def get_preset_configs(self) -> Dict[str, 'AudioConfig']:
        """获取预设配置
        
        Returns:
            Dict[str, AudioConfig]: 预设配置字典
        """
        presets = {}
        
        # 默认预设
        presets['default'] = AudioConfig()
        
        # 激进驾驶预设
        aggressive = AudioConfig()
        aggressive.rhythm.bpm_range = (80, 200)
        aggressive.melody.steer_pitch_influence = 18
        aggressive.effects.distortion_range = (0.0, 1.0)
        aggressive.effects.effects_sensitivity = 1.5
        presets['aggressive'] = aggressive
        
        # 平静驾驶预设
        calm = AudioConfig()
        calm.rhythm.bpm_range = (50, 120)
        calm.melody.steer_pitch_influence = 6
        calm.effects.distortion_range = (0.0, 0.3)
        calm.ambience.ambient_volume = 0.5
        presets['calm'] = calm
        
        # 赛车模式预设
        racing = AudioConfig()
        racing.rhythm.bpm_range = (100, 220)
        racing.melody.throttle_sensitivity = 2.0
        racing.effects.effects_sensitivity = 2.0
        racing.ambience.enable_lap_feedback = True
        racing.ambience.best_lap_celebration = True
        presets['racing'] = racing
        
        return presets

# 默认配置实例
DEFAULT_AUDIO_CONFIG = AudioConfig()