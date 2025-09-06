#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC交互音乐引擎

这个模块定义了音乐引擎的抽象接口。
具体的音频后端实现（如SuperCollider）将继承这些接口。
原有的Pygame实现已被移除，为专业音频后端让路。

作者: Assistant
日期: 2024
"""

import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from .audio_config import AudioConfig
from .music_mapper import MusicParameters


class AudioEngine(ABC):
    """
    音频引擎抽象基类

    定义了所有音频后端必须实现的接口。
    这确保了不同音频后端之间的兼容性。
    """

    @abstractmethod
    def __init__(self, config: AudioConfig):
        """
        初始化音频引擎

        Args:
            config: 音频配置对象
        """
        pass

    @abstractmethod
    def start(self) -> bool:
        """
        启动音频引擎

        Returns:
            bool: 启动是否成功
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        停止音频引擎
        """
        pass

    @abstractmethod
    def update_parameters(self, params: MusicParameters) -> None:
        """
        更新音乐参数

        Args:
            params: 音乐参数对象
        """
        pass

    @abstractmethod
    def set_master_volume(self, volume: float) -> None:
        """
        设置主音量

        Args:
            volume: 音量值 (0.0 到 1.0)
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        获取引擎状态

        Returns:
            Dict[str, Any]: 状态信息字典
        """
        pass

    @abstractmethod
    def pause(self) -> None:
        """
        暂停音频播放
        """
        pass

    @abstractmethod
    def resume(self) -> None:
        """
        恢复音频播放
        """
        pass

    @abstractmethod
    def is_paused(self) -> bool:
        """
        检查是否处于暂停状态

        Returns:
            bool: 是否已暂停
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        清理资源
        """
        pass


class MusicEngine(AudioEngine):
    """
    音乐引擎主类

    管理音频后端的生命周期，处理音乐参数更新，
    并提供统一的音频控制接口。
    """

    def __init__(self, config: AudioConfig):
        """
        初始化音乐引擎

        Args:
            config: 音频配置对象
        """
        self.config = config

        # 播放状态
        self.is_playing = False
        self.is_initialized = False

        # 当前参数
        self.current_params: Optional[MusicParameters] = None

        # 回调函数
        self.on_beat_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None

        # 根据配置选择音频后端
        self._audio_backend = self._create_audio_backend()

        print(f"[音乐引擎] 使用音频后端: {type(self._audio_backend).__name__}")

    def _create_audio_backend(self) -> AudioEngine:
        """
        根据配置创建音频后端

        Returns:
            AudioEngine: 音频后端实例
        """
        # 优先选择真实分轨后端
        try:
            engine_name = (self.config.audio_engine or "mock").lower()
        except Exception:
            engine_name = "mock"

        if engine_name in ("stems", "pygame", "pygame_stems"):
            try:
                return PygameStemsAudioEngine(self.config)
            except Exception as e:
                print(f"[音乐引擎] 创建 Pygame 分轨后端失败, 回退为模拟后端: {e}")

        # 默认使用模拟后端
        print("[音乐引擎] 使用模拟音频引擎")
        return MockAudioEngine(self.config)

    def start(self) -> bool:
        """
        启动音乐引擎

        Returns:
            bool: 启动是否成功
        """
        if self.is_playing:
            return True

        success = self._audio_backend.start()
        if success:
            self.is_playing = True
            self.is_initialized = True
            print("[音乐引擎] 已启动")
        else:
            print("[音乐引擎] 启动失败")

        return success

    def stop(self) -> None:
        """
        停止音乐引擎
        """
        if not self.is_playing:
            return

        self._audio_backend.stop()
        self.is_playing = False
        print("[音乐引擎] 已停止")

    def update_parameters(self, params: MusicParameters) -> None:
        """
        更新音乐参数

        Args:
            params: 音乐参数对象
        """
        if self.current_params is None:
            print(
                f"[音乐引擎] 首次接收参数: BPM={params.bpm:.1f}, 音量={params.volume:.2f}, 音调={params.base_pitch}"
            )

        self.current_params = params

        # 委托给音频后端
        self._audio_backend.update_parameters(params)

        # 触发回调
        if self.on_beat_callback:
            self.on_beat_callback(params)

    def set_master_volume(self, volume: float) -> None:
        """
        设置主音量

        Args:
            volume: 音量值 (0.0 到 1.0)
        """
        self._audio_backend.set_master_volume(volume)

    def set_beat_callback(self, callback: Callable) -> None:
        """
        设置节拍回调函数

        Args:
            callback: 回调函数
        """
        self.on_beat_callback = callback

    def set_error_callback(self, callback: Callable) -> None:
        """
        设置错误回调函数

        Args:
            callback: 错误回调函数
        """
        self.on_error_callback = callback

    def pause(self) -> None:
        """暂停播放"""
        try:
            self._audio_backend.pause()
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(e)

    def resume(self) -> None:
        """恢复播放"""
        try:
            self._audio_backend.resume()
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(e)

    def is_paused(self) -> bool:
        """是否处于暂停状态"""
        try:
            return bool(self._audio_backend.is_paused())
        except Exception:
            return False

    # ======== 新增方法：分轨控制 ========

    def set_stem_volume(self, stem: str, volume: float) -> None:
        """
        设置单个分轨音量

        Args:
            stem: 分轨名称 ('drums', 'bass', 'vocals', 'other')
            volume: 音量 (0.0-2.0，1.0为默认)
        """
        if hasattr(self._audio_backend, "set_stem_volume"):
            self._audio_backend.set_stem_volume(stem, volume)

    def set_stem_mute(self, stem: str, muted: bool) -> None:
        """
        设置分轨静音状态

        Args:
            stem: 分轨名称
            muted: 是否静音
        """
        if hasattr(self._audio_backend, "set_stem_mute"):
            self._audio_backend.set_stem_mute(stem, muted)

    def set_stem_solo(self, stem: str, solo: bool) -> None:
        """
        设置分轨独奏状态

        Args:
            stem: 分轨名称
            solo: 是否独奏
        """
        if hasattr(self._audio_backend, "set_stem_solo"):
            self._audio_backend.set_stem_solo(stem, solo)

    def fade_pause(self, duration: float = 0.2) -> None:
        """
        淡入淡出暂停

        Args:
            duration: 淡出时长（秒）
        """
        if hasattr(self._audio_backend, "fade_pause"):
            self._audio_backend.fade_pause(duration)
        else:
            self.pause()

    def fade_resume(self, duration: float = 0.2) -> None:
        """
        淡入淡出恢复

        Args:
            duration: 淡入时长（秒）
        """
        if hasattr(self._audio_backend, "fade_resume"):
            self._audio_backend.fade_resume(duration)
        else:
            self.resume()

    def update_config(self, config: AudioConfig) -> None:
        """
        更新配置

        Args:
            config: 新的音频配置
        """
        self.config = config
        # 将配置更新传递给后端
        if hasattr(self._audio_backend, "update_config"):
            self._audio_backend.update_config(config)

    def get_status(self) -> Dict[str, Any]:
        """
        获取引擎状态

        Returns:
            Dict[str, Any]: 状态信息字典
        """
        backend_status = self._audio_backend.get_status()

        return {
            "is_playing": self.is_playing,
            "is_initialized": self.is_initialized,
            "is_paused": self.is_paused(),
            "current_bpm": self.current_params.bpm if self.current_params else 0,
            "backend_type": type(self._audio_backend).__name__,
            "backend_status": backend_status,
        }

    def cleanup(self) -> None:
        """
        清理资源
        """
        self.stop()
        self._audio_backend.cleanup()
        print("[音乐引擎] 资源已清理")


class MockAudioEngine(AudioEngine):
    """
    模拟音频引擎

    用于在没有实际音频后端时提供基本功能。
    主要用于开发和测试目的。
    """

    def __init__(self, config: AudioConfig):
        """
        初始化模拟音频引擎

        Args:
            config: 音频配置对象
        """
        self.config = config
        self.is_running = False
        self.master_volume = 1.0
        self.current_params: Optional[MusicParameters] = None

        # 模拟播放线程
        self.playback_thread: Optional[threading.Thread] = None
        self.beat_count = 0

        # 暂停状态
        self._paused = False

        print("[模拟音频引擎] 已初始化")

    def start(self) -> bool:
        """
        启动模拟音频引擎

        Returns:
            bool: 始终返回True
        """
        if self.is_running:
            return True

        self.is_running = True
        self.beat_count = 0

        # 启动模拟播放线程
        self.playback_thread = threading.Thread(
            target=self._mock_playback_loop, daemon=True
        )
        self.playback_thread.start()

        print("[模拟音频引擎] 已启动")
        return True

    def stop(self) -> None:
        """
        停止模拟音频引擎
        """
        self.is_running = False
        print("[模拟音频引擎] 已停止")

    def pause(self) -> None:
        """暂停(模拟)"""
        self._paused = True
        print("[模拟音频引擎] 已暂停")

    def resume(self) -> None:
        """恢复(模拟)"""
        self._paused = False
        print("[模拟音频引擎] 已恢复")

    def is_paused(self) -> bool:
        """返回是否暂停(模拟)"""
        return self._paused

    def update_parameters(self, params: MusicParameters) -> None:
        """
        更新音乐参数

        Args:
            params: 音乐参数对象
        """
        self.current_params = params

        # 模拟参数处理
        if params.trigger_turbo_sound:
            print("[模拟音频] 触发涡轮音效")
        if params.trigger_drs_sound:
            print("[模拟音频] 触发DRS音效")
        if params.trigger_warning_sound:
            print("[模拟音频] 触发警告音效")
        if params.trigger_celebration:
            print("[模拟音频] 触发庆祝音效")

    def set_master_volume(self, volume: float) -> None:
        """
        设置主音量

        Args:
            volume: 音量值 (0.0 到 1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
        print(f"[模拟音频] 主音量设置为: {self.master_volume:.2f}")

    def get_status(self) -> Dict[str, Any]:
        """
        获取引擎状态

        Returns:
            Dict[str, Any]: 状态信息字典
        """
        return {
            "is_running": self.is_running,
            "master_volume": self.master_volume,
            "beat_count": self.beat_count,
            "current_bpm": self.current_params.bpm if self.current_params else 0,
        }

    def cleanup(self) -> None:
        """
        清理资源
        """
        self.stop()
        print("[模拟音频引擎] 资源已清理")

    def _mock_playback_loop(self) -> None:
        """
        模拟播放循环
        """
        print("[模拟音频引擎] 播放循环已启动")

        while self.is_running:
            try:
                if self._paused:
                    time.sleep(0.05)
                    continue
                if self.current_params is None:
                    time.sleep(0.1)
                    continue

                # 模拟节拍
                beat_interval = 60.0 / self.current_params.bpm
                time.sleep(beat_interval)

                self.beat_count += 1

                # 每10个节拍打印一次状态
                if self.beat_count % 10 == 0:
                    print(
                        f"[模拟音频] 节拍: {self.beat_count}, "
                        f"BPM: {self.current_params.bpm:.1f}, "
                        f"音量: {self.current_params.volume:.2f}"
                    )

            except Exception as e:
                print(f"[模拟音频] 播放循环错误: {e}")
                time.sleep(0.1)

        print("[模拟音频引擎] 播放循环已停止")


class PygameStemsAudioEngine(AudioEngine):
    """基于 pygame.mixer 的分轨音频引擎

    使用四个分轨 (drums/bass/vocals/other) 循环播放, 并根据 MusicParameters
    动态调制各分轨音量与左右声像, 实现可听到的真实输出。

    说明:
    - 分轨目录通过环境变量 ACC_STEMS_DIR 指定;
      若未设置且默认示例目录存在, 将自动使用示例目录。
    - 若找不到分轨文件, 将抛出异常, 并在上层回退为模拟引擎。
    """

    def __init__(self, config: AudioConfig) -> None:
        """初始化分轨音频引擎

        Args:
            config (AudioConfig): 音频配置
        """
        self.config = config
        self.is_running = False
        self.master_volume = 1.0
        self.current_params: Optional[MusicParameters] = None

        # 资源
        self._channels: Dict[str, Any] = {}
        self._sounds: Dict[str, Any] = {}

        # 分轨基础音量(为动态调制留余量)
        self._base_volumes: Dict[str, float] = {
            "drums": 0.8,
            "bass": 0.75,
            "vocals": 0.40,
            "other": 0.65,
        }

        # 暂停状态
        self._paused = False

        # 解析分轨目录
        self.stems_dir = os.environ.get("ACC_STEMS_DIR", "").strip()
        if not self.stems_dir:
            # 默认示例目录: <project_root>/songs/htdemucs/lose my mind
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            default_dir = os.path.join(
                project_root, "songs", "htdemucs", "lose my mind"
            )
            if os.path.isdir(default_dir):
                self.stems_dir = default_dir

        if not self.stems_dir:
            raise RuntimeError(
                "未设置分轨目录 ACC_STEMS_DIR，且默认示例目录不存在。"
                "请设置环境变量 ACC_STEMS_DIR 指向包含 "
                "drums.wav/bass.wav/vocals.wav/other.wav 的目录。"
            )

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    def start(self) -> bool:
        """启动分轨后端并开始循环播放"""
        if self.is_running:
            return True

        # 延迟导入, 避免模块级依赖导致导入失败
        try:
            import pygame  # type: ignore
        except Exception as e:
            raise RuntimeError(f"导入 pygame 失败: {e}")

        # 校验分轨文件
        required = ["drums", "bass", "vocals", "other"]
        for n in required:
            p = os.path.join(self.stems_dir, f"{n}.wav")
            if not os.path.isfile(p):
                raise FileNotFoundError(f"未找到分轨文件: {p}")

        # 初始化音频
        try:
            # 设置音频输出设备
            if self.config.output_device:
                import pygame._sdl2.audio as audio  # type: ignore

                # 获取可用音频设备
                audio.init()
                devices = audio.get_audio_device_names(False)  # False表示输出设备
                if self.config.output_device in devices:
                    audio.set_audio_device(self.config.output_device)
                else:
                    print(
                        f"[PygameStems] 指定的音频设备 '{self.config.output_device}' 不可用，使用默认设备"
                    )
                    print(f"[PygameStems] 可用设备: {devices}")

            pygame.mixer.pre_init(
                self.config.sample_rate,
                size=-16,
                channels=2,
                buffer=max(256, int(self.config.buffer_size)),
            )
            pygame.init()
        except Exception as e:
            raise RuntimeError(f"初始化 pygame 音频失败: {e}")

        # 加载声音与分配声道
        try:
            for n in required:
                self._sounds[n] = pygame.mixer.Sound(
                    os.path.join(self.stems_dir, f"{n}.wav")
                )
            for idx, n in enumerate(required):
                self._channels[n] = pygame.mixer.Channel(idx)
        except Exception as e:
            raise RuntimeError(f"加载分轨失败: {e}")

        # 应用初始音量
        self._apply_all_volumes(pan=0.0)

        # 循环播放
        for n, snd in self._sounds.items():
            self._channels[n].play(snd, loops=-1)

        self.is_running = True
        print("[PygameStems] 分轨后端已启动")
        return True

    def stop(self) -> None:
        """停止播放并释放资源"""
        if not self.is_running:
            return
        try:
            import pygame  # type: ignore

            pygame.mixer.stop()
        except Exception:
            pass
        finally:
            self.is_running = False
            print("[PygameStems] 分轨后端已停止")

    # ------------------------------------------------------------------
    # 参数更新
    # ------------------------------------------------------------------
    def update_parameters(self, params: MusicParameters) -> None:
        """根据音乐参数动态调制分轨音量与声像"""
        if not self.is_running:
            return
        self.current_params = params

        # 计算每轨目标音量(0-1), 融合主存在感(volume)
        master = max(0.0, min(1.0, params.volume))
        brightness = max(0.0, min(1.0, params.brightness))
        distortion = max(0.0, min(1.0, params.distortion_amount))

        vol_map: Dict[str, float] = {
            "drums": self._base_volumes["drums"]
            * (0.8 + 0.4 * min(1.0, master + 0.5 * distortion)),
            "bass": self._base_volumes["bass"] * (0.7 + 0.5 * master),
            "vocals": self._base_volumes["vocals"] * (0.9 + 0.1 * master),
            "other": self._base_volumes["other"] * (0.6 + 0.4 * brightness),
        }

        # 应用主存在感与声像
        self._apply_all_volumes(pan=params.pan, master=master, per_stem=vol_map)

        # 处理一次性触发(当前以日志代替)
        if params.trigger_turbo_sound:
            print("[PygameStems] 触发涡轮音效")
        if params.trigger_drs_sound:
            print("[PygameStems] 触发DRS音效")
        if params.trigger_warning_sound:
            print("[PygameStems] 触发警告音效")
        if params.trigger_celebration:
            print("[PygameStems] 触发庆祝音效")

    def set_master_volume(self, volume: float) -> None:
        """设置主音量(存在感)"""
        self.master_volume = max(0.0, min(1.0, float(volume)))

    def get_status(self) -> Dict[str, Any]:
        """获取后端状态"""
        return {
            "is_running": self.is_running,
            "backend": "pygame_stems",
            "stems_dir": self.stems_dir,
            "master_volume": getattr(self, "master_volume", 1.0),
            "has_params": self.current_params is not None,
        }

    def cleanup(self) -> None:
        """清理资源"""
        self.stop()

    @staticmethod
    def list_audio_devices() -> List[str]:
        """列出所有可用的音频输出设备

        Returns:
            List[str]: 可用音频设备名称列表
        """
        try:
            import pygame  # type: ignore
            import pygame._sdl2.audio as audio  # type: ignore

            # 初始化音频系统
            pygame.init()
            audio.init()

            # 获取输出设备列表
            devices = audio.get_audio_device_names(False)  # False表示输出设备
            return devices

        except Exception as e:
            print(f"[PygameStems] 获取音频设备列表失败: {e}")
            return []

    @staticmethod
    def get_current_audio_device() -> Optional[str]:
        """获取当前使用的音频输出设备

        Returns:
            Optional[str]: 当前音频设备名称，如果无法获取则返回None
        """
        try:
            import pygame._sdl2.audio as audio  # type: ignore

            if hasattr(audio, "get_audio_device_name"):
                return audio.get_audio_device_name(False, 0)  # 获取默认输出设备
            return None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # 播放控制（暂停/恢复）
    # ------------------------------------------------------------------
    def pause(self) -> None:
        """暂停所有分轨的播放

        使用 pygame.mixer.pause() 统一暂停所有声道。
        若引擎尚未启动或已处于暂停状态，则不执行任何操作。
        """
        if not self.is_running or self._paused:
            return
        try:
            import pygame  # type: ignore

            pygame.mixer.pause()
            self._paused = True
        except Exception:
            # 忽略暂停过程中的异常，保持稳定
            pass

    def resume(self) -> None:
        """恢复所有分轨的播放

        使用 pygame.mixer.unpause() 恢复所有声道的播放。
        若引擎未启动或未处于暂停状态，则不执行任何操作。
        """
        if not self.is_running or not self._paused:
            return
        try:
            import pygame  # type: ignore

            pygame.mixer.unpause()
            self._paused = False
        except Exception:
            # 忽略恢复过程中的异常
            pass

    def is_paused(self) -> bool:
        """返回当前是否处于暂停状态"""
        return bool(self._paused)

    # ------------------------------------------------------------------
    # 高级控制功能
    # ------------------------------------------------------------------

    def set_stem_volume(self, stem: str, volume: float) -> None:
        """设置单个分轨音量

        Args:
            stem: 分轨名称 ('drums', 'bass', 'vocals', 'other')
            volume: 音量 (0.0-2.0，1.0为默认)
        """
        if not self.is_running:
            return

        volume = max(0.0, min(2.0, float(volume)))

        if stem in self._base_volumes:
            # 更新基础音量并重新应用所有音量设置
            self._base_volumes[stem] = volume * 0.8  # 保留原有缩放比例

            # 重新应用当前的音量和声像设置
            current_params = self.current_params
            if current_params:
                master = max(0.0, min(1.0, current_params.volume))
                self._apply_all_volumes(pan=current_params.pan, master=master)
            else:
                self._apply_all_volumes()

    def set_stem_mute(self, stem: str, muted: bool) -> None:
        """设置分轨静音状态

        Args:
            stem: 分轨名称
            muted: 是否静音
        """
        if not self.is_running or stem not in self._channels:
            return

        if not hasattr(self, "_stem_muted"):
            self._stem_muted = {name: False for name in self._base_volumes.keys()}

        self._stem_muted[stem] = bool(muted)

        # 立即应用静音设置
        channel = self._channels[stem]
        if muted:
            channel.set_volume(0.0, 0.0)
        else:
            # 恢复正常音量
            current_params = self.current_params
            if current_params:
                master = max(0.0, min(1.0, current_params.volume))
                self._apply_all_volumes(pan=current_params.pan, master=master)
            else:
                self._apply_all_volumes()

    def set_stem_solo(self, stem: str, solo: bool) -> None:
        """设置分轨独奏状态

        Args:
            stem: 分轨名称
            solo: 是否独奏
        """
        if not self.is_running:
            return

        if not hasattr(self, "_stem_solo"):
            self._stem_solo = {name: False for name in self._base_volumes.keys()}

        self._stem_solo[stem] = bool(solo)

        # 应用独奏逻辑：如果有任何分轨独奏，其他分轨静音
        has_solo = any(self._stem_solo.values())

        for name in self._base_volumes.keys():
            channel = self._channels[name]
            if has_solo:
                if self._stem_solo.get(name, False):
                    # 独奏分轨：正常音量
                    self._apply_single_stem_volume(name)
                else:
                    # 非独奏分轨：静音
                    channel.set_volume(0.0, 0.0)
            else:
                # 无独奏：所有分轨正常
                self._apply_single_stem_volume(name)

    def fade_pause(self, duration: float = 0.2) -> None:
        """淡入淡出暂停

        Args:
            duration: 淡出时长（秒）
        """
        if not self.is_running or self._paused:
            return

        try:
            import threading
            import time

            # 记录当前各分轨音量
            current_volumes = {}
            for name, channel in self._channels.items():
                left_vol = (
                    channel.get_volume()[0]
                    if hasattr(channel.get_volume(), "__getitem__")
                    else channel.get_volume()
                )
                current_volumes[name] = left_vol

            def fade_out_thread():
                try:
                    steps = max(10, int(duration * 50))  # 50步每秒
                    step_time = duration / steps

                    for step in range(steps):
                        if self._paused:  # 如果已经暂停则停止淡出
                            break

                        fade_factor = 1.0 - (step + 1) / steps

                        for name, channel in self._channels.items():
                            if name in current_volumes:
                                target_vol = current_volumes[name] * fade_factor
                                channel.set_volume(target_vol, target_vol)

                        time.sleep(step_time)

                    # 完成淡出后暂停
                    if not self._paused:
                        self.pause()

                except Exception as e:
                    print(f"[PygameStems] 淡出暂停失败: {e}")
                    self.pause()  # 回退到直接暂停

            # 启动淡出线程
            threading.Thread(target=fade_out_thread, daemon=True).start()

        except Exception as e:
            print(f"[PygameStems] 淡出暂停初始化失败，使用直接暂停: {e}")
            self.pause()

    def fade_resume(self, duration: float = 0.2) -> None:
        """淡入淡出恢复

        Args:
            duration: 淡入时长（秒）
        """
        if not self.is_running or not self._paused:
            return

        try:
            import threading
            import time

            # 先恢复播放但音量为0
            self.resume()

            # 计算目标音量
            target_volumes = {}
            current_params = self.current_params
            if current_params:
                master = max(0.0, min(1.0, current_params.volume)) * self.master_volume
                for name in self._base_volumes.keys():
                    base_vol = self._base_volumes.get(name, 0.7)
                    target_vol = max(0.0, min(1.0, base_vol * master))
                    target_volumes[name] = target_vol
            else:
                for name in self._base_volumes.keys():
                    target_volumes[name] = (
                        self._base_volumes.get(name, 0.7) * self.master_volume
                    )

            def fade_in_thread():
                try:
                    steps = max(10, int(duration * 50))  # 50步每秒
                    step_time = duration / steps

                    for step in range(steps):
                        if self._paused:  # 如果又被暂停则停止淡入
                            break

                        fade_factor = (step + 1) / steps

                        for name, channel in self._channels.items():
                            if name in target_volumes:
                                current_vol = target_volumes[name] * fade_factor
                                # 检查静音和独奏状态
                                if hasattr(
                                    self, "_stem_muted"
                                ) and self._stem_muted.get(name, False):
                                    current_vol = 0.0
                                elif hasattr(self, "_stem_solo"):
                                    has_solo = any(self._stem_solo.values())
                                    if has_solo and not self._stem_solo.get(
                                        name, False
                                    ):
                                        current_vol = 0.0

                                channel.set_volume(current_vol, current_vol)

                        time.sleep(step_time)

                except Exception as e:
                    print(f"[PygameStems] 淡入恢复失败: {e}")
                    # 恢复正常音量
                    if current_params:
                        master = max(0.0, min(1.0, current_params.volume))
                        self._apply_all_volumes(pan=current_params.pan, master=master)
                    else:
                        self._apply_all_volumes()

            # 启动淡入线程
            threading.Thread(target=fade_in_thread, daemon=True).start()

        except Exception as e:
            print(f"[PygameStems] 淡入恢复失败，使用直接恢复: {e}")
            self.resume()

    def update_config(self, config: AudioConfig) -> None:
        """更新音频配置

        Args:
            config: 新的音频配置
        """
        self.config = config

        # 应用分轨音量配置
        for stem, volume in config.stem_volumes.items():
            if stem in self._base_volumes:
                self.set_stem_volume(stem, volume)

        # 应用静音配置
        for stem, muted in config.stem_muted.items():
            self.set_stem_mute(stem, muted)

        # 应用独奏配置
        for stem, solo in config.stem_solo.items():
            self.set_stem_solo(stem, solo)

        # 更新主音量
        self.set_master_volume(config.master_volume)

    # ------------------------------------------------------------------
    # 内部工具（更新以支持高级功能）
    # ------------------------------------------------------------------
    def _apply_single_stem_volume(self, name: str) -> None:
        """为单个分轨应用音量设置

        Args:
            name: 分轨名称
        """
        if name not in self._channels:
            return

        # 检查静音状态
        if hasattr(self, "_stem_muted") and self._stem_muted.get(name, False):
            self._channels[name].set_volume(0.0, 0.0)
            return

        # 检查独奏状态
        if hasattr(self, "_stem_solo"):
            has_solo = any(self._stem_solo.values())
            if has_solo and not self._stem_solo.get(name, False):
                self._channels[name].set_volume(0.0, 0.0)
                return

        # 计算正常音量
        base_vol = self._base_volumes.get(name, 0.7)
        master = self.master_volume

        if self.current_params:
            master *= max(0.0, min(1.0, self.current_params.volume))

        final_vol = max(0.0, min(1.0, base_vol * master))

        # 应用声像
        if self.current_params:
            left, right = self._pan_to_lr(final_vol, self.current_params.pan)
        else:
            left = right = final_vol

        self._channels[name].set_volume(left, right)

    def _apply_all_volumes(
        self,
        pan: float = 0.0,
        master: float = 1.0,
        per_stem: Optional[Dict[str, float]] = None,
    ) -> None:
        """将音量/声像应用到所有分轨"""
        if per_stem is None:
            per_stem = self._base_volumes

        # 归一化主音量
        master = max(0.0, min(1.0, master)) * self.master_volume

        for name in ("drums", "bass", "vocals", "other"):
            base = max(
                0.0, min(1.0, per_stem.get(name, self._base_volumes.get(name, 0.7)))
            )
            vol = max(0.0, min(1.0, base * master))

            # 检查静音状态
            if hasattr(self, "_stem_muted") and self._stem_muted.get(name, False):
                vol = 0.0

            # 检查独奏状态
            if hasattr(self, "_stem_solo"):
                has_solo = any(self._stem_solo.values()) if self._stem_solo else False
                if has_solo and not self._stem_solo.get(name, False):
                    vol = 0.0

            l, r = self._pan_to_lr(vol, pan)
            ch = self._channels.get(name)
            if ch is not None:
                ch.set_volume(l, r)

    def _pan_to_lr(self, vol: float, pan: float) -> tuple[float, float]:
        """根据声像将总体音量分配到左右声道"""
        pan = max(-1.0, min(1.0, float(pan)))
        left = vol * (1.0 - max(0.0, pan))
        right = vol * (1.0 + min(0.0, pan))
        return max(0.0, min(1.0, left)), max(0.0, min(1.0, right))
