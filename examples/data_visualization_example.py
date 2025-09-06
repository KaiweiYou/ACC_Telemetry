#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry 数据可视化示例

这个示例展示了如何使用matplotlib绘制ACC遥测数据的实时图表。
运行此示例前，请确保已安装matplotlib和numpy库。

使用方法:
    python data_visualization_example.py
"""

import sys
import time
from collections import deque

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.animation import FuncAnimation


# 自动检测并设置支持中文的字体，避免缺字警告
def _set_chinese_font():
    """在常见中文字体中选择可用字体并应用到 matplotlib。"""
    candidate_fonts = [
        "SimHei",  # 黑体
        "Microsoft YaHei",  # 微软雅黑
        "SimSun",  # 宋体
        "STHeiti",  # 华文黑体 (macOS)
        "PingFang SC",  # 苹果系统默认中文字体
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for font_name in candidate_fonts:
        if font_name in available:
            plt.rcParams["font.family"] = font_name
            break
    # 解决负号无法正常显示的问题
    plt.rcParams["axes.unicode_minus"] = False


# 调用字体设置
_set_chinese_font()

# 导入遥测模块
from acc_telemetry.core.telemetry import ACCTelemetry

# 数据缓冲区大小（保存多少个数据点）
BUFFER_SIZE = 100


class TelemetryVisualizer:
    def __init__(self):
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()

        # 初始化数据缓冲区
        self.timestamps = deque(maxlen=BUFFER_SIZE)
        self.speeds = deque(maxlen=BUFFER_SIZE)
        self.rpms = deque(maxlen=BUFFER_SIZE)
        self.throttles = deque(maxlen=BUFFER_SIZE)
        self.brakes = deque(maxlen=BUFFER_SIZE)
        self.clutches = deque(maxlen=BUFFER_SIZE)
        self.tire_fl = deque(maxlen=BUFFER_SIZE)
        self.tire_fr = deque(maxlen=BUFFER_SIZE)
        self.tire_rl = deque(maxlen=BUFFER_SIZE)
        self.tire_rr = deque(maxlen=BUFFER_SIZE)

        # 初始化时间基准
        self.start_time = time.time()

        # 创建图表
        self.setup_plot()

    def setup_plot(self):
        """设置图表布局"""
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title("ACC 遥测数据可视化")

        # 创建子图
        self.ax1 = plt.subplot(2, 2, 1)  # 速度
        self.ax2 = plt.subplot(2, 2, 2)  # 转速
        self.ax3 = plt.subplot(2, 2, 3)  # 踏板
        self.ax4 = plt.subplot(2, 2, 4)  # 轮胎压力

        # 设置标题和标签
        self.ax1.set_title("速度")
        self.ax1.set_ylabel("km/h")
        self.ax1.set_xlabel("时间 (秒)")

        self.ax2.set_title("发动机转速")
        self.ax2.set_ylabel("RPM")
        self.ax2.set_xlabel("时间 (秒)")

        self.ax3.set_title("踏板状态")
        self.ax3.set_ylabel("百分比 (%)")
        self.ax3.set_xlabel("时间 (秒)")
        self.ax3.set_ylim(0, 100)

        self.ax4.set_title("轮胎压力")
        self.ax4.set_ylabel("PSI")
        self.ax4.set_xlabel("时间 (秒)")

        # 创建线条对象
        (self.speed_line,) = self.ax1.plot([], [], "b-", label="速度")
        (self.rpm_line,) = self.ax2.plot([], [], "r-", label="转速")

        (self.throttle_line,) = self.ax3.plot([], [], "g-", label="油门")
        (self.brake_line,) = self.ax3.plot([], [], "r-", label="刹车")
        (self.clutch_line,) = self.ax3.plot([], [], "b-", label="离合")

        (self.tire_fl_line,) = self.ax4.plot([], [], "b-", label="左前")
        (self.tire_fr_line,) = self.ax4.plot([], [], "r-", label="右前")
        (self.tire_rl_line,) = self.ax4.plot([], [], "g-", label="左后")
        (self.tire_rr_line,) = self.ax4.plot([], [], "y-", label="右后")

        # 添加图例
        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()
        self.ax4.legend()

        # 调整布局
        plt.tight_layout()

    def update_data(self):
        """更新遥测数据"""
        data = self.telemetry.get_telemetry()

        if data is not None:
            # 计算相对时间（从启动开始的秒数）
            current_time = time.time() - self.start_time

            # 更新数据缓冲区
            self.timestamps.append(current_time)
            self.speeds.append(data.speed)
            self.rpms.append(data.rpm)
            self.throttles.append(data.throttle * 100)  # 转换为百分比
            self.brakes.append(data.brake * 100)
            self.clutches.append(data.clutch * 100)
            self.tire_fl.append(data.tire_pressure_fl)
            self.tire_fr.append(data.tire_pressure_fr)
            self.tire_rl.append(data.tire_pressure_rl)
            self.tire_rr.append(data.tire_pressure_rr)

            return True
        return False

    def update_plot(self, frame):
        """更新图表"""
        # 更新数据
        success = self.update_data()

        if success and len(self.timestamps) > 1:
            # 转换为数组以便绘图
            times = np.array(self.timestamps)

            # 更新线条数据
            self.speed_line.set_data(times, np.array(self.speeds))
            self.rpm_line.set_data(times, np.array(self.rpms))

            self.throttle_line.set_data(times, np.array(self.throttles))
            self.brake_line.set_data(times, np.array(self.brakes))
            self.clutch_line.set_data(times, np.array(self.clutches))

            self.tire_fl_line.set_data(times, np.array(self.tire_fl))
            self.tire_fr_line.set_data(times, np.array(self.tire_fr))
            self.tire_rl_line.set_data(times, np.array(self.tire_rl))
            self.tire_rr_line.set_data(times, np.array(self.tire_rr))

            # 调整坐标轴范围
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.relim()
                ax.autoscale_view()

            # 设置固定的y轴范围
            if len(self.speeds) > 0:
                self.ax1.set_ylim(0, max(max(self.speeds) * 1.1, 10))

            if len(self.rpms) > 0:
                self.ax2.set_ylim(0, max(max(self.rpms) * 1.1, 1000))

            # 踏板状态固定为0-100%
            self.ax3.set_ylim(0, 100)

            if len(self.tire_fl) > 0:
                min_pressure = min(
                    min(self.tire_fl),
                    min(self.tire_fr),
                    min(self.tire_rl),
                    min(self.tire_rr),
                )
                max_pressure = max(
                    max(self.tire_fl),
                    max(self.tire_fr),
                    max(self.tire_rl),
                    max(self.tire_rr),
                )
                self.ax4.set_ylim(min_pressure * 0.9, max_pressure * 1.1)

            # 调整x轴范围，只显示最近的数据
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                if len(times) > 0:
                    ax.set_xlim(max(0, times[-1] - 20), times[-1] + 1)

        return [
            self.speed_line,
            self.rpm_line,
            self.throttle_line,
            self.brake_line,
            self.clutch_line,
            self.tire_fl_line,
            self.tire_fr_line,
            self.tire_rl_line,
            self.tire_rr_line,
        ]

    def run(self):
        """运行可视化"""
        try:
            # 创建动画
            self.ani = FuncAnimation(self.fig, self.update_plot, interval=50, blit=True)
            plt.show()
        except KeyboardInterrupt:
            print("\n可视化已停止")
        finally:
            self.telemetry.close()


def main():
    print("启动ACC遥测数据可视化...")
    print("请确保ACC游戏正在运行")
    print("按 Ctrl+C 或关闭窗口退出")

    visualizer = TelemetryVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()
