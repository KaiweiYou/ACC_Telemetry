#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块: multi_song_runner

多歌曲交互运行器 (MBUX Sound Drive 增强版):
- 支持多首歌曲的自动管理和切换
- 提供歌曲选择界面和播放队列功能
- 保持 MBUX Sound Drive 的音乐表现力特性
- 支持随机播放、顺序播放、单曲循环等模式
"""

import json
import os
import random
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pygame

# 将项目根目录加入模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData
from examples.single_song_runner import MusicalExpressionEngine


class SongManager:
    """歌曲管理器 - 负责扫描和管理所有可用的歌曲"""

    def __init__(self, songs_root_dir: str):
        """初始化歌曲管理器

        Args:
            songs_root_dir: 歌曲根目录路径
        """
        self.songs_root = Path(songs_root_dir)
        self.available_songs: List[Dict[str, Any]] = []
        self.current_song_index = 0
        self.scan_songs()

    def scan_songs(self) -> None:
        """扫描根目录下所有可用的歌曲"""
        self.available_songs = []

        # 遍历所有可能的歌曲目录
        for song_dir in self.songs_root.rglob("*"):
            if song_dir.is_dir():
                # 检查是否包含必要的分轨文件和分析文件
                required_files = [
                    "drums.wav",
                    "bass.wav",
                    "vocals.wav",
                    "other.wav",
                    "analysis.json",
                ]
                if all((song_dir / file).exists() for file in required_files):
                    # 读取歌曲信息
                    try:
                        with open(
                            song_dir / "analysis.json", "r", encoding="utf-8"
                        ) as f:
                            analysis = json.load(f)

                        song_info = {
                            "name": song_dir.name,
                            "path": str(song_dir),
                            "duration": analysis.get("duration", 0),
                            "bpm": analysis.get("bpm", 0),
                            "artist": analysis.get("artist", "Unknown"),
                            "genre": analysis.get("genre", "Unknown"),
                        }
                        self.available_songs.append(song_info)
                    except Exception as e:
                        print(f"跳过歌曲 {song_dir.name}: {e}")

        print(f"扫描完成，找到 {len(self.available_songs)} 首可用歌曲")

    def get_song_count(self) -> int:
        """获取可用歌曲数量"""
        return len(self.available_songs)

    def get_song_info(self, index: int) -> Optional[Dict[str, Any]]:
        """获取指定索引的歌曲信息"""
        if 0 <= index < len(self.available_songs):
            return self.available_songs[index]
        return None

    def get_next_song(self, mode: str = "sequential") -> Optional[Dict[str, Any]]:
        """获取下一首歌曲

        Args:
            mode: 播放模式 ('sequential', 'random', 'repeat')
        """
        if not self.available_songs:
            return None

        if mode == "random":
            return random.choice(self.available_songs)
        elif mode == "repeat":
            return self.available_songs[self.current_song_index]
        else:  # sequential
            self.current_song_index = (self.current_song_index + 1) % len(
                self.available_songs
            )
            return self.available_songs[self.current_song_index]

    def set_current_song(self, index: int) -> bool:
        """手动设置当前歌曲"""
        if 0 <= index < len(self.available_songs):
            self.current_song_index = index
            return True
        return False


class MultiSongRunner:
    """多歌曲交互运行器"""

    def __init__(self, songs_root_dir: str = None):
        """初始化多歌曲运行器

        Args:
            songs_root_dir: 歌曲根目录，默认为项目 songs 目录
        """
        if songs_root_dir is None:
            songs_root_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "songs"
            )

        self.song_manager = SongManager(songs_root_dir)
        self.current_runner = None
        self.playback_mode = "sequential"  # sequential, random, repeat
        self.auto_advance = True

        # 遥测控制
        self._running = False
        self._thread = None
        self.telemetry = ACCTelemetry()

    def list_songs(self) -> None:
        """显示所有可用歌曲列表"""
        songs = self.song_manager.available_songs
        if not songs:
            print("没有找到可用的歌曲！")
            return

        print("\n=== 可用歌曲列表 ===")
        for i, song in enumerate(songs):
            marker = " -> 当前" if i == self.song_manager.current_song_index else "    "
            print(f"{marker}[{i}] {song['name']}")
            print(
                f"     艺术家: {song['artist']} | BPM: {song['bpm']} | 时长: {song['duration']:.1f}s"
            )
            print()

    def play_song(self, song_index: int = None) -> bool:
        """播放指定歌曲

        Args:
            song_index: 歌曲索引，None 表示播放当前歌曲
        """
        if song_index is not None:
            if not self.song_manager.set_current_song(song_index):
                print("无效的歌曲索引！")
                return False

        song_info = self.song_manager.get_song_info(
            self.song_manager.current_song_index
        )
        if not song_info:
            print("没有找到歌曲！")
            return False

        # 停止当前播放
        if self.current_runner:
            self.current_runner.stop()

        # 创建新的单歌曲运行器
        try:
            from examples.single_song_runner import SingleSongRunner

            self.current_runner = SingleSongRunner(song_info["path"])
            self.current_runner.start()
            print(f"正在播放: {song_info['name']}")
            return True
        except Exception as e:
            print(f"播放失败: {e}")
            return False

    def play_next(self) -> bool:
        """播放下一首歌曲"""
        next_song = self.song_manager.get_next_song(self.playback_mode)
        if next_song:
            return self.play_song()
        return False

    def play_previous(self) -> bool:
        """播放上一首歌曲"""
        if self.song_manager.get_song_count() > 0:
            self.song_manager.current_song_index = (
                self.song_manager.current_song_index - 1
            ) % self.song_manager.get_song_count()
            return self.play_song()
        return False

    def set_playback_mode(self, mode: str) -> bool:
        """设置播放模式

        Args:
            mode: 播放模式 ('sequential', 'random', 'repeat')
        """
        if mode in ["sequential", "random", "repeat"]:
            self.playback_mode = mode
            print(f"播放模式已设置为: {mode}")
            return True
        return False

    def start_auto_advance(self) -> None:
        """启动自动切歌功能"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._auto_advance_loop, daemon=True)
            self._thread.start()

    def stop_auto_advance(self) -> None:
        """停止自动切歌"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _auto_advance_loop(self) -> None:
        """自动切歌曲循环"""
        while self._running:
            if self.current_runner and self.auto_advance:
                # 检查当前歌曲是否播放结束
                try:
                    # 这里需要根据实际播放状态来判断
                    time.sleep(5)  # 每5秒检查一次

                    # 简单的模拟：如果当前歌曲运行器停止，播放下一首
                    if not self.current_runner._running:
                        self.play_next()

                except Exception:
                    pass
            else:
                time.sleep(1)

    def interactive_control(self) -> None:
        """交互式控制台控制"""
        print("=== 多歌曲交互控制台 ===")
        print("命令:")
        print("  list - 显示歌曲列表")
        print("  play [n] - 播放指定歌曲")
        print("  next - 下一首")
        print("  prev - 上一首")
        print("  mode [sequential/random/repeat] - 设置播放模式")
        print("  info - 显示当前歌曲信息")
        print("  help - 显示帮助信息")
        print("  quit - 退出")
        print()

        while True:
            try:
                command = input("> ").strip().lower()

                if command == "list":
                    self.list_songs()

                elif command.startswith("play"):
                    parts = command.split()
                    if len(parts) > 1:
                        try:
                            index = int(parts[1])
                            self.play_song(index)
                        except ValueError:
                            print("请输入有效的歌曲编号")
                    else:
                        self.play_song()

                elif command == "next":
                    self.play_next()

                elif command == "prev":
                    self.play_previous()

                elif command.startswith("mode"):
                    parts = command.split()
                    if len(parts) > 1:
                        self.set_playback_mode(parts[1])
                    else:
                        print("可用模式: sequential, random, repeat")

                elif command == "info":
                    song = self.song_manager.get_song_info(
                        self.song_manager.current_song_index
                    )
                    if song:
                        print(f"当前: {song['name']} - {song['artist']}")
                        print(f"模式: {self.playback_mode}")
                    else:
                        print("没有正在播放的歌曲")

                elif command == "help":
                    print("\n=== 帮助信息 ===")
                    print("list - 显示所有可用歌曲列表")
                    print("play [n] - 播放指定编号的歌曲，如：play 0")
                    print("next - 播放下一首歌曲")
                    print("prev - 播放上一首歌曲")
                    print(
                        "mode [模式] - 设置播放模式：sequential(顺序)、random(随机)、repeat(重复)"
                    )
                    print("info - 显示当前播放歌曲的信息")
                    print("quit/exit/q - 退出程序")
                    print("help - 显示此帮助信息")

                elif command in ["quit", "exit", "q"]:
                    break

                else:
                    print("未知命令，输入 'help' 查看帮助")

            except KeyboardInterrupt:
                break

    def cleanup(self) -> None:
        """清理资源"""
        self.stop_auto_advance()
        if self.current_runner:
            self.current_runner.stop()
        try:
            self.telemetry.disconnect()
        except Exception:
            pass


def main() -> None:
    """主程序入口"""
    # 使用环境变量或默认路径
    songs_dir = os.environ.get("ACC_SONGS_DIR")
    if not songs_dir:
        songs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "songs")

    runner = MultiSongRunner(songs_dir)

    # 检查是否有可用歌曲
    if runner.song_manager.get_song_count() == 0:
        print("没有找到可用的歌曲！")
        print("请确保在 songs 目录下有完整的分轨文件和分析文件")
        return

    try:
        runner.list_songs()
        runner.interactive_control()
    except KeyboardInterrupt:
        print("\n正在退出...")
    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()
