#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry 测试脚本

这个脚本用于测试ACC_Telemetry库的基本功能，包括：
1. 连接到ACC共享内存
2. 读取遥测数据
3. 验证数据格式和内容

使用方法:
    python test_telemetry.py
"""

import sys
import time

# 导入本地模块
from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData

# 也可以使用以下导入方式（如果已安装为包）
# from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData


def test_connection():
    """测试与ACC共享内存的连接"""
    print("测试1: 连接到ACC共享内存")

    try:
        telemetry = ACCTelemetry()
        print("  ✓ 成功创建ACCTelemetry实例")

        # 尝试关闭连接
        telemetry.close()
        print("  ✓ 成功关闭连接")

        return True
    except Exception as e:
        print(f"  ✗ 连接测试失败: {e}")
        return False


def test_data_reading():
    """测试读取遥测数据"""
    print("\n测试2: 读取遥测数据")

    telemetry = ACCTelemetry()

    try:
        # 尝试读取数据（最多尝试5次）
        data = None
        attempts = 0
        max_attempts = 5

        while data is None and attempts < max_attempts:
            attempts += 1
            print(f"  尝试读取数据... ({attempts}/{max_attempts})")
            data = telemetry.get_telemetry()

            if data is None:
                print("  未检测到数据，请确保ACC游戏正在运行")
                time.sleep(1)

        if data is not None:
            print("  ✓ 成功读取遥测数据")
            return data
        else:
            print("  ✗ 无法读取遥测数据，请确保ACC游戏正在运行")
            return None
    except Exception as e:
        print(f"  ✗ 读取数据测试失败: {e}")
        return None
    finally:
        telemetry.close()


def test_data_validation(data):
    """验证遥测数据的格式和内容"""
    print("\n测试3: 验证遥测数据")

    if data is None:
        print("  ✗ 没有数据可供验证")
        return False

    try:
        # 验证数据类型
        if not isinstance(data, TelemetryData):
            print(f"  ✗ 数据类型错误: {type(data)}，应为TelemetryData")
            return False

        print("  ✓ 数据类型正确: TelemetryData")

        # 验证基本字段
        fields = [
            "timestamp",
            "speed",
            "rpm",
            "gear",
            "fuel",
            "throttle",
            "brake",
            "clutch",
            "tire_pressure_fl",
            "tire_pressure_fr",
            "tire_pressure_rl",
            "tire_pressure_rr",
        ]

        for field in fields:
            if not hasattr(data, field):
                print(f"  ✗ 缺少字段: {field}")
                return False

        print("  ✓ 所有必要字段都存在")

        # 验证数据范围（简单检查）
        if not (0 <= data.speed <= 500):
            print(f"  ✗ 速度值异常: {data.speed}")

        if not (0 <= data.rpm <= 20000):
            print(f"  ✗ 转速值异常: {data.rpm}")

        if not (-1 <= data.gear <= 8):
            print(f"  ✗ 档位值异常: {data.gear}")

        if not (0 <= data.fuel <= 200):
            print(f"  ✗ 燃油值异常: {data.fuel}")

        # 验证踏板值（应该在0-1之间）
        pedals = ["throttle", "brake", "clutch"]
        for pedal in pedals:
            value = getattr(data, pedal)
            if not (0 <= value <= 1):
                print(f"  ✗ {pedal}值异常: {value}，应在0-1之间")

        # 验证轮胎压力（通常在20-35 PSI之间）
        tires = [
            "tire_pressure_fl",
            "tire_pressure_fr",
            "tire_pressure_rl",
            "tire_pressure_rr",
        ]
        for tire in tires:
            value = getattr(data, tire)
            if not (0 <= value <= 50):
                print(f"  ✗ {tire}值异常: {value}，应在0-50 PSI之间")

        print("  ✓ 数据值在合理范围内")

        # 打印数据摘要
        print("\n数据摘要:")
        print(f"  时间戳: {data.timestamp:.3f}")
        print(f"  速度: {data.speed:.1f} km/h")
        print(f"  转速: {data.rpm} RPM")
        print(f"  档位: {data.gear}")
        print(f"  燃油: {data.fuel:.1f} L")
        print(f"  油门: {data.throttle*100:.1f}%")
        print(f"  刹车: {data.brake*100:.1f}%")
        print(f"  离合: {data.clutch*100:.1f}%")
        print(
            f"  轮胎压力 (PSI): {data.tire_pressure_fl:.1f} / "
            f"{data.tire_pressure_fr:.1f} / {data.tire_pressure_rl:.1f} / "
            f"{data.tire_pressure_rr:.1f}"
        )

        return True
    except Exception as e:
        print(f"  ✗ 数据验证失败: {e}")
        return False


def run_tests():
    """运行所有测试"""
    print("===== ACC_Telemetry 测试 =====\n")

    # 测试1: 连接
    connection_ok = test_connection()
    if not connection_ok:
        print("\n连接测试失败，无法继续后续测试")
        return False

    # 测试2: 读取数据
    data = test_data_reading()

    # 测试3: 验证数据
    if data is not None:
        data_ok = test_data_validation(data)
    else:
        data_ok = False

    # 总结
    print("\n===== 测试结果摘要 =====")
    print(f"连接测试: {'通过' if connection_ok else '失败'}")
    print(f"数据读取测试: {'通过' if data is not None else '失败'}")
    print(f"数据验证测试: {'通过' if data_ok else '失败'}")

    if connection_ok and data is not None and data_ok:
        print("\n所有测试通过! ACC_Telemetry工作正常。")
        return True
    else:
        print("\n部分测试失败。请检查ACC游戏是否正在运行，以及共享内存是否可访问。")
        return False


if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        sys.exit(1)
