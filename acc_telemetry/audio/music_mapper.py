#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块: music_mapper

该模块定义音乐参数数据结构, 用于在应用内不同组件之间传递音乐控制参数。
这些参数可以由任意映射器(例如 MBUX 风格的驾驶-音乐映射)产生, 并由具体的音频后端消费。

设计目标:
- 与现有 MusicEngine/AudioEngine 接口解耦
- 提供足够通用的字段以承载节奏/音量/音高/空间/音色等信息
- 允许携带一次性触发的特殊事件(例如涡轮、DRS、警告、庆祝)

作者: Assistant
日期: 2024
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MusicParameters:
    """音乐参数数据类

    用于描述在某一时间点的音乐控制参数集合, 由映射器(如 MBUX 适配器)产生, 由音频引擎消费。

    字段说明:
    - bpm:             当前节拍速度, 单位 BPM
    - volume:          主存在感/主音量, 范围 0.0-1.0
    - base_pitch:      基础音高(例如根音), 使用 MIDI 数值, 常见范围 36-84
    - pan:             空间位置/声像, -1.0(左) ~ 1.0(右)
    - brightness:      音色亮度(可映射到滤波/谐波), 0.0-1.0
    - reverb_amount:   混响量(可选), 0.0-1.0
    - distortion_amount: 失真量(可选), 0.0-1.0
    - trigger_turbo_sound: 触发一次性涡轮音效
    - trigger_drs_sound:   触发一次性 DRS 音效
    - trigger_warning_sound: 触发一次性警告音效
    - trigger_celebration:   触发一次性庆祝音效
    - timestamp:       时间戳(秒), 用于时序参考
    """

    bpm: float
    volume: float
    base_pitch: int

    pan: float = 0.0
    brightness: float = 0.5
    reverb_amount: float = 0.0
    distortion_amount: float = 0.0

    trigger_turbo_sound: bool = False
    trigger_drs_sound: bool = False
    trigger_warning_sound: bool = False
    trigger_celebration: bool = False

    timestamp: Optional[float] = None

    # 预留扩展字段(不改变现有后端的前提下可被忽略)
    # 例如: sidechain_amount: float = 0.0
