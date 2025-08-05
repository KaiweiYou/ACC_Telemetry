#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry Arduino串口桥接程序

这个脚本用于将ACC遥测数据通过串口发送到Arduino，
以驱动物理仪表盘、LED指示灯或其他硬件设备。

硬件要求:
- Arduino Uno/Mega/Nano等，已上传arduino_integration_example.ino程序
- USB连接线

使用方法:
    python arduino_serial_bridge.py [COM端口] [波特率]

参数:
    COM端口 - Arduino的串口端口，例如COM3（Windows）或/dev/ttyACM0（Linux）
    波特率 - 串口通信波特率，默认为115200
"""

import sys
import time
import serial
import serial.tools.list_ports
import argparse

# 导入遥测模块
from acc_telemetry.core.telemetry import ACCTelemetry

# 方法2：如果已安装为包，可以使用以下导入方式
# from acc_telemetry.core.telemetry import ACCTelemetry

class ArduinoSerialBridge:
    def __init__(self, port=None, baudrate=115200):
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()
        
        # 如果没有指定端口，尝试自动检测Arduino
        if port is None:
            port = self.find_arduino_port()
            if port is None:
                raise ValueError("无法自动检测Arduino端口，请手动指定")
        
        # 初始化串口连接
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # 等待Arduino重置
        
        # 清空缓冲区
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        
        print(f"已连接到Arduino: {port} (波特率: {baudrate})")
        
        # 等待Arduino就绪
        self.wait_for_arduino()
    
    def find_arduino_port(self):
        """尝试自动检测Arduino的串口端口"""
        print("正在自动检测Arduino端口...")
        ports = list(serial.tools.list_ports.comports())
        
        for port in ports:
            # 在Windows上，Arduino通常显示为"Arduino Uno"或包含"CH340"等
            # 在Linux上，通常是/dev/ttyACM0或/dev/ttyUSB0
            if "Arduino" in port.description or "CH340" in port.description or \
               "ACM" in port.device or "USB" in port.device:
                print(f"找到可能的Arduino设备: {port.device} ({port.description})")
                return port.device
        
        # 如果没有找到明确的Arduino设备，列出所有可用端口
        if ports:
            print("未找到明确的Arduino设备，以下是所有可用端口:")
            for i, port in enumerate(ports):
                print(f"  {i+1}. {port.device} - {port.description}")
            
            # 如果只有一个端口，假设它是Arduino
            if len(ports) == 1:
                print(f"只有一个可用端口，假设它是Arduino: {ports[0].device}")
                return ports[0].device
        else:
            print("未检测到任何串口设备")
        
        return None
    
    def wait_for_arduino(self):
        """等待Arduino发送就绪消息"""
        print("等待Arduino就绪...")
        timeout = time.time() + 10  # 10秒超时
        
        while time.time() < timeout:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                print(f"Arduino: {line}")
                if "ready" in line.lower():
                    print("Arduino已就绪")
                    return True
            time.sleep(0.1)
        
        print("警告: Arduino未发送就绪消息，继续执行")
        return False
    
    def send_telemetry(self, data):
        """将遥测数据发送到Arduino"""
        if data is None:
            return False
        
        # 构建命令字符串
        # 格式: "S:123.4,R:5678,G:2,T:0.75,B:0.25"
        command = f"S:{data.speed:.1f},R:{data.rpm},G:{data.gear},"
        command += f"T:{data.throttle:.2f},B:{data.brake:.2f}\n"
        
        # 发送命令
        self.serial.write(command.encode('utf-8'))
        
        # 读取响应（非阻塞）
        self.read_response()
        
        return True
    
    def read_response(self):
        """读取Arduino的响应（非阻塞）"""
        if self.serial.in_waiting > 0:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                if line.startswith("ACK:"):
                    # 确认消息，不需要打印
                    pass
                else:
                    print(f"Arduino: {line}")
            except Exception as e:
                print(f"读取Arduino响应时出错: {e}")
    
    def run(self, update_rate=20):
        """运行桥接程序
        
        参数:
            update_rate - 每秒更新次数
        """
        # 计算更新间隔
        update_interval = 1.0 / update_rate
        
        # 连接状态
        connected = False
        retry_count = 0
        
        try:
            print(f"开始发送数据到Arduino，更新率: {update_rate}Hz")
            print("按 Ctrl+C 停止")
            
            while True:
                # 获取遥测数据
                data = self.telemetry.get_telemetry()
                
                # 发送数据
                if data is not None:
                    success = self.send_telemetry(data)
                    
                    # 更新连接状态
                    if success and not connected:
                        connected = True
                        retry_count = 0
                        print("已连接到ACC游戏，正在发送数据...")
                    
                    # 短暂延迟
                    time.sleep(update_interval)
                else:
                    if connected:
                        connected = False
                        print("与ACC游戏的连接已断开，等待重新连接...")
                    else:
                        retry_count += 1
                        if retry_count % 20 == 0:  # 每20次重试显示一次消息
                            print(f"等待ACC游戏运行中... (尝试次数: {retry_count})")
                    
                    # 等待时间稍长一些
                    time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n程序已被用户中断")
        except Exception as e:
            print(f"\n发生错误: {e}")
        finally:
            # 关闭连接
            self.telemetry.close()
            self.serial.close()
            print("已关闭所有连接")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="ACC遥测数据Arduino串口桥接程序")
    parser.add_argument(
        "port",
        nargs="?",
        help="Arduino的串口端口，例如COM3（Windows）或/dev/ttyACM0（Linux）"
    )
    parser.add_argument(
        "--baudrate", "-b",
        type=int,
        default=115200,
        help="串口通信波特率，默认为115200"
    )
    parser.add_argument(
        "--rate", "-r",
        type=int,
        default=20,
        help="数据更新频率（Hz），默认为20"
    )
    
    args = parser.parse_args()
    
    try:
        # 创建并运行桥接程序
        bridge = ArduinoSerialBridge(args.port, args.baudrate)
        bridge.run(args.rate)
    except ValueError as e:
        print(f"错误: {e}")
        available_ports = list(serial.tools.list_ports.comports())
        if available_ports:
            print("\n可用的串口端口:")
            for port in available_ports:
                print(f"  {port.device} - {port.description}")
            print("\n请使用以上端口之一重新运行程序，例如:")
            print(f"  python {sys.argv[0]} {available_ports[0].device}")
        else:
            print("未检测到任何串口设备，请确保Arduino已正确连接")

if __name__ == "__main__":
    main()