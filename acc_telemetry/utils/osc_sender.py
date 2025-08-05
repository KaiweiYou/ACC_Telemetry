from pythonosc.udp_client import SimpleUDPClient
from ..core.telemetry import ACCTelemetry
import time
import sys

# 导入配置
from ..config import OSC_CONFIG, ADVANCED_CONFIG

class ACCDataSender:
    def __init__(self, ip=None, port=None):
        # 使用配置文件中的值或默认值
        self.ip = ip if ip is not None else OSC_CONFIG['ip']
        self.port = port if port is not None else OSC_CONFIG['port']
        self.update_rate = OSC_CONFIG['update_rate']
        self.debug_mode = ADVANCED_CONFIG['debug_mode']
        
        # 创建 OSC 客户端
        self.client = SimpleUDPClient(self.ip, self.port)
        
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()
        
        if self.debug_mode:
            print(f"OSC客户端已初始化，目标: {self.ip}:{self.port}")
            print(f"更新频率: {self.update_rate}Hz")
        
    def send_data(self):
        """读取并发送遥测数据"""
        data = self.telemetry.get_telemetry()
        
        if data is not None:
            try:
                # 发送时间戳
                self.client.send_message("/acc/timestamp", float(data.timestamp))
                
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
                
                # 发送组合数据（便于一次性接收所有数据）
                self.client.send_message("/acc/all", [
                    float(data.timestamp),
                    float(data.speed),
                    int(data.rpm),
                    int(data.gear),
                    float(data.fuel),
                    float(data.throttle),
                    float(data.brake),
                    float(data.clutch),
                    float(data.tire_pressure_fl),
                    float(data.tire_pressure_fr),
                    float(data.tire_pressure_rl),
                    float(data.tire_pressure_rr)
                ])
                
                return True
            except Exception as e:
                if self.debug_mode:
                    print(f"发送数据错误: {e}")
                return False
        return False

    def run(self):
        """运行数据发送循环"""
        # 计算更新间隔
        update_interval = 1.0 / self.update_rate
        
        # 连接计数器
        connected = False
        retry_count = 0
        
        try:
            print(f"开始发送数据到 {self.ip}:{self.port}...")
            print(f"按 Ctrl+C 停止发送")
            
            while True:
                # 发送数据
                success = self.send_data()
                
                # 更新连接状态
                if success and not connected:
                    connected = True
                    retry_count = 0
                    print("已连接到 ACC 游戏，正在发送数据...")
                elif not success and connected:
                    connected = False
                    print("与 ACC 游戏的连接已断开，等待重新连接...")
                elif not success and not connected:
                    retry_count += 1
                    if retry_count % 10 == 0:  # 每10次重试显示一次消息
                        print(f"等待 ACC 游戏运行中... (尝试次数: {retry_count})")
                
                # 根据配置的更新频率发送数据
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n停止发送数据")
        except Exception as e:
            print(f"\n发生错误: {e}")
        finally:
            self.telemetry.close()
            print("已关闭连接")

def print_usage():
    """打印使用说明"""
    print("\nACC OSC数据发送器")
    print("用法: python osc_sender.py [ip] [port]")
    print("  ip   - 目标IP地址 (默认: 配置文件中的设置)")
    print("  port - 目标端口 (默认: 配置文件中的设置)")
    print("\n示例:")
    print("  python osc_sender.py                  # 使用配置文件中的设置")
    print("  python osc_sender.py 127.0.0.1        # 发送到本地，使用配置文件中的端口")
    print("  python osc_sender.py 192.168.1.100 9000 # 发送到指定IP和端口")

if __name__ == "__main__":
    # 解析命令行参数
    ip = None
    port = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print_usage()
            sys.exit(0)
        ip = sys.argv[1]
        
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"错误: 端口必须是一个整数")
            print_usage()
            sys.exit(1)
    
    # 创建发送器实例
    sender = ACCDataSender(ip, port)
    
    # 运行发送循环
    sender.run()
