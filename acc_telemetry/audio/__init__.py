#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC遥测交互音乐模块

这个模块提供将ACC遥测数据转换为实时交互音乐的功能。
通过分析车辆的各种传感器数据，生成对应的音乐元素，
为驾驶体验增添音乐化的维度。

主要功能：
- 遥测数据到音乐参数的映射
- 实时音乐生成和播放
- 音乐配置和个性化设置
- MBUX Sound Drive 风格的驾驶音乐体验
- 音乐可视化界面

作者: Assistant
日期: 2024
"""

from .audio_config import AudioConfig
from .mbux_controller import MBUXSoundDriveController, MusicalExpressionEngine
from .music_engine import AudioEngine, MockAudioEngine, MusicEngine
from .music_mapper import MusicParameters

__all__ = [
    "MusicEngine",
    "AudioEngine",
    "MockAudioEngine",
    "AudioConfig",
    "MusicParameters",
    "MBUXSoundDriveController",
    "MusicalExpressionEngine",
]

__version__ = "1.0.0"
