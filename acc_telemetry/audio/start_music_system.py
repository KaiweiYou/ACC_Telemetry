#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC遥测音乐系统启动脚本

这个脚本提供了启动ACC遥测音乐系统的便捷方式，
包括GUI界面和命令行模式。

使用方法:
1. GUI模式: python start_music_system.py
2. 命令行模式: python start_music_system.py --cli
3. 显示帮助: python start_music_system.py --help

作者: Assistant
日期: 2024
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from .music_gui import MusicControlGUI
    from .music_integration import MusicIntegration, MusicConfig
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖模块都已正确安装")
    sys.exit(1)


def setup_logging(level=logging.INFO):
    """
    设置日志配置
    
    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('acc_music_system.log', encoding='utf-8')
        ]
    )


def check_dependencies():
    """
    检查系统依赖
    
    Returns:
        bool: 依赖检查是否通过
    """
    print("检查系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return False
    
    # 检查必要的模块
    required_modules = [
        'tkinter',
        'threading',
        'json',
        'time',
        'logging',
        'pathlib'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"错误: 缺少必要模块: {', '.join(missing_modules)}")
        return False
    
    # 检查OSC库
    try:
        from pythonosc import udp_client
        print("✓ python-osc库已安装")
    except ImportError:
        print("警告: python-osc库未安装，请运行: pip install python-osc")
        return False
    
    # 检查SuperCollider（可选）
    print("提示: 请确保SuperCollider已安装并运行acc_music_engine.scd脚本")
    
    print("依赖检查完成")
    return True


def run_gui_mode():
    """
    运行GUI模式
    """
    print("启动GUI模式...")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        
        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置窗口图标
            pass
        except:
            pass
        
        app = MusicControlGUI(root)
        
        print("GUI界面已启动")
        print("使用GUI界面控制音乐系统")
        
        app.run()
        
    except Exception as e:
        print(f"启动GUI时发生错误: {e}")
        logging.error(f"GUI启动错误: {e}")
        return False
    
    return True


def run_cli_mode(config_file=None):
    """
    运行命令行模式
    
    Args:
        config_file: 可选的配置文件路径
    """
    print("启动命令行模式...")
    
    try:
        # 加载配置
        config = MusicConfig()
        if config_file and os.path.exists(config_file):
            print(f"加载配置文件: {config_file}")
            # 这里可以添加配置文件加载逻辑
        
        # 创建音乐集成系统
        print("初始化音乐系统...")
        music_system = MusicIntegration(config)
        
        # 启动系统
        print("启动音乐系统...")
        if not music_system.start():
            print("启动音乐系统失败")
            return False
        
        print("\n🎵 ACC遥测音乐系统已启动 🏎️")
        print("="*50)
        print("系统状态:")
        print(f"  - 更新频率: {config.update_rate}Hz")
        print(f"  - OSC端口: {config.osc_port}")
        print(f"  - BPM范围: {config.bpm_range[0]}-{config.bpm_range[1]}")
        print("="*50)
        print("\n控制命令:")
        print("  - 按 's' 显示状态")
        print("  - 按 'q' 或 Ctrl+C 退出")
        print("\n等待遥测数据...")
        
        # 主循环
        try:
            while True:
                # 检查键盘输入（简单实现）
                try:
                    import select
                    import sys
                    
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        command = sys.stdin.readline().strip().lower()
                        
                        if command == 'q':
                            break
                        elif command == 's':
                            status = music_system.get_status()
                            print("\n当前状态:")
                            print(f"  - 系统运行: {status['running']}")
                            print(f"  - 遥测连接: {status['telemetry_connected']}")
                            print(f"  - 音乐引擎: {status['music_engine_running']}")
                            if status['last_data_time']:
                                print(f"  - 最后更新: {time.strftime('%H:%M:%S', time.localtime(status['last_data_time']))}")
                            print()
                    
                except ImportError:
                    # Windows系统可能没有select模块
                    pass
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n接收到中断信号...")
        
        # 停止系统
        print("正在停止音乐系统...")
        music_system.stop()
        print("音乐系统已停止")
        
    except Exception as e:
        print(f"运行命令行模式时发生错误: {e}")
        logging.error(f"CLI模式错误: {e}")
        return False
    
    return True


def create_desktop_shortcut():
    """
    创建桌面快捷方式（Windows）
    """
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "ACC音乐系统.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{__file__}"'
        shortcut.WorkingDirectory = str(project_root)
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print(f"桌面快捷方式已创建: {shortcut_path}")
        
    except ImportError:
        print("创建快捷方式需要安装: pip install winshell pywin32")
    except Exception as e:
        print(f"创建快捷方式时发生错误: {e}")


def show_system_info():
    """
    显示系统信息
    """
    print("\n🎵 ACC遥测音乐系统 🏎️")
    print("="*50)
    print(f"Python版本: {sys.version}")
    print(f"项目路径: {project_root}")
    print(f"操作系统: {os.name}")
    
    # 检查SuperCollider
    print("\nSuperCollider集成:")
    sc_script = project_root / "supercollider" / "acc_music_engine.scd"
    if sc_script.exists():
        print(f"✓ SuperCollider脚本: {sc_script}")
    else:
        print("✗ SuperCollider脚本未找到")
    
    print("="*50)


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="ACC遥测音乐系统启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python start_music_system.py              # 启动GUI模式
  python start_music_system.py --cli        # 启动命令行模式
  python start_music_system.py --info       # 显示系统信息
  python start_music_system.py --shortcut   # 创建桌面快捷方式

注意事项:
1. 启动前请确保SuperCollider已安装并运行
2. 确保ACC游戏正在运行并启用遥测数据
3. 检查防火墙设置，确保OSC通信正常
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='使用命令行模式启动（默认为GUI模式）'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='指定配置文件路径'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示系统信息'
    )
    
    parser.add_argument(
        '--shortcut',
        action='store_true',
        help='创建桌面快捷方式'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='检查系统依赖'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='启用详细日志输出'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    # 显示系统信息
    if args.info:
        show_system_info()
        return
    
    # 创建快捷方式
    if args.shortcut:
        create_desktop_shortcut()
        return
    
    # 检查依赖
    if args.check_deps or not check_dependencies():
        if args.check_deps:
            return
        else:
            print("依赖检查失败，请解决上述问题后重试")
            sys.exit(1)
    
    # 启动系统
    success = False
    
    if args.cli:
        success = run_cli_mode(args.config)
    else:
        success = run_gui_mode()
    
    if not success:
        print("系统启动失败")
        sys.exit(1)
    
    print("系统已正常退出")


if __name__ == "__main__":
    main()