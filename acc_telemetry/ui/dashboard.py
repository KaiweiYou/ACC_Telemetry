import tkinter as tk
from tkinter import ttk
from ..core.telemetry import ACCTelemetry

class AccDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ACC 遥测数据面板")
        self.root.geometry("600x800")
        
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建显示标签
        self.create_dashboard_widgets()
        
        # 开始更新循环
        self.update_dashboard()
        
    def create_section_label(self, text, row):
        """创建分区标签"""
        label = ttk.Label(self.main_frame, text=text, font=('Arial', 16, 'bold'))
        label.grid(row=row, column=0, columnspan=2, pady=(20,10), sticky=tk.W)
        return row + 1
        
    def create_dashboard_widgets(self):
        """创建仪表盘控件"""
        current_row = 0
        
        # 基础数据区
        current_row = self.create_section_label("基础数据", current_row)
        
        # 速度显示
        self.speed_label = ttk.Label(self.main_frame, text="速度:", font=('Arial', 14))
        self.speed_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.speed_value = ttk.Label(self.main_frame, text="0 km/h", font=('Arial', 14, 'bold'))
        self.speed_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # RPM显示
        self.rpm_label = ttk.Label(self.main_frame, text="转速:", font=('Arial', 14))
        self.rpm_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.rpm_value = ttk.Label(self.main_frame, text="0 RPM", font=('Arial', 14, 'bold'))
        self.rpm_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 档位显示
        self.gear_label = ttk.Label(self.main_frame, text="档位:", font=('Arial', 14))
        self.gear_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.gear_value = ttk.Label(self.main_frame, text="N", font=('Arial', 14, 'bold'))
        self.gear_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 油量显示
        self.fuel_label = ttk.Label(self.main_frame, text="燃油:", font=('Arial', 14))
        self.fuel_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.fuel_value = ttk.Label(self.main_frame, text="0 L", font=('Arial', 14, 'bold'))
        self.fuel_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 踏板数据区
        current_row = self.create_section_label("踏板状态", current_row)
        
        # 油门显示
        self.throttle_label = ttk.Label(self.main_frame, text="油门:", font=('Arial', 14))
        self.throttle_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.throttle_value = ttk.Label(self.main_frame, text="0%", font=('Arial', 14, 'bold'))
        self.throttle_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 刹车显示
        self.brake_label = ttk.Label(self.main_frame, text="刹车:", font=('Arial', 14))
        self.brake_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.brake_value = ttk.Label(self.main_frame, text="0%", font=('Arial', 14, 'bold'))
        self.brake_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 离合显示
        self.clutch_label = ttk.Label(self.main_frame, text="离合:", font=('Arial', 14))
        self.clutch_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.clutch_value = ttk.Label(self.main_frame, text="0%", font=('Arial', 14, 'bold'))
        self.clutch_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 轮胎数据区
        current_row = self.create_section_label("轮胎压力 (PSI)", current_row)
        
        # 左前轮胎
        self.fl_pressure_label = ttk.Label(self.main_frame, text="左前:", font=('Arial', 14))
        self.fl_pressure_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.fl_pressure_value = ttk.Label(self.main_frame, text="0.0", font=('Arial', 14, 'bold'))
        self.fl_pressure_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 右前轮胎
        self.fr_pressure_label = ttk.Label(self.main_frame, text="右前:", font=('Arial', 14))
        self.fr_pressure_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.fr_pressure_value = ttk.Label(self.main_frame, text="0.0", font=('Arial', 14, 'bold'))
        self.fr_pressure_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 左后轮胎
        self.rl_pressure_label = ttk.Label(self.main_frame, text="左后:", font=('Arial', 14))
        self.rl_pressure_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.rl_pressure_value = ttk.Label(self.main_frame, text="0.0", font=('Arial', 14, 'bold'))
        self.rl_pressure_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        current_row += 1
        
        # 右后轮胎
        self.rr_pressure_label = ttk.Label(self.main_frame, text="右后:", font=('Arial', 14))
        self.rr_pressure_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
        self.rr_pressure_value = ttk.Label(self.main_frame, text="0.0", font=('Arial', 14, 'bold'))
        self.rr_pressure_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
        
    def update_dashboard(self):
        """更新仪表盘数据"""
        data = self.telemetry.get_telemetry()
        
        if data is not None:
            # 更新基础数据
            self.speed_value.config(text=f"{data.speed:.1f} km/h")
            self.rpm_value.config(text=f"{data.rpm} RPM")
            self.gear_value.config(text=str(data.gear))
            self.fuel_value.config(text=f"{data.fuel:.1f} L")
            
            # 更新踏板数据
            self.throttle_value.config(text=f"{data.throttle * 100:.0f}%")
            self.brake_value.config(text=f"{data.brake * 100:.0f}%")
            self.clutch_value.config(text=f"{data.clutch * 100:.0f}%")
            
            # 更新轮胎压力数据
            self.fl_pressure_value.config(text=f"{data.tire_pressure_fl:.1f}")
            self.fr_pressure_value.config(text=f"{data.tire_pressure_fr:.1f}")
            self.rl_pressure_value.config(text=f"{data.tire_pressure_rl:.1f}")
            self.rr_pressure_value.config(text=f"{data.tire_pressure_rr:.1f}")
        
        # 每16毫秒更新一次 (约60fps)
        self.root.after(16, self.update_dashboard)
    
    def run(self):
        """运行仪表盘"""
        try:
            self.root.mainloop()
        finally:
            self.telemetry.close()

if __name__ == "__main__":
    dashboard = AccDashboard()
    dashboard.run()