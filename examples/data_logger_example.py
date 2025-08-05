#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry 数据记录器示例

这个示例展示了如何将ACC遥测数据记录到CSV文件中，以便进行离线分析。
运行此示例将创建一个包含时间戳的CSV文件，记录所有遥测数据。

使用方法:
    python data_logger_example.py [输出文件名]

参数:
    输出文件名 - 可选，默认为"acc_telemetry_日期时间.csv"
"""

import sys
import time
import csv
from datetime import datetime

# 导入遥测模块
from acc_telemetry.core.telemetry import ACCTelemetry, TelemetryData

class TelemetryLogger:
    def __init__(self, output_file=None):
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()
        
        # 设置输出文件名
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = f"acc_telemetry_{timestamp}.csv"
        else:
            self.output_file = output_file
        
        # 初始化CSV文件
        self.init_csv()
        
        # 记录开始时间
        self.start_time = time.time()
        self.last_data_time = 0
        self.sample_count = 0
    
    def init_csv(self):
        """初始化CSV文件并写入表头"""
        with open(self.output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'elapsed_time', 'speed', 'rpm', 'gear', 'fuel',
                'throttle', 'brake', 'clutch',
                'tire_pressure_fl', 'tire_pressure_fr', 'tire_pressure_rl', 'tire_pressure_rr'
            ]
            self.writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            self.writer.writeheader()
        
        print(f"已创建数据记录文件: {self.output_file}")
    
    def log_data(self, data: TelemetryData):
        """将遥测数据记录到CSV文件"""
        # 计算经过的时间
        elapsed_time = time.time() - self.start_time
        
        # 准备数据字典
        data_dict = {
            'timestamp': data.timestamp,
            'elapsed_time': round(elapsed_time, 3),
            'speed': data.speed,
            'rpm': data.rpm,
            'gear': data.gear,
            'fuel': data.fuel,
            'throttle': data.throttle,
            'brake': data.brake,
            'clutch': data.clutch,
            'tire_pressure_fl': data.tire_pressure_fl,
            'tire_pressure_fr': data.tire_pressure_fr,
            'tire_pressure_rl': data.tire_pressure_rl,
            'tire_pressure_rr': data.tire_pressure_rr
        }
        
        # 写入CSV文件
        with open(self.output_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data_dict.keys())
            writer.writerow(data_dict)
        
        # 更新计数器
        self.sample_count += 1
        self.last_data_time = time.time()
    
    def run(self, duration=None, sample_rate=10):
        """运行数据记录器
        
        参数:
            duration - 记录持续时间（秒），None表示一直运行直到中断
            sample_rate - 每秒采样次数
        """
        # 计算采样间隔
        sample_interval = 1.0 / sample_rate
        
        try:
            print(f"开始记录数据，采样率: {sample_rate}Hz")
            print("按 Ctrl+C 停止记录")
            
            # 记录开始时间
            start_time = time.time()
            last_status_time = start_time
            
            while True:
                # 检查是否达到指定的持续时间
                if duration is not None and (time.time() - start_time) >= duration:
                    print(f"\n已达到指定的记录时间 {duration} 秒")
                    break
                
                # 获取遥测数据
                data = self.telemetry.get_telemetry()
                
                if data is not None:
                    # 记录数据
                    self.log_data(data)
                    
                    # 每5秒显示一次状态
                    current_time = time.time()
                    if current_time - last_status_time >= 5:
                        elapsed = current_time - start_time
                        print(f"已记录 {self.sample_count} 个数据点，运行时间: {elapsed:.1f} 秒，速度: {data.speed:.1f} km/h")
                        last_status_time = current_time
                
                # 等待下一个采样周期
                time.sleep(sample_interval)
                
        except KeyboardInterrupt:
            print("\n记录已被用户中断")
        except Exception as e:
            print(f"\n记录过程中发生错误: {e}")
        finally:
            # 关闭连接并显示统计信息
            self.telemetry.close()
            
            # 计算总时间和平均采样率
            total_time = time.time() - start_time
            avg_rate = self.sample_count / total_time if total_time > 0 else 0
            
            print("\n记录已完成")
            print(f"总记录时间: {total_time:.1f} 秒")
            print(f"记录的数据点: {self.sample_count}")
            print(f"平均采样率: {avg_rate:.2f} Hz")
            print(f"数据已保存到: {self.output_file}")

def main():
    # 解析命令行参数
    output_file = None
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    # 创建并运行记录器
    logger = TelemetryLogger(output_file)
    
    # 运行记录器，采样率为10Hz，不设置持续时间（一直运行直到中断）
    logger.run(duration=None, sample_rate=10)

if __name__ == "__main__":
    main()