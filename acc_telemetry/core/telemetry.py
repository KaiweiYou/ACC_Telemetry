from .shared_memory import accSharedMemory
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class TelemetryData:
    speed: float
    rpm: int
    gear: int
    fuel: float
    tire_pressure_fl: float
    tire_pressure_fr: float 
    tire_pressure_rl: float
    tire_pressure_rr: float
    # 新增踏板数据
    throttle: float  # 油门踏板位置 0-1
    brake: float    # 刹车踏板位置 0-1
    clutch: float   # 离合器踏板位置 0-1

class ACCTelemetry:
    def __init__(self):
        self.asm = accSharedMemory()
        
    def get_telemetry(self) -> Optional[TelemetryData]:
        """读取并返回遥测数据"""
        sm = self.asm.read_shared_memory()
        
        if sm is not None:
            return TelemetryData(
                speed=sm.Physics.speed_kmh,
                rpm=sm.Physics.rpm,
                gear=sm.Physics.gear,
                fuel=sm.Physics.fuel,
                tire_pressure_fl=sm.Physics.wheel_pressure.front_left,
                tire_pressure_fr=sm.Physics.wheel_pressure.front_right,
                tire_pressure_rl=sm.Physics.wheel_pressure.rear_left,
                tire_pressure_rr=sm.Physics.wheel_pressure.rear_right,
                # 新增踏板数据读取
                throttle=sm.Physics.gas,
                brake=sm.Physics.brake,
                clutch=sm.Physics.clutch
            )
        return None

    def close(self):
        self.asm.close()

def main():
    print("正在尝试连接 ACC 共享内存...")
    telemetry = ACCTelemetry()
    
    try:
        while True:
            data = telemetry.get_telemetry()
            
            if data is not None:
                print("\n--- ACC 遥测数据 ---")
                
                # 物理数据
                print("\n物理数据:")
                print(f"速度: {data.speed:.1f} km/h")
                print(f"转速: {data.rpm} RPM")
                print(f"档位: {data.gear}")
                print(f"剩余燃油: {data.fuel:.1f} L")
                
                # 踏板数据
                print("\n踏板状态:")
                print(f"油门: {data.throttle * 100:.0f}%")
                print(f"刹车: {data.brake * 100:.0f}%")
                print(f"离合: {data.clutch * 100:.0f}%")
                
                # 轮胎数据
                print("\n轮胎压力:")
                print(f"左前: {data.tire_pressure_fl:.1f} PSI")
                print(f"右前: {data.tire_pressure_fr:.1f} PSI")
                print(f"左后: {data.tire_pressure_rl:.1f} PSI")
                print(f"右后: {data.tire_pressure_rr:.1f} PSI")
                
                time.sleep(1)  # 每秒更新一次数据
            else:
                print("\n等待 ACC 游戏运行中... (请确保游戏已启动)")
                time.sleep(2)
                
    except KeyboardInterrupt:
        print("\n程序已停止")
    finally:
        telemetry.close()
        print("已关闭共享内存连接")

if __name__ == "__main__":
    main()