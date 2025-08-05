#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC 遥测 Web 面板服务器

这个脚本启动一个Web服务器，允许通过浏览器访问ACC遥测数据。
局域网内的任何设备都可以通过访问 http://[服务器IP]:8080 来查看实时遥测数据。

使用方法:
1. 确保ACC游戏正在运行
2. 运行此脚本: python web_telemetry_server.py
3. 在浏览器中访问显示的地址
4. 在手机或其他设备上访问 http://[您的IP地址]:8080
"""

import sys
import os
import socket
import argparse
from acc_telemetry.web import WebTelemetryServer

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 连接到一个远程地址来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    parser = argparse.ArgumentParser(description='ACC 遥测 Web 面板服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器绑定地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口 (默认: 8080)')
    
    args = parser.parse_args()
    
    # 获取本机IP地址
    local_ip = get_local_ip()
    
    print("="*60)
    print("🏎️  ACC 遥测 Web 面板服务器")
    print("="*60)
    print(f"服务器启动地址: http://{args.host}:{args.port}")
    print(f"本机访问地址:   http://localhost:{args.port}")
    print(f"局域网访问地址: http://{local_ip}:{args.port}")
    print("")
    print("📱 手机访问步骤:")
    print(f"   1. 确保手机和电脑在同一局域网")
    print(f"   2. 在手机浏览器中输入: http://{local_ip}:{args.port}")
    print("")
    print("⚠️  注意事项:")
    print("   - 确保ACC游戏正在运行")
    print("   - 确保防火墙允许端口访问")
    print("   - 按 Ctrl+C 停止服务器")
    print("="*60)
    print("")
    
    # 创建并启动服务器
    server = WebTelemetryServer(host=args.host, port=args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务器...")
        server.stop()
        print("✅ 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        print("\n可能的解决方案:")
        print(f"1. 检查端口 {args.port} 是否被占用")
        print("2. 尝试使用其他端口: python web_telemetry_server.py --port 8081")
        print("3. 检查防火墙设置")
        sys.exit(1)

if __name__ == '__main__':
    main()