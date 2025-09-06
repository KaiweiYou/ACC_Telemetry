#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的ACC_Telemetry使用示例

展示最佳实践和错误处理
"""

import logging
import os
import sys
import time
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_telemetry.config import ADVANCED_CONFIG, DASHBOARD_CONFIG, OSC_CONFIG
from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TelemetryMonitor:
    """遥测数据监控器

    提供数据读取、验证和处理的完整解决方案
    """

    def __init__(self):
        self.telemetry: Optional[ACCTelemetry] = None
        self.running = False
        self.data_count = 0
        self.error_count = 0

    def start(self) -> bool:
        """启动监控器"""
        try:
            logger.info("正在启动ACC遥测监控器...")
            self.telemetry = ACCTelemetry()
            self.running = True
            logger.info("遥测监控器启动成功")
            return True
        except Exception as e:
            logger.error(f"启动监控器失败: {e}")
            return False

    def stop(self):
        """停止监控器"""
        self.running = False
        if self.telemetry:
            self.telemetry.close()
            self.telemetry = None
        logger.info("遥测监控器已停止")

    def validate_data(self, data: TelemetryData) -> bool:
        """验证遥测数据的合理性"""
        try:
            # 基础数据验证
            if not (0 <= data.speed <= 500):
                logger.warning(f"异常速度值: {data.speed}")
                return False

            if not (0 <= data.rpm <= 20000):
                logger.warning(f"异常转速值: {data.rpm}")
                return False

            if not (-1 <= data.gear <= 8):
                logger.warning(f"异常档位值: {data.gear}")
                return False

            # 踏板数据验证
            for pedal_name, value in [
                ("throttle", data.throttle),
                ("brake", data.brake),
                ("clutch", data.clutch),
            ]:
                if not (0 <= value <= 1):
                    logger.warning(f"异常{pedal_name}值: {value}")
                    return False

            # 轮胎压力验证
            tire_pressures = [
                data.tire_pressure_fl,
                data.tire_pressure_fr,
                data.tire_pressure_rl,
                data.tire_pressure_rr,
            ]
            for i, pressure in enumerate(tire_pressures):
                if not (0 <= pressure <= 50):
                    logger.warning(f"异常轮胎压力值 (轮胎{i+1}): {pressure}")
                    return False

            return True
        except Exception as e:
            logger.error(f"数据验证时发生错误: {e}")
            return False

    def process_data(self, data: TelemetryData):
        """处理遥测数据"""
        # 这里可以添加自定义的数据处理逻辑
        # 例如：数据记录、分析、转发等

        # 示例：检测急刹车
        if data.brake > 0.8:
            logger.info(f"检测到急刹车: {data.brake*100:.1f}%")

        # 示例：检测高转速
        if data.rpm > 8000:
            logger.info(f"高转速警告: {data.rpm} RPM")

        # 示例：检测轮胎压力异常
        avg_pressure = (
            data.tire_pressure_fl
            + data.tire_pressure_fr
            + data.tire_pressure_rl
            + data.tire_pressure_rr
        ) / 4
        if avg_pressure < 2.0:
            logger.warning(f"轮胎压力偏低: 平均 {avg_pressure:.2f} PSI")

    def run_monitoring(self, duration: int = 60):
        """运行监控循环

        Args:
            duration: 监控持续时间（秒），0表示无限循环
        """
        if not self.start():
            return

        start_time = time.time()
        logger.info(f"开始监控，持续时间: {duration}秒 (0=无限)")

        try:
            while self.running:
                try:
                    # 读取数据
                    data = self.telemetry.get_telemetry()

                    if data is not None:
                        self.data_count += 1

                        # 验证数据
                        if self.validate_data(data):
                            # 处理数据
                            self.process_data(data)

                            # 每100次数据显示一次统计
                            if self.data_count % 100 == 0:
                                logger.info(
                                    f"已处理 {self.data_count} 条数据，错误: {self.error_count}"
                                )
                        else:
                            self.error_count += 1

                    # 检查是否超时
                    if duration > 0 and (time.time() - start_time) > duration:
                        logger.info("监控时间到达，正在停止...")
                        break

                    # 控制更新频率
                    time.sleep(1.0 / DASHBOARD_CONFIG["update_rate"])

                except KeyboardInterrupt:
                    logger.info("用户中断监控")
                    break
                except Exception as e:
                    logger.error(f"监控循环中发生错误: {e}")
                    self.error_count += 1
                    time.sleep(1)  # 错误后暂停1秒

        finally:
            self.stop()
            logger.info(
                f"监控结束 - 总数据: {self.data_count}, 错误: {self.error_count}"
            )


def demo_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")

    # 使用上下文管理器确保资源正确释放
    try:
        with ACCTelemetry() as telemetry:
            print("成功连接到ACC共享内存")

            # 读取几次数据
            for i in range(5):
                data = telemetry.get_telemetry()
                if data:
                    print(
                        f"数据 {i+1}: 速度={data.speed:.1f} km/h, "
                        f"转速={data.rpm} RPM, 档位={data.gear}"
                    )
                else:
                    print(f"数据 {i+1}: 无数据 (请确保ACC游戏正在运行)")
                time.sleep(0.5)

    except RuntimeError as e:
        print(f"连接失败: {e}")
        print("请确保ACC游戏正在运行")


def demo_advanced_monitoring():
    """高级监控示例"""
    print("\n=== 高级监控示例 ===")

    monitor = TelemetryMonitor()

    try:
        # 运行30秒监控
        monitor.run_monitoring(duration=30)
    except KeyboardInterrupt:
        print("监控被用户中断")
    except Exception as e:
        print(f"监控过程中发生错误: {e}")


def demo_config_usage():
    """配置使用示例"""
    print("\n=== 配置使用示例 ===")

    print("当前配置:")
    print(f"OSC目标: {OSC_CONFIG['ip']}:{OSC_CONFIG['port']}")
    print(f"OSC更新频率: {OSC_CONFIG['update_rate']} Hz")
    print(f"仪表盘更新频率: {DASHBOARD_CONFIG['update_rate']} Hz")
    print(f"仪表盘尺寸: {DASHBOARD_CONFIG['width']}x{DASHBOARD_CONFIG['height']}")
    print(f"调试模式: {ADVANCED_CONFIG['debug_mode']}")
    print(f"超时时间: {ADVANCED_CONFIG['timeout']} 秒")


if __name__ == "__main__":
    print("ACC_Telemetry 改进使用示例")
    print("=" * 50)

    # 显示配置信息
    demo_config_usage()

    # 基础使用示例
    demo_basic_usage()

    # 询问是否运行高级监控
    try:
        response = input("\n是否运行高级监控示例? (y/N): ").strip().lower()
        if response in ["y", "yes"]:
            demo_advanced_monitoring()
        else:
            print("跳过高级监控示例")
    except KeyboardInterrupt:
        print("\n程序被用户中断")

    print("\n示例程序结束")
