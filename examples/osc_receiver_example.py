#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry OSC接收器示例

这个示例展示了如何使用python-osc库接收从ACC_Telemetry发送的OSC数据。
运行此示例前，请确保已启动ACC游戏和ACC_Telemetry的OSC发送器。

使用方法:
    python osc_receiver_example.py [port]

参数:
    port - 监听的端口号，默认为8000
"""

import argparse
import time

from pythonosc import dispatcher as osc_dispatcher
from pythonosc import osc_server

# 存储最新的遥测数据
telemetry_data = {
    "timestamp": 0,
    "speed": 0,
    "rpm": 0,
    "gear": 0,
    "fuel": 0,
    "throttle": 0,
    "brake": 0,
    "clutch": 0,
    "tire_fl": 0,
    "tire_fr": 0,
    "tire_rl": 0,
    "tire_rr": 0,
}


# 处理所有数据的回调函数
def handle_all(unused_addr, *args):
    """处理/acc/all消息，包含所有遥测数据"""
    if len(args) >= 12:
        telemetry_data["timestamp"] = args[0]
        telemetry_data["speed"] = args[1]
        telemetry_data["rpm"] = args[2]
        telemetry_data["gear"] = args[3]
        telemetry_data["fuel"] = args[4]
        telemetry_data["throttle"] = args[5]
        telemetry_data["brake"] = args[6]
        telemetry_data["clutch"] = args[7]
        telemetry_data["tire_fl"] = args[8]
        telemetry_data["tire_fr"] = args[9]
        telemetry_data["tire_rl"] = args[10]
        telemetry_data["tire_rr"] = args[11]
        print_telemetry()


# 处理单个数据的回调函数
def handle_speed(unused_addr, args):
    telemetry_data["speed"] = args


def handle_rpm(unused_addr, args):
    telemetry_data["rpm"] = args


def handle_gear(unused_addr, args):
    telemetry_data["gear"] = args


def handle_fuel(unused_addr, args):
    telemetry_data["fuel"] = args


def handle_throttle(unused_addr, args):
    telemetry_data["throttle"] = args


def handle_brake(unused_addr, args):
    telemetry_data["brake"] = args


def handle_clutch(unused_addr, args):
    telemetry_data["clutch"] = args


def handle_tire_fl(unused_addr, args):
    telemetry_data["tire_fl"] = args


def handle_tire_fr(unused_addr, args):
    telemetry_data["tire_fr"] = args


def handle_tire_rl(unused_addr, args):
    telemetry_data["tire_rl"] = args


def handle_tire_rr(unused_addr, args):
    telemetry_data["tire_rr"] = args


def handle_timestamp(unused_addr, args):
    telemetry_data["timestamp"] = args


# 打印遥测数据
def print_telemetry():
    """打印当前遥测数据"""
    # 清屏 (Windows)
    print("\033[H\033[J", end="")

    print("===== ACC 遥测数据 =====")
    print(f"时间戳: {telemetry_data['timestamp']:.3f}")
    print(f"速度: {telemetry_data['speed']:.1f} km/h")
    print(f"转速: {telemetry_data['rpm']} RPM")

    # 处理档位显示
    gear = telemetry_data["gear"]
    if gear == 0:
        gear_display = "N"
    elif gear == -1:
        gear_display = "R"
    else:
        gear_display = str(gear)
    print(f"档位: {gear_display}")

    print(f"燃油: {telemetry_data['fuel']:.1f} L")
    print("\n--- 踏板状态 ---")
    print(f"油门: {telemetry_data['throttle']*100:.1f}%")
    print(f"刹车: {telemetry_data['brake']*100:.1f}%")
    print(f"离合: {telemetry_data['clutch']*100:.1f}%")
    print("\n--- 轮胎压力 (PSI) ---")
    print(
        f"左前: {telemetry_data['tire_fl']:.1f}  右前: {telemetry_data['tire_fr']:.1f}"
    )
    print(
        f"左后: {telemetry_data['tire_rl']:.1f}  右后: {telemetry_data['tire_rr']:.1f}"
    )
    print("\n按 Ctrl+C 退出")


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="ACC遥测数据OSC接收器示例")
    parser.add_argument("--port", type=int, default=8000, help="监听的端口号")
    parser.add_argument("--ip", default="0.0.0.0", help="监听的IP地址")
    args = parser.parse_args()

    # 设置OSC调度器
    disp = osc_dispatcher.Dispatcher()

    # 注册回调函数
    disp.map("/acc/all", handle_all)
    disp.map("/acc/speed", handle_speed)
    disp.map("/acc/rpm", handle_rpm)
    disp.map("/acc/gear", handle_gear)
    disp.map("/acc/fuel", handle_fuel)
    disp.map("/acc/pedals/throttle", handle_throttle)
    disp.map("/acc/pedals/brake", handle_brake)
    disp.map("/acc/pedals/clutch", handle_clutch)
    disp.map("/acc/tires/fl", handle_tire_fl)
    disp.map("/acc/tires/fr", handle_tire_fr)
    disp.map("/acc/tires/rl", handle_tire_rl)
    disp.map("/acc/tires/rr", handle_tire_rr)
    disp.map("/acc/timestamp", handle_timestamp)

    # 启动OSC服务器
    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), disp)

    print(f"启动OSC接收器，监听 {args.ip}:{args.port}")
    print("等待接收数据...")
    print("按 Ctrl+C 退出")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n接收器已停止")


if __name__ == "__main__":
    main()
