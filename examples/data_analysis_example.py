#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry 数据分析示例

这个示例展示了如何加载和分析之前记录的ACC遥测数据。
它将读取CSV文件，计算一些基本统计信息，并生成分析图表。

使用方法:
    python data_analysis_example.py [输入文件]

参数:
    输入文件 - 包含遥测数据的CSV文件路径

要求:
    - pandas
    - matplotlib
    - numpy
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec


def load_telemetry_data(file_path):
    """加载遥测数据CSV文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件: {file_path}")

    print(f"正在加载数据文件: {file_path}")
    df = pd.read_csv(file_path)

    # 显示数据基本信息
    print(f"\n数据点数量: {len(df)}")
    print(f"记录时长: {df['elapsed_time'].max():.1f} 秒")
    print(f"数据列: {', '.join(df.columns)}")

    return df


def calculate_statistics(df):
    """计算基本统计信息"""
    print("\n计算基本统计信息...")

    # 速度统计
    max_speed = df["speed"].max()
    avg_speed = df["speed"].mean()
    print(f"最高速度: {max_speed:.1f} km/h")
    print(f"平均速度: {avg_speed:.1f} km/h")

    # 转速统计
    max_rpm = df["rpm"].max()
    avg_rpm = df["rpm"].mean()
    print(f"最高转速: {max_rpm:.0f} RPM")
    print(f"平均转速: {avg_rpm:.0f} RPM")

    # 踏板使用统计
    throttle_usage = df["throttle"].mean() * 100
    brake_usage = df["brake"].mean() * 100
    print(f"平均油门使用: {throttle_usage:.1f}%")
    print(f"平均刹车使用: {brake_usage:.1f}%")

    # 档位使用统计
    gear_counts = df["gear"].value_counts().sort_index()
    print("\n档位使用情况:")
    for gear, count in gear_counts.items():
        percentage = count / len(df) * 100
        if gear == -1:
            gear_name = "R"
        elif gear == 0:
            gear_name = "N"
        else:
            gear_name = str(gear)
        print(f"  {gear_name}: {percentage:.1f}% ({count} 个数据点)")

    # 轮胎压力统计
    print("\n轮胎压力 (PSI):")
    print(
        f"  左前: {df['tire_pressure_fl'].mean():.2f} (平均) / {df['tire_pressure_fl'].max():.2f} (最大)"
    )
    print(
        f"  右前: {df['tire_pressure_fr'].mean():.2f} (平均) / {df['tire_pressure_fr'].max():.2f} (最大)"
    )
    print(
        f"  左后: {df['tire_pressure_rl'].mean():.2f} (平均) / {df['tire_pressure_rl'].max():.2f} (最大)"
    )
    print(
        f"  右后: {df['tire_pressure_rr'].mean():.2f} (平均) / {df['tire_pressure_rr'].max():.2f} (最大)"
    )

    # 计算加速和减速
    df["speed_diff"] = df["speed"].diff()
    df["acceleration"] = df["speed_diff"] / df["elapsed_time"].diff()

    # 过滤掉无效值
    valid_acc = df["acceleration"].dropna()
    valid_acc = valid_acc[np.abs(valid_acc) < 100]  # 过滤掉异常值

    max_acceleration = (
        valid_acc[valid_acc > 0].max() if len(valid_acc[valid_acc > 0]) > 0 else 0
    )
    max_deceleration = (
        abs(valid_acc[valid_acc < 0].min()) if len(valid_acc[valid_acc < 0]) > 0 else 0
    )

    print(f"\n最大加速度: {max_acceleration:.2f} km/h/s")
    print(f"最大减速度: {max_deceleration:.2f} km/h/s")

    return {
        "max_speed": max_speed,
        "avg_speed": avg_speed,
        "max_rpm": max_rpm,
        "avg_rpm": avg_rpm,
        "throttle_usage": throttle_usage,
        "brake_usage": brake_usage,
        "gear_counts": gear_counts,
        "max_acceleration": max_acceleration,
        "max_deceleration": max_deceleration,
    }


def plot_telemetry_data(df, stats):
    """绘制遥测数据分析图表"""
    print("\n生成分析图表...")

    # 创建一个大图表
    plt.figure(figsize=(15, 10))
    gs = GridSpec(3, 3)

    # 1. 速度随时间变化
    ax1 = plt.subplot(gs[0, :])
    ax1.plot(df["elapsed_time"], df["speed"], "b-")
    ax1.set_title("速度随时间变化")
    ax1.set_xlabel("时间 (秒)")
    ax1.set_ylabel("速度 (km/h)")
    ax1.grid(True)

    # 2. 转速随时间变化
    ax2 = plt.subplot(gs[1, :])
    ax2.plot(df["elapsed_time"], df["rpm"], "r-")
    ax2.set_title("转速随时间变化")
    ax2.set_xlabel("时间 (秒)")
    ax2.set_ylabel("转速 (RPM)")
    ax2.grid(True)

    # 3. 踏板使用随时间变化
    ax3 = plt.subplot(gs[2, 0])
    ax3.plot(df["elapsed_time"], df["throttle"] * 100, "g-", label="油门")
    ax3.plot(df["elapsed_time"], df["brake"] * 100, "r-", label="刹车")
    ax3.plot(df["elapsed_time"], df["clutch"] * 100, "b-", label="离合")
    ax3.set_title("踏板使用随时间变化")
    ax3.set_xlabel("时间 (秒)")
    ax3.set_ylabel("踏板位置 (%)")
    ax3.set_ylim(0, 100)
    ax3.legend()
    ax3.grid(True)

    # 4. 档位使用饼图
    ax4 = plt.subplot(gs[2, 1])
    gear_labels = []
    gear_values = []
    gear_colors = ["red", "gray", "blue", "green", "orange", "purple", "brown", "pink"]

    for gear, count in stats["gear_counts"].items():
        if gear == -1:
            gear_labels.append("R")
        elif gear == 0:
            gear_labels.append("N")
        else:
            gear_labels.append(str(gear))
        gear_values.append(count)

    ax4.pie(
        gear_values,
        labels=gear_labels,
        colors=gear_colors[: len(gear_labels)],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax4.axis("equal")  # 确保饼图是圆的
    ax4.set_title("档位使用分布")

    # 5. 轮胎压力箱线图
    ax5 = plt.subplot(gs[2, 2])
    tire_data = [
        df["tire_pressure_fl"],
        df["tire_pressure_fr"],
        df["tire_pressure_rl"],
        df["tire_pressure_rr"],
    ]
    ax5.boxplot(tire_data, labels=["左前", "右前", "左后", "右后"])
    ax5.set_title("轮胎压力分布")
    ax5.set_ylabel("压力 (PSI)")
    ax5.grid(True)

    # 调整布局
    plt.tight_layout()

    # 保存图表
    output_file = "telemetry_analysis.png"
    plt.savefig(output_file, dpi=150)
    print(f"分析图表已保存到: {output_file}")

    # 显示图表
    plt.show()


def analyze_lap_times(df):
    """尝试分析圈速（如果数据中有相关信息）"""
    # 这个功能需要数据中有圈速信息
    # 在这个简化的示例中，我们假设没有这些数据
    # 实际应用中，可以根据速度和位置数据来估计圈速
    pass


def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("错误: 未指定输入文件")
        print(f"用法: python {sys.argv[0]} <telemetry_data.csv>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # 加载数据
        df = load_telemetry_data(input_file)

        # 计算统计信息
        stats = calculate_statistics(df)

        # 绘制图表
        plot_telemetry_data(df, stats)

    except Exception as e:
        print(f"\n分析过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
