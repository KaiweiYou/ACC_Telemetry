#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的ACC_Telemetry测试脚本

包含更全面的测试用例和错误处理验证
"""

import os
import sys
import time
import unittest
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData


class TestACCTelemetry(unittest.TestCase):
    """ACC遥测系统测试类"""

    def setUp(self):
        """测试前准备"""
        self.telemetry = None

    def tearDown(self):
        """测试后清理"""
        if self.telemetry:
            try:
                self.telemetry.close()
            except:
                pass

    def test_telemetry_data_structure(self):
        """测试TelemetryData数据结构"""
        # 创建测试数据
        test_data = TelemetryData(
            timestamp=time.time(),
            speed=100.0,
            rpm=6000,
            gear=3,
            fuel=50.0,
            throttle=0.8,
            brake=0.0,
            clutch=0.0,
            tire_pressure_fl=2.5,
            tire_pressure_fr=2.5,
            tire_pressure_rl=2.4,
            tire_pressure_rr=2.4,
            tire_temp_fl=85.0,
            tire_temp_fr=85.0,
            tire_temp_rl=80.0,
            tire_temp_rr=80.0,
            brake_temp_fl=300.0,
            brake_temp_fr=300.0,
            brake_temp_rl=250.0,
            brake_temp_rr=250.0,
            suspension_travel_fl=0.1,
            suspension_travel_fr=0.1,
            suspension_travel_rl=0.15,
            suspension_travel_rr=0.15,
            acceleration_x=0.5,
            acceleration_y=-0.8,
            acceleration_z=0.0,
            steer_angle=15.0,
            engine_temp=90.0,
            turbo_boost=1.2,
            velocity_x=25.0,
            velocity_y=0.0,
            velocity_z=15.0,
            wheel_slip_fl=0.1,
            wheel_slip_fr=0.1,
            wheel_slip_rl=0.2,
            wheel_slip_rr=0.2,
            drs=0,
            tc=1,
            abs=1,
            lap_time=90000,
            last_lap=92000,
            best_lap=89500,
        )

        # 验证数据类型
        self.assertIsInstance(test_data, TelemetryData)
        self.assertIsInstance(test_data.timestamp, float)
        self.assertIsInstance(test_data.speed, float)
        self.assertIsInstance(test_data.rpm, int)
        self.assertIsInstance(test_data.gear, int)

        # 验证数据范围
        self.assertGreaterEqual(test_data.speed, 0)
        self.assertGreaterEqual(test_data.rpm, 0)
        self.assertGreaterEqual(test_data.throttle, 0)
        self.assertLessEqual(test_data.throttle, 1)
        self.assertGreaterEqual(test_data.brake, 0)
        self.assertLessEqual(test_data.brake, 1)

    @patch("acc_telemetry.core.telemetry.accSharedMemory")
    def test_telemetry_initialization_success(self, mock_shared_memory):
        """测试遥测系统成功初始化"""
        mock_shared_memory.return_value = Mock()

        try:
            telemetry = ACCTelemetry()
            self.assertIsNotNone(telemetry)
            self.assertIsNotNone(telemetry.asm)
        except Exception as e:
            self.fail(f"遥测系统初始化失败: {e}")

    @patch("acc_telemetry.core.telemetry.accSharedMemory")
    def test_telemetry_initialization_failure(self, mock_shared_memory):
        """测试遥测系统初始化失败处理"""
        mock_shared_memory.side_effect = Exception("共享内存连接失败")

        with self.assertRaises(RuntimeError) as context:
            ACCTelemetry()

        self.assertIn("无法初始化ACC共享内存连接", str(context.exception))

    def test_context_manager(self):
        """测试上下文管理器功能"""
        with patch("acc_telemetry.core.telemetry.accSharedMemory") as mock_sm:
            mock_instance = Mock()
            mock_sm.return_value = mock_instance

            with ACCTelemetry() as telemetry:
                self.assertIsNotNone(telemetry)

            # 验证close方法被调用
            mock_instance.close.assert_called_once()

    def test_config_values(self):
        """测试配置文件值"""
        # 验证OSC配置
        self.assertIn("ip", OSC_CONFIG)
        self.assertIn("port", OSC_CONFIG)
        self.assertIn("update_rate", OSC_CONFIG)

        # 验证端口范围
        self.assertGreater(OSC_CONFIG["port"], 0)
        self.assertLess(OSC_CONFIG["port"], 65536)

        # 验证更新频率
        self.assertGreater(OSC_CONFIG["update_rate"], 0)
        self.assertLessEqual(OSC_CONFIG["update_rate"], 120)

        # 验证仪表盘配置
        self.assertIn("update_rate", DASHBOARD_CONFIG)
        self.assertIn("width", DASHBOARD_CONFIG)
        self.assertIn("height", DASHBOARD_CONFIG)

        # 验证高级配置
        self.assertIn("debug_mode", ADVANCED_CONFIG)
        self.assertIn("timeout", ADVANCED_CONFIG)
        self.assertIn("retry_interval", ADVANCED_CONFIG)


class TestIntegration(unittest.TestCase):
    """集成测试类"""

    def test_import_all_modules(self):
        """测试所有模块导入"""
        try:
            from acc_telemetry import config
            from acc_telemetry.core import shared_memory, telemetry
            from acc_telemetry.ui import dashboard
            from acc_telemetry.utils import osc_sender
        except ImportError as e:
            self.fail(f"模块导入失败: {e}")

    def test_package_structure(self):
        """测试包结构完整性"""
        import acc_telemetry

        # 验证子包存在
        self.assertTrue(hasattr(acc_telemetry, "core"))
        self.assertTrue(hasattr(acc_telemetry, "ui"))
        self.assertTrue(hasattr(acc_telemetry, "utils"))


def run_performance_test():
    """性能测试"""
    print("\n=== 性能测试 ===")

    with patch("acc_telemetry.core.telemetry.accSharedMemory") as mock_sm:
        # 模拟共享内存数据
        mock_instance = Mock()
        mock_data = Mock()
        mock_data.Physics = Mock()
        mock_data.Graphics = Mock()

        # 设置模拟数据
        mock_data.Physics.speed_kmh = 100.0
        mock_data.Physics.rpm = 6000
        mock_data.Physics.gear = 3
        mock_data.Physics.fuel = 50.0
        mock_data.Physics.gas = 0.8
        mock_data.Physics.brake = 0.0
        mock_data.Physics.clutch = 0.0

        # 设置轮胎压力
        mock_data.Physics.wheel_pressure = Mock()
        mock_data.Physics.wheel_pressure.front_left = 2.5
        mock_data.Physics.wheel_pressure.front_right = 2.5
        mock_data.Physics.wheel_pressure.rear_left = 2.4
        mock_data.Physics.wheel_pressure.rear_right = 2.4

        # 设置其他必要的模拟数据
        for attr in [
            "tyre_core_temp",
            "brake_temp",
            "suspension_travel",
            "g_force",
            "velocity",
            "wheel_slip",
        ]:
            setattr(mock_data.Physics, attr, Mock())
            getattr(mock_data.Physics, attr).front_left = 0.0
            getattr(mock_data.Physics, attr).front_right = 0.0
            getattr(mock_data.Physics, attr).rear_left = 0.0
            getattr(mock_data.Physics, attr).rear_right = 0.0
            if attr == "g_force" or attr == "velocity":
                getattr(mock_data.Physics, attr).x = 0.0
                getattr(mock_data.Physics, attr).y = 0.0
                getattr(mock_data.Physics, attr).z = 0.0

        mock_data.Physics.steer_angle = 0.0
        mock_data.Physics.water_temp = 90.0
        mock_data.Physics.turbo_boost = 1.0
        mock_data.Physics.tc = 1
        mock_data.Physics.abs = 1

        mock_data.Graphics.current_time = 90000
        mock_data.Graphics.last_time = 92000
        mock_data.Graphics.best_time = 89500

        mock_instance.read_shared_memory.return_value = mock_data
        mock_sm.return_value = mock_instance

        # 性能测试
        start_time = time.time()
        iterations = 1000

        with ACCTelemetry() as telemetry:
            for _ in range(iterations):
                data = telemetry.get_telemetry()
                if data is None:
                    break

        end_time = time.time()
        duration = end_time - start_time

        print(f"完成 {iterations} 次数据读取")
        print(f"总耗时: {duration:.3f} 秒")
        print(f"平均每次: {duration/iterations*1000:.3f} 毫秒")
        print(f"理论最大频率: {iterations/duration:.1f} Hz")


if __name__ == "__main__":
    # 运行单元测试
    print("=== 运行单元测试 ===")
    unittest.main(argv=[""], exit=False, verbosity=2)

    # 运行性能测试
    run_performance_test()
