from acc_telemetry.core.shared_memory import accSharedMemory
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time
import os
import json
import csv
from datetime import datetime

# 导入配置
from ..config import TERMINAL_CONFIG, LOGGING_CONFIG, ADVANCED_CONFIG

@dataclass
class TelemetryData:
    # 基础物理数据
    speed: float           # 速度 (km/h)
    rpm: int               # 发动机转速
    gear: int              # 档位
    fuel: float            # 剩余燃油 (L)
    
    # 轮胎数据
    tire_pressure_fl: float  # 左前轮胎压力 (PSI)
    tire_pressure_fr: float  # 右前轮胎压力 (PSI)
    tire_pressure_rl: float  # 左后轮胎压力 (PSI)
    tire_pressure_rr: float  # 右后轮胎压力 (PSI)
    
    # 踏板数据
    throttle: float  # 油门踏板位置 0-1
    brake: float     # 刹车踏板位置 0-1
    clutch: float    # 离合器踏板位置 0-1
    
    # 时间数据
    timestamp: float = 0.0  # 数据时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """将数据转换为字典格式"""
        return {
            'timestamp': self.timestamp,
            'speed': self.speed,
            'rpm': self.rpm,
            'gear': self.gear,
            'fuel': self.fuel,
            'tire_pressure_fl': self.tire_pressure_fl,
            'tire_pressure_fr': self.tire_pressure_fr,
            'tire_pressure_rl': self.tire_pressure_rl,
            'tire_pressure_rr': self.tire_pressure_rr,
            'throttle': self.throttle,
            'brake': self.brake,
            'clutch': self.clutch
        }

class ACCTelemetry:
    def __init__(self, timeout=None, retry_interval=None):
        # 使用配置文件中的值或默认值
        self.timeout = timeout if timeout is not None else ADVANCED_CONFIG['timeout']
        self.retry_interval = retry_interval if retry_interval is not None else ADVANCED_CONFIG['retry_interval']
        self.debug_mode = ADVANCED_CONFIG['debug_mode']
        
        # 初始化共享内存读取器
        self.asm = accSharedMemory()
        
        # 初始化数据记录器
        self.logger = None
        if LOGGING_CONFIG['enabled']:
            self.init_logger()
        
    def init_logger(self):
        """初始化数据记录器"""
        # 创建日志目录
        log_dir = LOGGING_CONFIG['log_dir']
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_format = LOGGING_CONFIG['log_format'].lower()
        filename = f"acc_telemetry_{timestamp}.{log_format}"
        self.log_path = os.path.join(log_dir, filename)
        
        # 初始化CSV文件头
        if log_format == 'csv':
            with open(self.log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'speed', 'rpm', 'gear', 'fuel',
                    'tire_pressure_fl', 'tire_pressure_fr', 'tire_pressure_rl', 'tire_pressure_rr',
                    'throttle', 'brake', 'clutch'
                ])
        
        self.logger = {
            'format': log_format,
            'last_log_time': 0,
            'log_interval': 1.0 / LOGGING_CONFIG['update_rate']
        }
        
        if self.debug_mode:
            print(f"数据记录已启用，日志文件: {self.log_path}")
    
    def log_data(self, data: TelemetryData):
        """记录遥测数据"""
        if not self.logger or not LOGGING_CONFIG['enabled']:
            return
            
        current_time = time.time()
        # 检查是否需要记录（基于配置的更新频率）
        if current_time - self.logger['last_log_time'] < self.logger['log_interval']:
            return
            
        self.logger['last_log_time'] = current_time
        
        # 根据配置的格式记录数据
        if self.logger['format'] == 'csv':
            with open(self.log_path, 'a', newline='') as f:
                writer = csv.writer(f)
                d = data.to_dict()
                writer.writerow([
                    d['timestamp'], d['speed'], d['rpm'], d['gear'], d['fuel'],
                    d['tire_pressure_fl'], d['tire_pressure_fr'], d['tire_pressure_rl'], d['tire_pressure_rr'],
                    d['throttle'], d['brake'], d['clutch']
                ])
        elif self.logger['format'] == 'json':
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(data.to_dict()) + '\n')
    
    def get_telemetry(self) -> Optional[TelemetryData]:
        """读取并返回遥测数据"""
        try:
            sm = self.asm.read_shared_memory()
            
            if sm is not None:
                data = TelemetryData(
                    speed=sm.Physics.speed_kmh,
                    rpm=sm.Physics.rpm,
                    gear=sm.Physics.gear,
                    fuel=sm.Physics.fuel,
                    tire_pressure_fl=sm.Physics.wheel_pressure.front_left,
                    tire_pressure_fr=sm.Physics.wheel_pressure.front_right,
                    tire_pressure_rl=sm.Physics.wheel_pressure.rear_left,
                    tire_pressure_rr=sm.Physics.wheel_pressure.rear_right,
                    throttle=sm.Physics.gas,
                    brake=sm.Physics.brake,
                    clutch=sm.Physics.clutch,
                    timestamp=time.time()
                )
                
                # 记录数据
                if LOGGING_CONFIG['enabled']:
                    self.log_data(data)
                    
                return data
        except Exception as e:
            if self.debug_mode:
                print(f"读取共享内存错误: {e}")
                
        return None

    def close(self):
        """关闭连接和资源"""
        self.asm.close()
        if self.debug_mode:
            print("已关闭共享内存连接")

def main():
    print("正在尝试连接 ACC 共享内存...")
    telemetry = ACCTelemetry()
    
    # 计算更新间隔
    update_interval = 1.0 / TERMINAL_CONFIG['update_rate']
    
    try:
        while True:
            data = telemetry.get_telemetry()
            
            if data is not None:
                print("\n--- ACC 遥测数据 ---")
                
                # 物理数据
                if TERMINAL_CONFIG['show_physics']:
                    print("\n物理数据:")
                    print(f"速度: {data.speed:.1f} km/h")
                    print(f"转速: {data.rpm} RPM")
                    print(f"档位: {data.gear}")
                    print(f"剩余燃油: {data.fuel:.1f} L")
                
                # 踏板数据
                if TERMINAL_CONFIG['show_pedals']:
                    print("\n踏板状态:")
                    print(f"油门: {data.throttle * 100:.0f}%")
                    print(f"刹车: {data.brake * 100:.0f}%")
                    print(f"离合: {data.clutch * 100:.0f}%")
                
                # 轮胎数据
                if TERMINAL_CONFIG['show_tires']:
                    print("\n轮胎压力:")
                    print(f"左前: {data.tire_pressure_fl:.1f} PSI")
                    print(f"右前: {data.tire_pressure_fr:.1f} PSI")
                    print(f"左后: {data.tire_pressure_rl:.1f} PSI")
                    print(f"右后: {data.tire_pressure_rr:.1f} PSI")
                
                time.sleep(update_interval)  # 根据配置的更新频率更新数据
            else:
                print("\n等待 ACC 游戏运行中... (请确保游戏已启动)")
                time.sleep(ADVANCED_CONFIG['retry_interval'])
                
    except KeyboardInterrupt:
        print("\n程序已停止")
    finally:
        telemetry.close()
        print("已关闭共享内存连接")

def telemetry_main():
    """遥测主函数，供外部调用"""
    main()

if __name__ == "__main__":
    main()