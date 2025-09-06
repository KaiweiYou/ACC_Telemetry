#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC 遥测 -> 纯 Python 音频 MVP 增强版 (MBUX Sound Drive 风格)

受奔驰 MBUX Sound Drive 启发的分轨式交互音乐系统：
- 分轨设计：鼓点、贝斯、合成器pad、lead旋律分别独立控制
- 多维度交互：速度→整体能量，转向→合成器音高，刹车→滤波效果，G力→混响氛围
- "越开越上头"的层次递进：低速平静环境音，高速全分轨燃爆，多层次渐入渐出
"""

import math
import threading
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pygame

from acc_telemetry.core.telemetry import ACCTelemetry


@dataclass
class SineVoice:
    """简易正弦波音色发生器"""

    sound: pygame.mixer.Sound
    channel: pygame.mixer.Channel
    base_buffer: np.ndarray


class MultiLayerSynth:
    """多层次分轨合成器（MBUX Sound Drive 风格）

    提供完整的分轨音乐体验：
    - Bass: 深沉贝斯线条，随速度增强
    - Pad: 背景合成器垫子，转向时音高变化
    - Lead: 主旋律线，高转速时激活
    - FX: 氛围音效与滤波，G力和刹车驱动
    """

    def __init__(self, sample_rate: int = 44100) -> None:
        """初始化多轨合成器

        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate

        # 预生成分轨音色
        self.kick = self._make_kick()
        self.snare = self._make_snare()
        self.hat = self._make_hat()

        # 持续音轨（循环播放）
        self.bass_voice = self._create_bass_voice()
        self.pad_voice = self._create_pad_voice()
        self.lead_voice = self._create_lead_voice()
        self.ambient_voice = self._create_ambient_voice()

        # 内部状态：避免过于频繁地重采样导致点击
        self._pad_last_semitones = 0.0
        self._bass_last_semitones = 0.0

    def _to_sound(self, mono: np.ndarray) -> pygame.mixer.Sound:
        """转换单声道为立体声 Sound 对象"""
        mono = np.clip(mono, -1.0, 1.0)
        stereo = np.stack([mono, mono], axis=1)
        data = (stereo * 32767).astype(np.int16)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _make_kick(self, dur: float = 0.18) -> pygame.mixer.Sound:
        """生成深沉底鼓：双层下滑正弦"""
        t = np.linspace(0.0, dur, int(self.sample_rate * dur), endpoint=False)
        # 主体：60Hz -> 35Hz
        f1 = 60.0 * np.exp(-t * 8.0)
        wave1 = np.sin(2 * np.pi * f1 * t) * np.exp(-t * 20.0)
        # 点击感：140Hz -> 80Hz
        f2 = 140.0 * np.exp(-t * 12.0)
        wave2 = np.sin(2 * np.pi * f2 * t) * np.exp(-t * 35.0) * 0.4
        sig = wave1 + wave2
        return self._to_sound(sig.astype(np.float32))

    def _make_snare(self, dur: float = 0.15) -> pygame.mixer.Sound:
        """生成电子军鼓：噪声+音调成分"""
        n = int(self.sample_rate * dur)
        t = np.linspace(0.0, dur, n, endpoint=False)

        # 噪声成分
        noise = np.random.uniform(-1.0, 1.0, size=n)
        # 音调成分（200Hz）
        tone = np.sin(2 * np.pi * 200.0 * t) * 0.3
        # 混合与包络
        sig = (noise + tone) * np.exp(-t * 25.0)
        return self._to_sound(sig.astype(np.float32))

    def _make_hat(self, dur: float = 0.06) -> pygame.mixer.Sound:
        """生成现代踩镲：更柔和的高频质感，避免刺耳

        说明：
        - 采用带限噪声（先高通再轻度低通平滑）作为主要音色，去掉强烈的金属谐波
        - 保留快速衰减的包络，减少持续的高频残响
        - 降低整体增益，避免在高密度节拍下累积成刺耳的高频
        """
        n = int(self.sample_rate * dur)
        t = np.linspace(0.0, dur, n, endpoint=False)

        # 随机噪声作为基础
        noise = np.random.uniform(-1.0, 1.0, size=n).astype(np.float32)

        # 简单高通（去除低频成分）
        hp = np.empty_like(noise)
        hp[0] = 0.0
        hp[1:] = noise[1:] - 0.90 * noise[:-1]

        # 轻度低通平滑，驯服最尖锐的高频
        lp = np.empty_like(hp)
        lp[0] = hp[0]
        alpha = 0.25  # 越小越平滑
        for i in range(1, n):
            lp[i] = lp[i - 1] + alpha * (hp[i] - lp[i - 1])

        # 快速衰减包络，减少延音
        env = np.exp(-t * 45.0).astype(np.float32)
        sig = (lp * env * 0.45).astype(np.float32)

        return self._to_sound(sig)

    def _create_bass_voice(self, base_freq: float = 55.0) -> SineVoice:
        """创建贝斯声部：深沉持续音，可调音高和音量"""
        dur = 0.1  # 循环片段
        t = np.linspace(0.0, dur, int(self.sample_rate * dur), endpoint=False)
        # 基频 + 八度泛音
        wave = np.sin(2 * np.pi * base_freq * t) + 0.3 * np.sin(
            2 * np.pi * base_freq * 2 * t
        )
        # 轻微低通特征
        for i in range(1, len(wave)):
            wave[i] = wave[i] * 0.95 + wave[i - 1] * 0.05

        buffer = (wave * 0.4).astype(np.float32)
        stereo = np.stack([buffer, buffer], axis=1)
        data = (stereo * 32767).astype(np.int16)

        sound = pygame.mixer.Sound(buffer=data.tobytes())
        channel = pygame.mixer.find_channel(True)
        if channel:
            channel.play(sound, loops=-1)
            channel.set_volume(0.0)  # 初始静音

        return SineVoice(sound=sound, channel=channel, base_buffer=stereo)

    def _create_pad_voice(self, base_freq: float = 220.0) -> SineVoice:
        """创建合成器垫子：温暖和声，转向时变化音高"""
        dur = 0.2
        t = np.linspace(0.0, dur, int(self.sample_rate * dur), endpoint=False)
        # 和弦式复合波形
        wave = (
            0.6 * np.sin(2 * np.pi * base_freq * t)  # 根音
            + 0.4 * np.sin(2 * np.pi * base_freq * 1.25 * t)  # 大三度
            + 0.3 * np.sin(2 * np.pi * base_freq * 1.5 * t)
        )  # 完全五度

        # 软化处理
        for i in range(3, len(wave)):
            wave[i] = wave[i] * 0.7 + (wave[i - 1] + wave[i - 2] + wave[i - 3]) * 0.1

        buffer = (wave * 0.25).astype(np.float32)
        stereo = np.stack([buffer, buffer], axis=1)
        data = (stereo * 32767).astype(np.int16)

        sound = pygame.mixer.Sound(buffer=data.tobytes())
        channel = pygame.mixer.find_channel(True)
        if channel:
            channel.play(sound, loops=-1)
            channel.set_volume(0.0)

        return SineVoice(sound=sound, channel=channel, base_buffer=stereo)

    def _create_lead_voice(self, base_freq: float = 440.0) -> SineVoice:
        """创建主旋律声部：明亮lead，高转速时激活"""
        dur = 0.08
        t = np.linspace(0.0, dur, int(self.sample_rate * dur), endpoint=False)
        # 锯齿波近似（基频+泛音） - 柔化：减少高频泛音数量
        wave = np.sin(2 * np.pi * base_freq * t)
        for n in range(2, 4):  # 仅保留前两次泛音，减少高频能量
            wave += np.sin(2 * np.pi * base_freq * n * t) / n

        # 更轻微的软限幅以避免过多高频尖峰
        wave = np.tanh(wave * 1.1) * 0.6

        buffer = wave.astype(np.float32) * 0.3
        stereo = np.stack([buffer, buffer], axis=1)
        data = (stereo * 32767).astype(np.int16)

        sound = pygame.mixer.Sound(buffer=data.tobytes())
        channel = pygame.mixer.find_channel(True)
        if channel:
            channel.play(sound, loops=-1)
            channel.set_volume(0.0)

        return SineVoice(sound=sound, channel=channel, base_buffer=stereo)

    def _create_ambient_voice(self) -> SineVoice:
        """创建氛围声部：白噪声基底，G力驱动"""
        dur = 0.5
        n = int(self.sample_rate * dur)
        # 粉红噪声近似
        noise = np.random.uniform(-1.0, 1.0, size=n)
        # 简单低通（模拟粉红噪声特征）
        for i in range(1, len(noise)):
            noise[i] = noise[i] * 0.8 + noise[i - 1] * 0.2

        buffer = (noise * 0.15).astype(np.float32)
        stereo = np.stack([buffer, buffer], axis=1)
        data = (stereo * 32767).astype(np.int16)

        sound = pygame.mixer.Sound(buffer=data.tobytes())
        channel = pygame.mixer.find_channel(True)
        if channel:
            channel.play(sound, loops=-1)
            channel.set_volume(0.0)

        return SineVoice(sound=sound, channel=channel, base_buffer=stereo)

    def update_bass(self, volume: float, pitch_shift: float = 1.0) -> None:
        """更新贝斯音量和音高

        Args:
            volume: 0~1 的音量
            pitch_shift: 以半音为单位的变调值（正升负降）
        """
        if self.bass_voice.channel:
            self.bass_voice.channel.set_volume(max(0.0, min(1.0, volume)))
            # 根据半音阈值进行重采样变调，避免频繁操作点击
            semitones = max(-24.0, min(24.0, pitch_shift))
            if abs(semitones - self._bass_last_semitones) >= 0.5:
                self._retune_loop(self.bass_voice, semitones)
                self._bass_last_semitones = semitones

    def update_pad(self, volume: float, pitch_shift: float = 1.0) -> None:
        """更新合成器垫子：音量和音高变化"""
        if self.pad_voice.channel:
            self.pad_voice.channel.set_volume(max(0.0, min(1.0, volume)))
            # 音高变化通过重采样实现（简化版）
            semitones = max(-12.0, min(12.0, pitch_shift))
            # 仅当变化超过 0.5 半音时才重采样，降低咔哒声风险
            if abs(semitones - self._pad_last_semitones) >= 0.5:
                self._retune_loop(self.pad_voice, semitones)
                self._pad_last_semitones = semitones

    def update_lead(self, volume: float, pitch_shift: float = 1.0) -> None:
        """更新主旋律音量"""
        if self.lead_voice.channel:
            self.lead_voice.channel.set_volume(max(0.0, min(1.0, volume)))

    def update_ambient(self, volume: float) -> None:
        """更新氛围音量"""
        if self.ambient_voice.channel:
            self.ambient_voice.channel.set_volume(max(0.0, min(1.0, volume)))

    def _retune_loop(self, voice: SineVoice, semitones: float) -> None:
        """对循环持续音进行半音级重采样变调

        Args:
            voice: 需要变调的持续音轨（包含原始立体声循环缓冲）
            semitones: 目标变调量（正值升高，负值降低），单位：半音
        注意：
            - 使用线性插值重采样，保证实时性与稳定性
            - 控制重采样比率范围，防止极端比率造成长度为 0 或音质异常
        """
        # 计算重采样比率：>1 升调、<1 降调
        ratio = float(2.0 ** (max(-24.0, min(24.0, semitones)) / 12.0))
        base = voice.base_buffer  # shape: (N, 2) stereo float32/float
        if base is None or base.shape[0] < 4:
            return

        n = base.shape[0]
        # 约束比率，避免极端导致输出长度过短或过长
        ratio = max(0.125, min(8.0, ratio))
        n_out = max(8, int(n / ratio))

        # 构建采样位置，并进行线性插值（逐通道）
        pos = (np.arange(n_out, dtype=np.float32) * ratio).astype(np.float32)
        max_pos = float(n - 2) - 1e-6  # 保障 idx+1 不越界
        pos = np.clip(pos, 0.0, max_pos)
        idx = pos.astype(np.int32)
        frac = pos - idx

        left = base[idx, 0] * (1.0 - frac) + base[idx + 1, 0] * frac
        right = base[idx, 1] * (1.0 - frac) + base[idx + 1, 1] * frac
        stereo = np.stack([left, right], axis=1).astype(np.float32)

        # 转换为 pygame Sound 并无缝替换播放
        data = (np.clip(stereo, -1.0, 1.0) * 32767).astype(np.int16)
        new_sound = pygame.mixer.Sound(buffer=data.tobytes())

        prev_vol = 0.0
        if voice.channel:
            try:
                prev_vol = voice.channel.get_volume()
            except Exception:
                prev_vol = 0.0
            voice.channel.stop()
            voice.channel.play(new_sound, loops=-1)
            voice.channel.set_volume(prev_vol)

        voice.sound = new_sound

    def play_kick(self, vol: float = 0.8) -> None:
        """播放底鼓"""
        ch = self.kick.play()
        if ch:
            ch.set_volume(max(0.0, min(1.0, vol)))

    def play_snare(self, vol: float = 0.7) -> None:
        """播放军鼓"""
        ch = self.snare.play()
        if ch:
            ch.set_volume(max(0.0, min(1.0, vol)))

    def play_hat(self, vol: float = 0.5) -> None:
        """播放踩镲"""
        ch = self.hat.play()
        if ch:
            ch.set_volume(max(0.0, min(1.0, vol)))


class MusicTemplate808:
    """808 鼓 + 合成器 Bass + Pad 的三轨音乐模板

    模板目标：
    - 固化“流行电子化”的和声与节奏语汇（更有音乐性）
    - 用简单的参数（速度/能量/油门/刹车/转向）驱动曲式与层次推进
    - 保持低延迟与稳定性，适合实时驾驶互动

    三大分轨：
    - Drums（808风格）：Kick / Snare / Hat
    - Bass（合成器）：根音随和弦变化
    - Pad（合成器）：和声垫，随和弦变化并受转向微调
    """

    def __init__(
        self, synth: MultiLayerSynth, sample_rate: int = 48000, base_key_midi: int = 57
    ) -> None:
        """初始化模板

        Args:
            synth: 多轨合成器实例
            sample_rate: 采样率（用于节拍调度推算）
            base_key_midi: 调式根音（默认 A3=57，A 小调，自然小调）
        """
        self.synth = synth
        self.sample_rate = sample_rate
        self.base_key_midi = base_key_midi  # A3 作为根音

        # 和弦走向（A 小调常见 4-chord：Am - F - C - G）
        # 相对 A（根音=0半音）的根音偏移：Am(0), F(-4), C(+3), G(+10)
        self.chord_roots_semi = [0.0, -4.0, 3.0, 10.0]
        self.chord_index = 0

        # 拍速与调度
        self.beat_index = 0
        self.next_beat_time = time.time() + 0.2
        self.next_hat_time = self.next_beat_time + 0.25

        # 内部平滑，以免音量跳变
        self._bass_vol_s = 0.0
        self._pad_vol_s = 0.0

        # 控制项：可快速关闭/启用踩镲（用于排查或口味偏好）
        self.enable_hat: bool = False

    def _midi_to_semitones_from_a(self, midi_note: int) -> float:
        """将任意 MIDI 音高转换为相对 A 的半音位移"""
        return float(midi_note - 69)

    def _root_for_current_chord(self) -> float:
        """获取当前小节的和弦根音相对 A 的半音偏移"""
        return float(
            self.chord_roots_semi[self.chord_index % len(self.chord_roots_semi)]
        )

    def _compute_bpm_and_intervals(self, energy: float) -> tuple[float, float]:
        """根据能量计算 BPM 及其对应的单拍时长

        - 低能量：70 BPM 左右
        - 高能量：最高 150 BPM 左右
        Returns:
            (bpm, beat_interval)
        """
        bpm = 70.0 + energy * 80.0
        beat_interval = 60.0 / bpm
        return bpm, beat_interval

    def update(
        self,
        now: float,
        energy: float,
        speed: float,
        throttle: float,
        brake: float,
        steer: float,
        rpm: float,
    ) -> None:
        """每帧调用：驱动三轨音乐的节拍、和声与动态

        Args:
            now: 当前时间戳
            energy: 0~1 的整体能量
            speed: 车速（km/h）
            throttle: 油门 0~1
            brake: 刹车 0~1
            steer: 转向角度（度）
            rpm: 发动机转速
        """
        # 1) 计算 BPM 与时间间隔
        bpm, beat_interval = self._compute_bpm_and_intervals(energy)

        # 2) 节拍调度：整拍用于 Kick/Snare 与小节推进
        while now >= self.next_beat_time:
            beat = self.beat_index % 4

            # 小节开始：推进和弦
            if beat == 0:
                self.chord_index = (self.chord_index + 1) % len(self.chord_roots_semi)

            # 808 Kick：拍 1 与 3 为主，高能量时加拍 2 的补拍
            if beat in (0, 2):
                kvol = 0.55 + 0.35 * energy + 0.25 * throttle
                self.synth.play_kick(min(1.0, kvol))
            if energy > 0.72 and beat == 1:
                self.synth.play_kick(0.45)

            # 808 Snare：拍 2 与 4，刹车时更突出
            if beat in (1, 3):
                svol = 0.45 + 0.25 * energy + 0.35 * brake
                self.synth.play_snare(min(1.0, svol))

            self.beat_index += 1
            self.next_beat_time += beat_interval

        # 3) Hat：密度随能量变化（>0.6 十六分音符，否则八分音符）
        hat_interval = beat_interval * (0.25 if energy > 0.6 else 0.5)
        while now >= self.next_hat_time:
            hvol = 0.30 + 0.40 * energy + 0.20 * throttle
            if energy > 0.2 and self.enable_hat:
                self.synth.play_hat(min(1.0, hvol))
            self.next_hat_time += hat_interval

        # 4) 和声与音量：Pad/Bass 随和弦与能量推进
        root_semi = self._root_for_current_chord()

        # Pad：体积随能量，音高=根音+转向微调（±12 半音 -> 这里缩小到 ±4 半音以保持和声稳定）
        steer_shift = max(-4.0, min(4.0, steer / 540.0 * 12.0))
        pad_semi = root_semi + steer_shift
        pad_target_vol = max(0.0, (energy - 0.15) * 1.1) * 0.6
        self._pad_vol_s += (pad_target_vol - self._pad_vol_s) * 0.2
        self.synth.update_pad(self._pad_vol_s, pad_semi)

        # Bass：体积更受速度/能量影响，音高=根音的低八度（下移 12 半音）
        bass_semi = root_semi - 12.0
        bass_target_vol = energy * 0.65 + throttle * 0.35
        self._bass_vol_s += (bass_target_vol - self._bass_vol_s) * 0.2
        self.synth.update_bass(self._bass_vol_s, bass_semi)

        # Lead：通常静音，避免高频干扰（只在换挡等特殊事件时临时激活）
        # 可选：极高能量时启用微弱 Lead（>0.85 且速度 >200km/h）
        if energy > 0.85 and speed > 200.0:
            lead_vol = (energy - 0.85) * 0.4  # 最高 0.06 音量，很微弱
            self.synth.update_lead(lead_vol)
        else:
            self.synth.update_lead(0.0)  # 默认静音

    def _handle_gear_change(self, new_gear: int, prev_gear: int) -> None:
        """换挡时的特殊音效：升档兴奋、降档紧张

        Args:
            new_gear: 当前档位
            prev_gear: 之前档位
        """
        if prev_gear == 0 or new_gear == 0:
            return

        if new_gear > prev_gear:
            # 升档：明亮提示 + 临时抬高 lead（音量下调以避免刺耳）
            self.synth.play_hat(0.5)
            if self.synth.lead_voice.channel:
                cur = self.synth.lead_voice.channel.get_volume()
                self.synth.update_lead(min(0.3, cur + 0.15))
        else:
            # 降档：低沉提示 + 临时抬高 bass
            self.synth.play_kick(0.75)
            if self.synth.bass_voice.channel:
                cur = self.synth.bass_voice.channel.get_volume()
                self.synth.update_bass(min(0.8, cur + 0.15))

    def run(self) -> None:
        """主循环：MBUX Sound Drive 风格的多维度音乐交互（三轨模板版）"""
        print("[MBUX Audio] 开始运行，体验分轨式驾驶音乐（Ctrl+C 结束）…")
        prev_print = time.time()

        try:
            while True:
                data = self.telemetry.get_telemetry()
                if data is None:
                    time.sleep(0.5)
                    continue

                # 平滑更新所有参数
                self.s_speed += (data.speed - self.s_speed) * 0.15
                self.s_rpm += (data.rpm - self.s_rpm) * 0.12
                self.s_steer += (data.steer_angle - self.s_steer) * 0.2
                self.s_throttle += (data.throttle - self.s_throttle) * 0.2
                self.s_brake += (data.brake - self.s_brake) * 0.25

                # G力平滑（如果有的话）
                if hasattr(data, "g_force_lateral"):
                    self.s_g_force_lat += (
                        data.g_force_lateral - self.s_g_force_lat
                    ) * 0.15
                if hasattr(data, "g_force_longitudinal"):
                    self.s_g_force_lon += (
                        data.g_force_longitudinal - self.s_g_force_lon
                    ) * 0.15

                # 计算整体能量等级（已扩展至 300km/h 上限）
                self.energy_level = self._calculate_energy_level(
                    self.s_speed, self.s_rpm
                )

                # 使用三轨音乐模板驱动编排与参数（核心调用）
                now = time.time()
                self.template.update(
                    now=now,
                    energy=self.energy_level,
                    speed=self.s_speed,
                    throttle=self.s_throttle,
                    brake=self.s_brake,
                    steer=self.s_steer,
                    rpm=self.s_rpm,
                )

                # 换挡事件检测（保留原有特效）
                if data.gear != self.prev_gear:
                    self._handle_gear_change(data.gear, self.prev_gear)
                    self.prev_gear = data.gear

                # 周期性状态打印
                if now - prev_print > 2.0:
                    print(
                        f"能量 {self.energy_level:.2f} | 速度 {self.s_speed:5.1f} | 转向 {self.s_steer:5.1f}° | 油门 {self.s_throttle:.2f} | 刹车 {self.s_brake:.2f}"
                    )
                    prev_print = now

                time.sleep(self.sleep_time)

        except KeyboardInterrupt:
            print("\n[MBUX Audio] 停止多轨音乐系统")
        finally:
            pygame.mixer.stop()
            pygame.quit()


class PythonAudioBridge:
    """MBUX Sound Drive 风格的分轨式音频桥接器（三轨 808 模板驱动）

    功能概述：
    - 集成 MusicTemplate808（三轨：808 鼓 / 合成器 Bass / Pad）
    - 接入 ACC 遥测数据，将速度、油门、刹车、转向、转速映射为音乐参数
    - 低延迟实时渲染，具备节拍调度、和声推进与动态能量管理
    """

    def __init__(
        self, sample_rate: int = 48000, buffer_ms: int = 80, update_rate: int = 30
    ) -> None:
        """构造函数

        Args:
            sample_rate: 采样率（Hz）
            buffer_ms: 音频缓冲（毫秒）
            update_rate: 主循环更新频率（Hz）
        """
        self.sample_rate = sample_rate
        self.update_rate = update_rate
        self.sleep_time = 1.0 / max(1, update_rate)

        # 初始化 pygame 音频
        pygame.mixer.pre_init(
            frequency=sample_rate,
            size=-16,
            channels=2,
            buffer=int(sample_rate * buffer_ms / 1000),
        )
        pygame.init()

        # 多轨合成器 + 三轨音乐模板
        self.synth = MultiLayerSynth(sample_rate=self.sample_rate)
        self.template = MusicTemplate808(self.synth, sample_rate=self.sample_rate)

        # ACC 遥测
        self.telemetry = ACCTelemetry()

        # 平滑状态
        self.s_speed = 0.0
        self.s_rpm = 0.0
        self.s_steer = 0.0
        self.s_throttle = 0.0
        self.s_brake = 0.0
        self.s_g_force_lat = 0.0
        self.s_g_force_lon = 0.0

        # 其它状态
        self.prev_gear = 0
        self.energy_level = 0.0

        print(
            f"[MBUX Audio] 启动三轨模板：sr={sample_rate}, buf~{buffer_ms}ms, rate={update_rate}Hz"
        )

    def _calculate_energy_level(self, speed: float, rpm: float) -> float:
        """计算整体能量等级 (0-1)

        规则说明：
        - 速度映射至 300km/h 上限，采用 0.9 次幂以增强中高段可感提升
        - 速度权重 0.7、转速权重 0.3，适配 GT 赛事高速巡航特性
        """
        spd_norm = max(0.0, min(1.0, speed / 300.0))
        spd_curve = spd_norm**0.9
        speed_factor = 0.7 * spd_curve

        rpm_norm = max(0.0, min(1.0, rpm / 8000.0))
        rpm_factor = 0.3 * rpm_norm

        return min(1.0, speed_factor + rpm_factor)

    def _handle_gear_change(self, new_gear: int, prev_gear: int) -> None:
        """换挡时的特殊音效：升档兴奋、降档紧张

        Args:
            new_gear: 当前档位
            prev_gear: 之前档位
        """
        if prev_gear == 0 or new_gear == 0:
            return

        if new_gear > prev_gear:
            # 升档：明亮提示 + 临时抬高 lead
            self.synth.play_hat(0.8)
            if self.synth.lead_voice.channel:
                cur = self.synth.lead_voice.channel.get_volume()
                self.synth.update_lead(min(1.0, cur + 0.3))
        else:
            # 降档：低沉提示 + 临时抬高 bass
            self.synth.play_kick(0.9)
            if self.synth.bass_voice.channel:
                cur = self.synth.bass_voice.channel.get_volume()
                self.synth.update_bass(min(1.0, cur + 0.2))

    def run(self) -> None:
        """主循环：采集遥测并驱动 MusicTemplate808 进行实时编排"""
        print("[MBUX Audio] 开始运行，体验三轨 808 模板（Ctrl+C 结束）…")
        prev_print = time.time()

        try:
            while True:
                data = self.telemetry.get_telemetry()
                if data is None:
                    time.sleep(0.5)
                    continue

                # 平滑更新
                self.s_speed += (data.speed - self.s_speed) * 0.15
                self.s_rpm += (data.rpm - self.s_rpm) * 0.12
                self.s_steer += (data.steer_angle - self.s_steer) * 0.2
                self.s_throttle += (data.throttle - self.s_throttle) * 0.2
                self.s_brake += (data.brake - self.s_brake) * 0.25

                if hasattr(data, "g_force_lateral"):
                    self.s_g_force_lat += (
                        data.g_force_lateral - self.s_g_force_lat
                    ) * 0.15
                if hasattr(data, "g_force_longitudinal"):
                    self.s_g_force_lon += (
                        data.g_force_longitudinal - self.s_g_force_lon
                    ) * 0.15

                # 能量等级
                self.energy_level = self._calculate_energy_level(
                    self.s_speed, self.s_rpm
                )

                # 三轨模板驱动
                now = time.time()
                self.template.update(
                    now=now,
                    energy=self.energy_level,
                    speed=self.s_speed,
                    throttle=self.s_throttle,
                    brake=self.s_brake,
                    steer=self.s_steer,
                    rpm=self.s_rpm,
                )

                # 换挡特效
                if data.gear != self.prev_gear:
                    self._handle_gear_change(data.gear, self.prev_gear)
                    self.prev_gear = data.gear

                # 打印状态
                if now - prev_print > 2.0:
                    print(
                        f"能量 {self.energy_level:.2f} | 速度 {self.s_speed:5.1f} | 转向 {self.s_steer:5.1f}° | 油门 {self.s_throttle:.2f} | 刹车 {self.s_brake:.2f}"
                    )
                    prev_print = now

                time.sleep(self.sleep_time)

        except KeyboardInterrupt:
            print("\n[MBUX Audio] 停止三轨音乐系统")
        finally:
            pygame.mixer.stop()
            pygame.quit()


def main():
    """入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description="ACC -> MBUX Sound Drive 风格多轨音乐")
    parser.add_argument("--sr", type=int, default=48000, help="采样率")
    parser.add_argument("--buf", type=int, default=80, help="缓冲毫秒数")
    parser.add_argument("--rate", type=int, default=30, help="更新频率 Hz")

    args = parser.parse_args()

    bridge = PythonAudioBridge(
        sample_rate=args.sr, buffer_ms=args.buf, update_rate=args.rate
    )
    bridge.run()


if __name__ == "__main__":
    main()
