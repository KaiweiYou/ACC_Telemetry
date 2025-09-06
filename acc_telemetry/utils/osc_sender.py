# -*- coding: utf-8 -*-
import time

from pythonosc.udp_client import SimpleUDPClient

from ..core.telemetry import ACCTelemetry


class ACCDataSender:
    def __init__(self, ip="192.168.10.66", port=8000):
        # 创建 OSC 客户端
        self.client = SimpleUDPClient(ip, port)
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()

    def send_data(self):
        """读取并发送遥测数据"""
        data = self.telemetry.get_telemetry()

        if data is not None:
            # 发送基础数据
            self.client.send_message("/acc/speed", float(data.speed))
            self.client.send_message("/acc/rpm", int(data.rpm))
            self.client.send_message("/acc/gear", int(data.gear))
            self.client.send_message("/acc/fuel", float(data.fuel))

            # 发送踏板数据
            self.client.send_message("/acc/pedals/throttle", float(data.throttle))
            self.client.send_message("/acc/pedals/brake", float(data.brake))
            self.client.send_message("/acc/pedals/clutch", float(data.clutch))

            # 发送轮胎压力数据
            self.client.send_message("/acc/tires/fl", float(data.tire_pressure_fl))
            self.client.send_message("/acc/tires/fr", float(data.tire_pressure_fr))
            self.client.send_message("/acc/tires/rl", float(data.tire_pressure_rl))
            self.client.send_message("/acc/tires/rr", float(data.tire_pressure_rr))

    def run(self):
        """运行数据发送循环"""
        try:
            print(f"开始发送数据...")
            while True:
                self.send_data()
                # 以60fps的频率发送数据
                time.sleep(1 / 60)
        except KeyboardInterrupt:
            print("\n停止发送数据")
        finally:
            self.telemetry.close()


if __name__ == "__main__":
    # 创建发送器实例（默认发送到192.168.10.66:8000）
    sender = ACCDataSender()
    # 运行发送循环
    sender.run()
