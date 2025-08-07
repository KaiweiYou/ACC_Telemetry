#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC交互音乐引擎

这个模块负责实际的音频生成和播放功能。
基于音乐参数生成实时音频，包括节奏、旋律、音效等多个层次的音乐元素。
使用纯Python实现，无需外部音频库依赖。

作者: Assistant
日期: 2024
"""

import math
import time
import threading
import queue
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import json

try:
    import pygame
    import numpy as np
    PYGAME_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError as e:
    PYGAME_AVAILABLE = False
    NUMPY_AVAILABLE = False
    print(f"警告: 音频依赖未安装 ({e})，音频播放功能将受限")

from .music_mapper import MusicParameters
from .audio_config import AudioConfig

@dataclass
class AudioSample:
    """音频样本数据类"""
    data: List[float]
    sample_rate: int = 44100
    channels: int = 2
    duration: float = 0.0
    
    def __post_init__(self):
        if self.duration == 0.0:
            self.duration = len(self.data) / (self.sample_rate * self.channels)

class SynthEngine:
    """合成器引擎
    
    负责生成基础音频波形和音效
    """
    
    def __init__(self, sample_rate: int = 44100):
        """初始化合成器引擎
        
        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate
        self.phase = 0.0
        
        # 预生成的波形表
        self.wave_tables = self._generate_wave_tables()
        
        # 音效缓存
        self.effect_cache: Dict[str, AudioSample] = {}
        
        # 生成基础音效
        self._generate_base_effects()
    
    def _generate_wave_tables(self, table_size: int = 1024) -> Dict[str, List[float]]:
        """生成波形表
        
        Args:
            table_size: 波形表大小
            
        Returns:
            Dict[str, List[float]]: 波形表字典
        """
        tables = {}
        
        # 正弦波
        tables['sine'] = [math.sin(2 * math.pi * i / table_size) for i in range(table_size)]
        
        # 方波
        tables['square'] = [1.0 if i < table_size // 2 else -1.0 for i in range(table_size)]
        
        # 锯齿波
        tables['sawtooth'] = [2.0 * i / table_size - 1.0 for i in range(table_size)]
        
        # 三角波
        tables['triangle'] = [
            4.0 * i / table_size - 1.0 if i < table_size // 2 
            else 3.0 - 4.0 * i / table_size 
            for i in range(table_size)
        ]
        
        # 噪声（白噪声近似）
        import random
        tables['noise'] = [random.uniform(-1.0, 1.0) for _ in range(table_size)]
        
        return tables
    
    def _generate_base_effects(self) -> None:
        """生成基础音效样本"""
        # 鼓点音效
        self.effect_cache['kick'] = self._generate_kick_drum()
        self.effect_cache['snare'] = self._generate_snare_drum()
        self.effect_cache['hihat'] = self._generate_hihat()
        
        # 特殊音效
        self.effect_cache['turbo'] = self._generate_turbo_sound()
        self.effect_cache['drs'] = self._generate_drs_sound()
        self.effect_cache['warning'] = self._generate_warning_sound()
        self.effect_cache['celebration'] = self._generate_celebration_sound()
    
    def generate_tone(self, frequency: float, duration: float, 
                     wave_type: str = 'sine', amplitude: float = 0.5) -> AudioSample:
        """生成音调
        
        Args:
            frequency: 频率 (Hz)
            duration: 持续时间 (秒)
            wave_type: 波形类型
            amplitude: 振幅
            
        Returns:
            AudioSample: 音频样本
        """
        num_samples = int(self.sample_rate * duration)
        wave_table = self.wave_tables.get(wave_type, self.wave_tables['sine'])
        table_size = len(wave_table)
        
        data = []
        phase_increment = frequency * table_size / self.sample_rate
        
        for i in range(num_samples):
            # 立体声
            sample_value = wave_table[int(self.phase) % table_size] * amplitude
            data.extend([sample_value, sample_value])  # L, R
            self.phase += phase_increment
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def _generate_kick_drum(self, duration: float = 0.2) -> AudioSample:
        """生成底鼓音效
        
        Args:
            duration: 持续时间
            
        Returns:
            AudioSample: 底鼓音频样本
        """
        num_samples = int(self.sample_rate * duration)
        data = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            # 低频正弦波 + 噪声 + 包络
            envelope = math.exp(-t * 15)  # 快速衰减
            tone = math.sin(2 * math.pi * 60 * t) * 0.8  # 60Hz基频
            click = math.sin(2 * math.pi * 2000 * t) * math.exp(-t * 50) * 0.3  # 点击声
            
            sample = (tone + click) * envelope * 0.7
            data.extend([sample, sample])
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def _generate_snare_drum(self, duration: float = 0.15) -> AudioSample:
        """生成军鼓音效
        
        Args:
            duration: 持续时间
            
        Returns:
            AudioSample: 军鼓音频样本
        """
        num_samples = int(self.sample_rate * duration)
        data = []
        
        import random
        for i in range(num_samples):
            t = i / self.sample_rate
            envelope = math.exp(-t * 8)
            
            # 噪声 + 音调成分
            noise = random.uniform(-1.0, 1.0) * 0.6
            tone = math.sin(2 * math.pi * 200 * t) * 0.4
            
            sample = (noise + tone) * envelope * 0.5
            data.extend([sample, sample])
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def _generate_hihat(self, duration: float = 0.1) -> AudioSample:
        """生成踩镲音效
        
        Args:
            duration: 持续时间
            
        Returns:
            AudioSample: 踩镲音频样本
        """
        num_samples = int(self.sample_rate * duration)
        data = []
        
        import random
        for i in range(num_samples):
            t = i / self.sample_rate
            envelope = math.exp(-t * 20)  # 快速衰减
            
            # 高频噪声
            sample = random.uniform(-1.0, 1.0) * envelope * 0.3
            data.extend([sample, sample])
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def _generate_turbo_sound(self, duration: float = 0.5) -> AudioSample:
        """生成涡轮增压音效
        
        Args:
            duration: 持续时间
            
        Returns:
            AudioSample: 涡轮音效样本
        """
        num_samples = int(self.sample_rate * duration)
        data = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            # 频率上升的哨声效果
            freq = 800 + t * 1200  # 从800Hz上升到2000Hz
            envelope = math.sin(math.pi * t / duration)  # 钟形包络
            
            sample = math.sin(2 * math.pi * freq * t) * envelope * 0.4
            data.extend([sample, sample])
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def _generate_drs_sound(self, duration: float = 0.3) -> AudioSample:
        """生成DRS音效
        
        Args:
            duration: 持续时间
            
        Returns:
            AudioSample: DRS音效样本
        """
        num_samples = int(self.sample_rate * duration)
        data = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            # 机械开启声效
            envelope = math.exp(-t * 3)
            click = math.sin(2 * math.pi * 1500 * t) * math.exp(-t * 10)
            whoosh = math.sin(2 * math.pi * 300 * t) * envelope
            
            sample = (click * 0.3 + whoosh * 0.5) * 0.6
            data.extend([sample, sample])
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def _generate_warning_sound(self, duration: float = 0.2) -> AudioSample:
        """生成警告音效
        
        Args:
            duration: 持续时间
            
        Returns:
            AudioSample: 警告音效样本
        """
        num_samples = int(self.sample_rate * duration)
        data = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            # 双音调警告声
            freq1 = 800
            freq2 = 1000
            switch_time = duration / 4
            
            if (t % (switch_time * 2)) < switch_time:
                freq = freq1
            else:
                freq = freq2
            
            envelope = 0.8
            sample = math.sin(2 * math.pi * freq * t) * envelope * 0.5
            data.extend([sample, sample])
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def _generate_celebration_sound(self, duration: float = 1.0) -> AudioSample:
        """生成庆祝音效
        
        Args:
            duration: 持续时间
            
        Returns:
            AudioSample: 庆祝音效样本
        """
        num_samples = int(self.sample_rate * duration)
        data = []
        
        # 上升音阶
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C大调音阶
        
        for i in range(num_samples):
            t = i / self.sample_rate
            note_duration = duration / len(notes)
            note_index = min(int(t / note_duration), len(notes) - 1)
            
            freq = notes[note_index]
            envelope = math.sin(math.pi * (t % note_duration) / note_duration)
            
            sample = math.sin(2 * math.pi * freq * t) * envelope * 0.6
            data.extend([sample, sample])
        
        return AudioSample(data, self.sample_rate, 2, duration)
    
    def apply_effects(self, sample: AudioSample, params: MusicParameters) -> AudioSample:
        """应用音效处理
        
        Args:
            sample: 输入音频样本
            params: 音乐参数
            
        Returns:
            AudioSample: 处理后的音频样本
        """
        data = sample.data.copy()
        
        # 应用立体声平移
        data = self._apply_pan(data, params.pan)
        
        # 应用失真
        if params.distortion > 0:
            data = self._apply_distortion(data, params.distortion)
        
        # 应用滤波器
        data = self._apply_filter(data, params.filter_freq, params.filter_resonance)
        
        # 应用音量
        data = [sample_val * params.volume for sample_val in data]
        
        return AudioSample(data, sample.sample_rate, sample.channels, sample.duration)
    
    def _apply_pan(self, data: List[float], pan: float) -> List[float]:
        """应用立体声平移
        
        Args:
            data: 音频数据 (交错立体声)
            pan: 平移值 (-1.0 到 1.0)
            
        Returns:
            List[float]: 处理后的音频数据
        """
        result = []
        left_gain = math.sqrt((1.0 - pan) / 2.0)
        right_gain = math.sqrt((1.0 + pan) / 2.0)
        
        for i in range(0, len(data), 2):
            left = data[i] * left_gain
            right = data[i + 1] * right_gain
            result.extend([left, right])
        
        return result
    
    def _apply_distortion(self, data: List[float], amount: float) -> List[float]:
        """应用失真效果
        
        Args:
            data: 音频数据
            amount: 失真强度 (0.0 到 1.0)
            
        Returns:
            List[float]: 处理后的音频数据
        """
        drive = 1.0 + amount * 10.0
        return [math.tanh(sample * drive) / drive for sample in data]
    
    def _apply_filter(self, data: List[float], cutoff: float, resonance: float) -> List[float]:
        """应用低通滤波器
        
        Args:
            data: 音频数据
            cutoff: 截止频率 (Hz)
            resonance: 共振强度
            
        Returns:
            List[float]: 处理后的音频数据
        """
        # 简单的一阶低通滤波器
        if cutoff >= self.sample_rate / 2:
            return data
        
        rc = 1.0 / (2 * math.pi * cutoff)
        dt = 1.0 / self.sample_rate
        alpha = dt / (rc + dt)
        
        result = []
        prev_left = 0.0
        prev_right = 0.0
        
        for i in range(0, len(data), 2):
            # 左声道
            filtered_left = prev_left + alpha * (data[i] - prev_left)
            prev_left = filtered_left
            
            # 右声道
            filtered_right = prev_right + alpha * (data[i + 1] - prev_right)
            prev_right = filtered_right
            
            result.extend([filtered_left, filtered_right])
        
        return result

class MusicEngine:
    """音乐引擎主类
    
    负责协调音频生成、播放和管理
    """
    
    def __init__(self, config: AudioConfig):
        """初始化音乐引擎
        
        Args:
            config: 音频配置
        """
        self.config = config
        self.synth = SynthEngine(config.sample_rate)
        
        # 播放状态
        self.is_playing = False
        self.is_initialized = False
        
        # 音频队列和线程
        self.audio_queue = queue.Queue(maxsize=10)
        self.playback_thread: Optional[threading.Thread] = None
        
        # 节拍器
        self.beat_timer = 0.0
        self.last_beat_time = 0.0
        
        # 当前参数
        self.current_params: Optional[MusicParameters] = None
        
        # 回调函数
        self.on_beat_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        # 初始化音频系统
        self._initialize_audio()
    
    def _initialize_audio(self) -> bool:
        """初始化音频系统
        
        Returns:
            bool: 初始化是否成功
        """
        if not PYGAME_AVAILABLE:
            print("警告: pygame不可用，使用模拟音频模式")
            self.is_initialized = True
            return True
        
        try:
            pygame.mixer.pre_init(
                frequency=self.config.sample_rate,
                size=-16,
                channels=2,
                buffer=self.config.buffer_size
            )
            pygame.mixer.init()
            self.is_initialized = True
            print(f"音频系统初始化成功: {self.config.sample_rate}Hz, 缓冲区: {self.config.buffer_size}")
            return True
        except Exception as e:
            print(f"音频系统初始化失败: {e}")
            if self.on_error_callback:
                self.on_error_callback(f"音频初始化失败: {e}")
            return False
    
    def start(self) -> bool:
        """启动音乐引擎
        
        Returns:
            bool: 启动是否成功
        """
        if not self.is_initialized:
            return False
        
        if self.is_playing:
            return True
        
        self.is_playing = True
        self.beat_timer = 0.0
        self.last_beat_time = time.time()
        
        # 启动播放线程
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()
        
        print("音乐引擎已启动")
        return True
    
    def stop(self) -> None:
        """停止音乐引擎"""
        self.is_playing = False
        
        if PYGAME_AVAILABLE:
            pygame.mixer.stop()
        
        # 清空队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        print("音乐引擎已停止")
    
    def update_parameters(self, params: MusicParameters) -> None:
        """更新音乐参数
        
        Args:
            params: 新的音乐参数
        """
        if self.current_params is None:
            print(f"[音乐引擎] 首次接收参数: BPM={params.bpm:.1f}, 音量={params.volume:.2f}, 音调={params.base_pitch}")
        
        self.current_params = params
        
        # 检查是否需要触发特殊音效
        self._handle_special_effects(params)
    
    def _playback_loop(self) -> None:
        """播放循环线程"""
        print("[音乐引擎] 播放循环已启动")
        beat_count = 0
        
        while self.is_playing:
            try:
                current_time = time.time()
                
                if self.current_params is None:
                    time.sleep(0.01)
                    continue
                
                # 计算节拍时间
                beat_interval = 60.0 / self.current_params.bpm
                
                if current_time - self.last_beat_time >= beat_interval:
                    self._generate_beat()
                    self.last_beat_time = current_time
                    beat_count += 1
                    
                    # 每10个节拍打印一次状态
                    if beat_count % 10 == 0:
                        print(f"[音乐引擎] 节拍: {beat_count}, BPM: {self.current_params.bpm:.1f}, 音量: {self.current_params.volume:.2f}")
                    
                    if self.on_beat_callback:
                        self.on_beat_callback(self.current_params)
                
                # 生成旋律音符（降低频率以避免过多音符）
                if self.config.enable_melody and beat_count % 4 == 0:  # 每4个节拍生成一个旋律音符
                    self._generate_melody_note()
                
                time.sleep(0.01)  # 避免过度占用CPU
                
            except Exception as e:
                print(f"播放循环错误: {e}")
                if self.on_error_callback:
                    self.on_error_callback(f"播放错误: {e}")
                time.sleep(0.1)
        
        print("[音乐引擎] 播放循环已停止")
    
    def _generate_beat(self) -> None:
        """生成节拍"""
        if not self.current_params or not self.config.enable_rhythm:
            return
        
        # 根据节拍模式选择音效
        beat_pattern = self.current_params.beat_pattern
        
        # 如果指定的节拍模式不存在，使用默认的kick
        if beat_pattern not in self.synth.effect_cache:
            beat_pattern = 'kick'
        
        if beat_pattern in self.synth.effect_cache:
            sample = self.synth.effect_cache[beat_pattern]
            
            # 应用音效处理
            processed_sample = self.synth.apply_effects(sample, self.current_params)
            
            # 播放音效
            self._play_sample(processed_sample)
        else:
            # 如果没有预设音效，生成简单的节拍音
            beat_sample = self.synth.generate_tone(80, 0.1, 'sine', self.current_params.volume * 0.5)
            processed_sample = self.synth.apply_effects(beat_sample, self.current_params)
            self._play_sample(processed_sample)
    
    def _generate_melody_note(self) -> None:
        """生成旋律音符"""
        if not self.current_params or not self.config.enable_melody:
            return
        
        # 计算音符频率
        base_freq = self._midi_to_frequency(self.current_params.base_pitch)
        pitch_offset_freq = base_freq * (2 ** (self.current_params.pitch_offset / 12))
        
        # 生成音符
        note_duration = 0.2  # 音符持续时间
        sample = self.synth.generate_tone(
            pitch_offset_freq, 
            note_duration, 
            'sine', 
            self.current_params.volume * 0.3
        )
        
        # 应用音效处理
        processed_sample = self.synth.apply_effects(sample, self.current_params)
        
        # 播放音符
        self._play_sample(processed_sample)
    
    def _handle_special_effects(self, params: MusicParameters) -> None:
        """处理特殊音效触发
        
        Args:
            params: 音乐参数
        """
        if params.trigger_turbo_sound:
            self._play_effect('turbo')
        
        if params.trigger_drs_sound:
            self._play_effect('drs')
        
        if params.trigger_warning_sound:
            self._play_effect('warning')
        
        if params.trigger_celebration:
            self._play_effect('celebration')
    
    def _play_effect(self, effect_name: str) -> None:
        """播放特殊音效
        
        Args:
            effect_name: 音效名称
        """
        if effect_name in self.synth.effect_cache:
            sample = self.synth.effect_cache[effect_name]
            
            if self.current_params:
                processed_sample = self.synth.apply_effects(sample, self.current_params)
            else:
                processed_sample = sample
            
            self._play_sample(processed_sample)
    
    def _play_sample(self, sample: AudioSample) -> None:
        """播放音频样本
        
        Args:
            sample: 音频样本
        """
        if not PYGAME_AVAILABLE or not NUMPY_AVAILABLE:
            # 模拟播放（打印调试信息）
            print(f"[模拟播放] 音频样本: {len(sample.data)}个采样点, 时长: {sample.duration:.3f}秒")
            return
        
        try:
            # 将浮点数据转换为16位整数
            audio_data = np.array(sample.data, dtype=np.float32)
            audio_data = np.clip(audio_data, -1.0, 1.0)
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # 确保数据长度是偶数（立体声）
            if len(audio_data) % 2 != 0:
                audio_data = np.append(audio_data, 0)
            
            # 创建pygame Sound对象并播放
            sound = pygame.sndarray.make_sound(audio_data.reshape(-1, 2))
            sound.set_volume(0.5)  # 设置适中的音量
            sound.play()
            
            print(f"[播放] 音频样本: {len(sample.data)}个采样点, 时长: {sample.duration:.3f}秒")
            
        except Exception as e:
            print(f"播放音频样本失败: {e}")
            if self.on_error_callback:
                self.on_error_callback(f"音频播放错误: {e}")
    
    def _midi_to_frequency(self, midi_note: int) -> float:
        """将MIDI音符转换为频率
        
        Args:
            midi_note: MIDI音符号 (0-127)
            
        Returns:
            float: 频率 (Hz)
        """
        return 440.0 * (2 ** ((midi_note - 69) / 12))
    
    def set_beat_callback(self, callback: Callable) -> None:
        """设置节拍回调函数
        
        Args:
            callback: 回调函数
        """
        self.on_beat_callback = callback
    
    def set_error_callback(self, callback: Callable) -> None:
        """设置错误回调函数
        
        Args:
            callback: 回调函数
        """
        self.on_error_callback = callback
    
    def update_config(self, config: AudioConfig) -> None:
        """更新配置
        
        Args:
            config: 新的音频配置
        """
        self.config = config
        # 注意: 更改采样率需要重新初始化音频系统
    
    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            'is_playing': self.is_playing,
            'is_initialized': self.is_initialized,
            'current_bpm': self.current_params.bpm if self.current_params else 0,
            'pygame_available': PYGAME_AVAILABLE,
            'sample_rate': self.config.sample_rate,
            'buffer_size': self.config.buffer_size
        }
    
    def cleanup(self) -> None:
        """清理资源"""
        self.stop()
        
        if PYGAME_AVAILABLE:
            pygame.mixer.quit()
        
        print("音乐引擎资源已清理")