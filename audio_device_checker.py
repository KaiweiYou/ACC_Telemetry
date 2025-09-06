#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频设备诊断工具

用于检查和配置音频输出设备，解决Moonlight串流无法听到音乐引擎声音的问题。

使用方法:
    python audio_device_checker.py
"""

import os
import sys

try:
    import pygame
    import pygame._sdl2.audio as audio
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装 pygame")
    sys.exit(1)


def main():
    """主函数"""
    print("=== ACC Telemetry 音频设备诊断工具 ===\n")

    try:
        # 初始化pygame
        pygame.init()

        print("1. 系统音频信息:")
        print(f"   pygame版本: {pygame.version.ver}")
        print(f"   SDL版本: {pygame.get_sdl_version()}")
        print()

        try:
            # 使用pygame._sdl2.audio获取设备信息
            import pygame._sdl2.audio as audio

            # 获取所有音频设备
            print("2. 可用音频输出设备:")
            output_devices = audio.get_audio_device_names(False)

            if not output_devices:
                print("   未找到音频输出设备")
            else:
                for i, device in enumerate(output_devices):
                    marker = " <- 默认" if i == 0 else ""
                    print(f"   [{i}] {device}{marker}")

            print()

            # 获取当前设备
            try:
                current_device = audio.get_audio_device_name(False, 0)
                print(f"3. 当前默认输出设备: {current_device}")
            except:
                print("3. 无法获取当前默认设备")

            print()

            # 获取输入设备
            print("4. 可用音频输入设备:")
            input_devices = audio.get_audio_device_names(True)

            if not input_devices:
                print("   未找到音频输入设备")
            else:
                for i, device in enumerate(input_devices):
                    print(f"   [{i}] {device}")

            print()

        except ImportError:
            print("2. 无法获取音频设备信息 (需要pygame 2.0+)")
            print()

        except Exception as e:
            print(f"2. 获取音频设备信息失败: {e}")
            print()

        # 提供配置建议
        print("5. 配置建议:")
        print("   如果通过Moonlight串流听不到声音，可以尝试以下方法:")
        print(
            "   - 在配置文件中指定虚拟音频设备 (如 'VoiceMeeter Input' 或 'VB-Cable')"
        )
        print("   - 使用Windows的立体声混音作为输出设备")
        print("   - 确保Moonlight客户端的音频重定向已启用")
        print()

        # 检查配置文件
        config_path = os.path.join(
            os.path.dirname(__file__), "acc_telemetry", "config", "audio_config.json"
        )
        if os.path.exists(config_path):
            import json

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                current_output = config.get("global", {}).get("output_device", "未设置")
                print(f"6. 当前配置文件中的输出设备: {current_output}")
        else:
            print("6. 配置文件不存在，将使用默认设备")

        print()
        print("使用说明:")
        print("- 要指定特定输出设备，请编辑 acc_telemetry/config/audio_config.json")
        print('- 在 global 部分添加: "output_device": "设备名称"')
        print("- 重启应用程序使配置生效")

    except Exception as e:
        print(f"诊断过程中出现错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
