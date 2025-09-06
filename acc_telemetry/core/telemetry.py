# -*- coding: utf-8 -*-
import logging
import time
from dataclasses import dataclass
from typing import Optional

from .shared_memory import accSharedMemory

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class TelemetryData:
    """遥测数据类

    包含从ACC游戏中读取的所有遥测数据
    """

    timestamp: float  # 数据时间戳

    # 基础数据
    speed: float
    rpm: int
    gear: int
    fuel: float

    # 踏板数据
    throttle: float  # 油门踏板位置 0-1
    brake: float  # 刹车踏板位置 0-1
    clutch: float  # 离合器踏板位置 0-1

    # 轮胎压力
    tire_pressure_fl: float
    tire_pressure_fr: float
    tire_pressure_rl: float
    tire_pressure_rr: float

    # 轮胎温度
    tire_temp_fl: float
    tire_temp_fr: float
    tire_temp_rl: float
    tire_temp_rr: float

    # 刹车温度
    brake_temp_fl: float
    brake_temp_fr: float
    brake_temp_rl: float
    brake_temp_rr: float

    # 悬挂数据
    suspension_travel_fl: float
    suspension_travel_fr: float
    suspension_travel_rl: float
    suspension_travel_rr: float

    # 车辆动态
    acceleration_x: float  # 横向G力
    acceleration_y: float  # 纵向G力
    acceleration_z: float  # 垂直G力

    # 转向数据
    steer_angle: float

    # 引擎数据
    engine_temp: float
    turbo_boost: float

    # 位置和速度
    velocity_x: float
    velocity_y: float
    velocity_z: float

    # 车轮滑移
    wheel_slip_fl: float
    wheel_slip_fr: float
    wheel_slip_rl: float
    wheel_slip_rr: float

    # DRS和其他
    drs: int  # DRS状态
    tc: int  # 牵引力控制
    abs: int  # ABS状态

    # 圈速数据
    lap_time: int
    last_lap: int
    best_lap: int


class ACCTelemetry:
    """ACC遥测数据读取器

    用于从ACC游戏的共享内存中读取实时遥测数据
    """

    def __init__(self):
        """初始化遥测数据读取器"""
        self.asm = None
        self._connected = False
        self._last_data = None
        self._last_read_time = 0
        self._min_update_interval = 0.05  # 最小更新间隔50ms
        self._last_connect_attempt = 0

    def connect(self) -> bool:
        """连接到ACC共享内存（带超时保护）

        Returns:
            bool: 连接是否成功
        """
        try:
            # 快速连接尝试，避免长时间阻塞
            import threading
            
            result = [None]
            def _connect():
                try:
                    self.asm = accSharedMemory()
                    result[0] = True
                except Exception as e:
                    logger.debug(f"连接尝试失败: {e}")
                    result[0] = False
            
            # 使用线程避免阻塞
            connect_thread = threading.Thread(target=_connect)
            connect_thread.daemon = True
            connect_thread.start()
            connect_thread.join(timeout=0.5)  # 最多等待500ms
            
            if result[0] is True:
                self._connected = True
                logger.info("已连接到ACC共享内存")
                return True
            else:
                self._connected = False
                return False
                
        except Exception as e:
            logger.error(f"无法连接到ACC共享内存: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """断开共享内存连接"""
        try:
            if self.asm:
                self.asm.close()
            self._connected = False
            logger.info("已断开ACC共享内存连接")
        except Exception as e:
            logger.error(f"断开连接时发生错误: {e}")

    def is_connected(self) -> bool:
        """检查是否已连接到共享内存

        Returns:
            bool: 连接状态
        """
        return self._connected and self.asm is not None

    def read_data(self) -> Optional[TelemetryData]:
        """读取遥测数据（带缓存和限流）

        Returns:
            Optional[TelemetryData]: 遥测数据对象，如果无数据则返回None
        """
        current_time = time.time()
        
        # 检查更新间隔，避免过于频繁的读取
        if current_time - self._last_read_time < self._min_update_interval:
            return self._last_data
            
        self._last_read_time = current_time
        
        if not self.is_connected():
            # 只在必要时尝试连接，避免频繁重试
            if current_time - self._last_connect_attempt > 5:
                self._last_connect_attempt = current_time
                if not self.connect():
                    return self._last_data
            return self._last_data
            
        data = self.get_telemetry()
        if data is not None:
            self._last_data = data
            
        return self._last_data

    def get_telemetry(self) -> Optional[TelemetryData]:
        """读取并返回遥测数据（优化版本，带超时保护）

        Returns:
            Optional[TelemetryData]: 遥测数据对象，如果无数据则返回None
        """
        if not self.is_connected():
            return None

        try:
            # 使用线程池避免阻塞主线程
            import threading
            
            result = [None]
            def _read_telemetry():
                try:
                    sm = self.asm.read_shared_memory()
                    if sm is not None:
                        telemetry = TelemetryData(
                            timestamp=time.time(),
                            # 基础数据
                            speed=sm.Physics.speed_kmh,
                            rpm=sm.Physics.rpm,
                            gear=sm.Physics.gear,
                            fuel=sm.Physics.fuel,
                            # 踏板数据
                            throttle=sm.Physics.gas,
                            brake=sm.Physics.brake,
                            clutch=sm.Physics.clutch,
                            # 轮胎压力
                            tire_pressure_fl=sm.Physics.wheel_pressure.front_left,
                            tire_pressure_fr=sm.Physics.wheel_pressure.front_right,
                            tire_pressure_rl=sm.Physics.wheel_pressure.rear_left,
                            tire_pressure_rr=sm.Physics.wheel_pressure.rear_right,
                            # 轮胎温度
                            tire_temp_fl=sm.Physics.tyre_core_temp.front_left,
                            tire_temp_fr=sm.Physics.tyre_core_temp.front_right,
                            tire_temp_rl=sm.Physics.tyre_core_temp.rear_left,
                            tire_temp_rr=sm.Physics.tyre_core_temp.rear_right,
                            # 刹车温度
                            brake_temp_fl=sm.Physics.brake_temp.front_left,
                            brake_temp_fr=sm.Physics.brake_temp.front_right,
                            brake_temp_rl=sm.Physics.brake_temp.rear_left,
                            brake_temp_rr=sm.Physics.brake_temp.rear_right,
                            # 悬挂数据
                            suspension_travel_fl=sm.Physics.suspension_travel.front_left,
                            suspension_travel_fr=sm.Physics.suspension_travel.front_right,
                            suspension_travel_rl=sm.Physics.suspension_travel.rear_left,
                            suspension_travel_rr=sm.Physics.suspension_travel.rear_right,
                            # 车辆动态
                            acceleration_x=sm.Physics.g_force.x,
                            acceleration_y=sm.Physics.g_force.y,
                            acceleration_z=sm.Physics.g_force.z,
                            # 转向数据
                            steer_angle=sm.Physics.steer_angle,
                            # 引擎数据
                            engine_temp=sm.Physics.water_temp,
                            turbo_boost=sm.Physics.turbo_boost,
                            # 位置和速度
                            velocity_x=sm.Physics.velocity.x,
                            velocity_y=sm.Physics.velocity.y,
                            velocity_z=sm.Physics.velocity.z,
                            # 车轮滑移
                            wheel_slip_fl=sm.Physics.wheel_slip.front_left,
                            wheel_slip_fr=sm.Physics.wheel_slip.front_right,
                            wheel_slip_rl=sm.Physics.wheel_slip.rear_left,
                            wheel_slip_rr=sm.Physics.wheel_slip.rear_right,
                            # DRS和其他 (DRS在ACC中未使用，暂时设为0)
                            drs=0,
                            tc=sm.Physics.tc,
                            abs=sm.Physics.abs,
                            # 圈速数据
                            lap_time=sm.Graphics.current_time,
                            last_lap=sm.Graphics.last_time,
                            best_lap=sm.Graphics.best_time,
                        )
                        result[0] = telemetry
                    else:
                        result[0] = None
                except Exception as e:
                    logger.debug(f"读取共享内存失败: {e}")
                    result[0] = None
            
            # 启动读取线程
            read_thread = threading.Thread(target=_read_telemetry)
            read_thread.daemon = True
            read_thread.start()
            read_thread.join(timeout=0.1)  # 最多等待100ms
            
            return result[0]
            
        except Exception as e:
            logger.error(f"读取遥测数据时发生错误: {e}")
            return None

    def close(self) -> None:
        """关闭共享内存连接"""
        try:
            self.asm.close()
            logger.info("ACC遥测连接已关闭")
        except Exception as e:
            logger.error(f"关闭遥测连接时发生错误: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


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
