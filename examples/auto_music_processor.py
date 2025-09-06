#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块: auto_music_processor

一键式音乐库批量处理工具
自动完成歌曲分轨、分析和标准化目录创建
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

# 将项目根目录添加到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from examples.batch_song_processor import batch_process, generate_summary_report


class AutoMusicProcessor:
    """自动音乐处理工具类"""

    def __init__(self):
        self.songs_dir = project_root / "songs"
        self.config_file = Path(__file__).parent / "auto_process_config.json"
        self.default_config = {
            "input_directory": "./music_input",
            "output_directory": "./songs",
            "audio_extensions": [".mp3", ".wav", ".flac", ".m4a", ".ogg"],
            "demucs_model": "htdemucs",
            "skip_existing": True,
            "auto_cleanup": True,
        }

    def check_dependencies(self) -> Dict[str, bool]:
        """检查必要的依赖项"""
        deps = {"demucs": False, "ffmpeg": False, "python": False}

        # 检查demucs
        try:
            result = subprocess.run(
                ["demucs", "--version"], capture_output=True, text=True
            )
            deps["demucs"] = result.returncode == 0
        except FileNotFoundError:
            deps["demucs"] = False

        # 检查ffmpeg
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True
            )
            deps["ffmpeg"] = result.returncode == 0
        except FileNotFoundError:
            deps["ffmpeg"] = False

        # 检查Python
        deps["python"] = sys.version_info >= (3, 8)

        return deps

    def install_demucs(self) -> bool:
        """自动安装Demucs"""
        print("正在安装Demucs...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "demucs"], check=True
            )
            return True
        except subprocess.CalledProcessError:
            print("安装失败，请手动安装: pip install demucs")
            return False

    def load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("配置文件格式错误，使用默认配置")

        return self.default_config.copy()

    def save_config(self, config: Dict):
        """保存配置文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def setup_directories(self, config: Dict) -> bool:
        """设置必要的目录"""
        try:
            # 确保输入和输出目录存在
            Path(config["input_directory"]).mkdir(parents=True, exist_ok=True)
            Path(config["output_directory"]).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"目录设置失败: {e}")
            return False

    def interactive_setup(self) -> Dict:
        """交互式设置配置"""
        config = self.load_config()

        print("=== 自动音乐处理设置 ===")
        print("按回车使用默认值，或直接输入新值")

        # 输入目录
        default_input = config.get("input_directory", "./music_input")
        new_input = input(f"输入音乐目录 [{default_input}]: ").strip()
        if new_input:
            config["input_directory"] = new_input
        else:
            config["input_directory"] = default_input

        # 输出目录
        default_output = config.get("output_directory", "./songs")
        new_output = input(f"输出歌曲目录 [{default_output}]: ").strip()
        if new_output:
            config["output_directory"] = new_output
        else:
            config["output_directory"] = default_output

        # 跳过已存在文件
        skip_existing = input("跳过已存在的歌曲? [Y/n]: ").strip().lower()
        config["skip_existing"] = skip_existing != "n"

        # 自动清理临时文件
        auto_cleanup = input("自动清理临时文件? [Y/n]: ").strip().lower()
        config["auto_cleanup"] = auto_cleanup != "n"

        self.save_config(config)
        return config

    def process_music_library(self, config: Dict = None) -> bool:
        """处理整个音乐库"""
        if config is None:
            config = self.load_config()

        if not self.setup_directories(config):
            return False

        input_dir = Path(config["input_directory"])
        if not input_dir.exists() or not any(input_dir.iterdir()):
            print(f"输入目录不存在或为空: {input_dir}")
            print("请将音乐文件放入该目录后重试")
            return False

        print(f"\n开始处理音乐库...")
        print(f"输入目录: {config['input_directory']}")
        print(f"输出目录: {config['output_directory']}")
        print(f"跳过已存在: {config['skip_existing']}")

        # 执行批量处理
        results = batch_process(
            config["input_directory"],
            config["output_directory"],
            skip_existing=config["skip_existing"],
        )

        # 生成报告
        report_file = Path(config["output_directory"]) / "processing_report.json"
        generate_summary_report(results, str(report_file))

        return True

    def quick_start(self):
        """一键启动处理"""
        print("=== 自动音乐处理工具 ===")

        # 检查依赖
        deps = self.check_dependencies()
        if not deps["demucs"]:
            print("检测到Demucs未安装")
            if input("是否自动安装? [Y/n]: ").strip().lower() != "n":
                if not self.install_demucs():
                    return False
            else:
                print("请先安装Demucs: pip install demucs")
                return False

        if not deps["ffmpeg"]:
            print("警告: 未检测到ffmpeg，可能影响音频处理")
            print("建议安装: conda install ffmpeg 或 下载ffmpeg并添加到PATH")

        # 选择处理方式
        print("\n选择处理方式:")
        print("1. 一键处理 (使用上次配置)")
        print("2. 交互式设置")
        print("3. 预览模式 (仅查看文件)")

        choice = input("请选择 [1/2/3]: ").strip()

        if choice == "1":
            config = self.load_config()
        elif choice == "2":
            config = self.interactive_setup()
        elif choice == "3":
            config = self.load_config()
            input_dir = Path(config["input_directory"])

            from examples.batch_song_processor import find_audio_files

            audio_files = find_audio_files(str(input_dir))

            print(f"\n预览模式 - 找到 {len(audio_files)} 个音频文件:")
            for i, file in enumerate(audio_files, 1):
                print(f"  {i}. {file.name}")

            proceed = input("\n是否继续处理? [Y/n]: ").strip().lower()
            if proceed == "n":
                return False
        else:
            print("无效选择")
            return False

        return self.process_music_library(config)


def main():
    """主程序入口"""
    processor = AutoMusicProcessor()

    try:
        if processor.quick_start():
            print("\n✅ 音乐库处理完成！")
            print("现在可以使用 multi_song_runner.py 播放处理后的歌曲")
        else:
            print("\n❌ 处理未完成")
    except KeyboardInterrupt:
        print("\n\n用户中断处理")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
