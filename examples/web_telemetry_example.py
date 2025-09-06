#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC 遥测 Web 面板使用示例

这个示例展示了如何启动和使用Web遥测面板功能。
Web面板允许通过浏览器访问实时遥测数据，支持手机、平板等移动设备。

功能特点:
- 实时显示ACC遥测数据
- 响应式设计，支持移动设备
- WebSocket实时数据推送
- 现代化的仪表盘界面
- 局域网访问支持

使用方法:
1. 确保ACC游戏正在运行
2. 运行此脚本
3. 在浏览器中访问显示的地址
4. 在手机浏览器中访问局域网地址
"""

import os
import socket
import sys
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_telemetry.core.telemetry import ACCTelemetry
from acc_telemetry.web import WebTelemetryServer


def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def check_acc_connection():
    """检查ACC游戏连接状态"""
    try:
        telemetry = ACCTelemetry()
        data = telemetry.get_telemetry()
        return data is not None
    except Exception:
        return False


def main():
    print("=" * 70)
    print("🏎️  ACC 遥测 Web 面板示例")
    print("=" * 70)

    # 检查ACC连接
    print("🔍 检查ACC游戏连接...")
    if check_acc_connection():
        print("✅ ACC游戏已连接，遥测数据可用")
    else:
        print("⚠️  警告: 未检测到ACC游戏或遥测数据不可用")
        print("   请确保:")
        print("   1. ACC游戏正在运行")
        print("   2. 游戏中启用了遥测功能")
        print("   3. 正在进行比赛或练习")
        print("")
        response = input("是否继续启动Web服务器? (y/n): ")
        if response.lower() != "y":
            print("已取消启动")
            return

    print("")

    # 配置服务器参数
    host = "0.0.0.0"  # 监听所有网络接口
    port = 8080
    local_ip = get_local_ip()

    print("🌐 Web服务器配置:")
    print(f"   服务器地址: {host}:{port}")
    print(f"   本机访问:   http://localhost:{port}")
    print(f"   局域网访问: http://{local_ip}:{port}")
    print("")

    print("📱 移动设备访问指南:")
    print("   1. 确保设备与电脑在同一WiFi网络")
    print(f"   2. 在移动设备浏览器中输入: http://{local_ip}:{port}")
    print("   3. 建议使用横屏模式以获得最佳体验")
    print("")

    print("🎛️  仪表盘功能:")
    print("   - 实时显示车辆速度、转速、档位等基础数据")
    print("   - 监控轮胎压力和温度")
    print("   - 显示刹车温度和引擎数据")
    print("   - 车辆动态数据(G力、转向角度等)")
    print("   - 圈速和辅助系统状态")
    print("")

    print("⚠️  注意事项:")
    print("   - 确保防火墙允许端口访问")
    print("   - 数据更新频率约60fps")
    print("   - 按 Ctrl+C 停止服务器")
    print("=" * 70)
    print("")

    # 创建并启动Web服务器
    try:
        print("🚀 正在启动Web遥测服务器...")
        server = WebTelemetryServer(host=host, port=port)

        # 在单独线程中启动服务器，以便可以添加额外功能
        def start_server():
            server.start()

        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()

        print(f"✅ 服务器已启动! 请在浏览器中访问: http://localhost:{port}")
        print(f"📱 手机访问地址: http://{local_ip}:{port}")
        print("")
        print("💡 提示: 打开浏览器后，您应该能看到实时更新的遥测数据")
        print("")

        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止服务器...")
            server.stop()
            print("✅ 服务器已停止")

    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        print("\n🔧 可能的解决方案:")
        print(f"   1. 检查端口 {port} 是否被占用")
        print("   2. 尝试以管理员权限运行")
        print("   3. 检查防火墙设置")
        print("   4. 尝试使用其他端口")

        # 提供端口更改选项
        try:
            new_port = input(f"\n是否尝试使用其他端口? 输入新端口号 (当前: {port}): ")
            if new_port.isdigit():
                port = int(new_port)
                print(f"\n🔄 尝试使用端口 {port}...")
                server = WebTelemetryServer(host=host, port=port)
                server.start()
        except KeyboardInterrupt:
            print("\n已取消")
        except Exception as e2:
            print(f"❌ 仍然失败: {e2}")


if __name__ == "__main__":
    main()
