#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry 主程序

这个文件提供了一个统一的入口点，用户可以通过命令行参数选择启动不同的功能模块。
"""

import sys
import argparse
from acc_telemetry.config import ADVANCED_CONFIG

def print_header():
    """打印程序头部信息"""
    print("\n====================================")
    print("       ACC 遥测数据工具        ")
    print("====================================")
    print("版本: 1.0.0")
    print("====================================")

def print_usage():
    """打印使用说明"""
    print("\n使用方法:")
    print("  python main.py [模式] [参数]")
    print("\n可用模式:")
    print("  terminal  - 在终端显示遥测数据")
    print("  dashboard - 启动图形化仪表盘")
    print("  osc       - 启动OSC数据发送器")
    print("  help      - 显示此帮助信息")
    print("\n示例:")
    print("  python main.py terminal  # 在终端显示遥测数据")
    print("  python main.py dashboard # 启动图形化仪表盘")
    print("  python main.py osc       # 启动OSC数据发送器")
    print("  python main.py osc 127.0.0.1 9000 # 发送OSC数据到指定IP和端口")

def run_terminal_mode():
    """运行终端模式"""
    from acc_telemetry.core.telemetry import telemetry_main
    print("\n启动终端模式...")
    telemetry_main()

def run_dashboard_mode():
    """运行仪表盘模式"""
    from acc_telemetry.ui.dashboard import AccDashboard
    print("\n启动仪表盘模式...")
    dashboard = AccDashboard()
    dashboard.run()

def run_osc_mode(args):
    """运行OSC发送模式"""
    from acc_telemetry.utils.osc_sender import ACCDataSender
    
    ip = None
    port = None
    
    if len(args) > 0:
        ip = args[0]
    
    if len(args) > 1:
        try:
            port = int(args[1])
        except ValueError:
            print(f"错误: 端口必须是一个整数")
            return
    
    print("\n启动OSC发送模式...")
    sender = ACCDataSender(ip, port)
    sender.run()

def main():
    """主函数"""
    print_header()
    
    # 解析命令行参数
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        print_usage()
        return
    
    mode = sys.argv[1].lower()
    args = sys.argv[2:]
    
    # 根据模式启动相应功能
    if mode == "terminal":
        run_terminal_mode()
    elif mode == "dashboard":
        run_dashboard_mode()
    elif mode == "osc":
        run_osc_mode(args)
    else:
        print(f"错误: 未知模式 '{mode}'")
        print_usage()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        if ADVANCED_CONFIG['debug_mode']:
            # 在调试模式下显示完整错误信息
            import traceback
            print(f"\n发生错误: {e}")
            print("\n详细错误信息:")
            traceback.print_exc()
        else:
            print(f"\n发生错误: {e}")
        sys.exit(1)