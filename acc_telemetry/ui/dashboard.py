import tkinter as tk
from tkinter import ttk
import time
from ..core.telemetry import ACCTelemetry
from ..config import DASHBOARD_CONFIG

class AccDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ACC 遥测数据面板")
        
        # 从配置文件读取窗口尺寸
        window_width = DASHBOARD_CONFIG['width']
        window_height = DASHBOARD_CONFIG['height']
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 应用主题
        self.apply_theme(DASHBOARD_CONFIG['theme'])
        
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置窗口响应式布局
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 创建状态栏
        self.status_bar = ttk.Label(self.root, text="等待连接 ACC...", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 创建显示标签
        self.create_dashboard_widgets()
        
        # 计算更新间隔
        self.update_interval = int(1000 / DASHBOARD_CONFIG['update_rate'])  # 毫秒
        
        # 开始更新循环
        self.update_dashboard()
        
    def apply_theme(self, theme_name):
        """应用主题设置"""
        style = ttk.Style()
        
        if theme_name == 'dark':
            # 深色主题
            self.root.configure(bg='#2e2e2e')
            style.configure('TFrame', background='#2e2e2e')
            style.configure('TLabel', background='#2e2e2e', foreground='#ffffff')
            style.configure('Header.TLabel', font=(DASHBOARD_CONFIG['font_family'], 16, 'bold'), background='#2e2e2e', foreground='#ffffff')
            style.configure('Value.TLabel', font=(DASHBOARD_CONFIG['font_family'], 14, 'bold'), background='#2e2e2e', foreground='#00ff00')
            style.configure('Title.TLabel', font=(DASHBOARD_CONFIG['font_family'], 14), background='#2e2e2e', foreground='#aaaaaa')
        elif theme_name == 'light':
            # 浅色主题
            self.root.configure(bg='#f0f0f0')
            style.configure('TFrame', background='#f0f0f0')
            style.configure('TLabel', background='#f0f0f0', foreground='#000000')
            style.configure('Header.TLabel', font=(DASHBOARD_CONFIG['font_family'], 16, 'bold'), background='#f0f0f0', foreground='#000000')
            style.configure('Value.TLabel', font=(DASHBOARD_CONFIG['font_family'], 14, 'bold'), background='#f0f0f0', foreground='#0000ff')
            style.configure('Title.TLabel', font=(DASHBOARD_CONFIG['font_family'], 14), background='#f0f0f0', foreground='#555555')
        else:  # default
            # 默认主题
            style.configure('Header.TLabel', font=(DASHBOARD_CONFIG['font_family'], 16, 'bold'))
            style.configure('Value.TLabel', font=(DASHBOARD_CONFIG['font_family'], 14, 'bold'))
            style.configure('Title.TLabel', font=(DASHBOARD_CONFIG['font_family'], 14))
    
    def create_section_label(self, text, row):
        """创建分区标签"""
        label = ttk.Label(self.main_frame, text=text, style='Header.TLabel')
        label.grid(row=row, column=0, columnspan=2, pady=(20,10), sticky=tk.W)
        return row + 1
        
    def create_dashboard_widgets(self):
        """创建仪表盘控件"""
        current_row = 0
        
        # 基础数据区
        if DASHBOARD_CONFIG['show_physics']:
            current_row = self.create_section_label("基础数据", current_row)
            
            # 速度显示
            self.speed_label = ttk.Label(self.main_frame, text="速度:", style='Title.TLabel')
            self.speed_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
            self.speed_value = ttk.Label(self.main_frame, text="0 km/h", style='Value.TLabel')
            self.speed_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
            current_row += 1
            
            # RPM显示
            self.rpm_label = ttk.Label(self.main_frame, text="转速:", style='Title.TLabel')
            self.rpm_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
            self.rpm_value = ttk.Label(self.main_frame, text="0 RPM", style='Value.TLabel')
            self.rpm_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
            current_row += 1
            
            # 档位显示
            self.gear_label = ttk.Label(self.main_frame, text="档位:", style='Title.TLabel')
            self.gear_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
            self.gear_value = ttk.Label(self.main_frame, text="N", style='Value.TLabel')
            self.gear_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
            current_row += 1
            
            # 油量显示
            self.fuel_label = ttk.Label(self.main_frame, text="燃油:", style='Title.TLabel')
            self.fuel_label.grid(row=current_row, column=0, sticky=tk.W, padx=10, pady=5)
            self.fuel_value = ttk.Label(self.main_frame, text="0 L", style='Value.TLabel')
            self.fuel_value.grid(row=current_row, column=1, sticky=tk.W, padx=10, pady=5)
            current_row += 1
        
        # 踏板数据区
        if DASHBOARD_CONFIG['show_pedals']:
            current_row = self.create_section_label("踏板状态", current_row)
            
            # 创建进度条框架
            pedals_frame = ttk.Frame(self.main_frame)
            pedals_frame.grid(row=current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
            pedals_frame.columnconfigure(1, weight=1)
            
            # 油门显示
            ttk.Label(pedals_frame, text="油门:", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
            self.throttle_bar = ttk.Progressbar(pedals_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
            self.throttle_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            self.throttle_value = ttk.Label(pedals_frame, text="0%", style='Value.TLabel')
            self.throttle_value.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
            
            # 刹车显示
            ttk.Label(pedals_frame, text="刹车:", style='Title.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
            self.brake_bar = ttk.Progressbar(pedals_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
            self.brake_bar.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            self.brake_value = ttk.Label(pedals_frame, text="0%", style='Value.TLabel')
            self.brake_value.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
            
            # 离合显示
            ttk.Label(pedals_frame, text="离合:", style='Title.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
            self.clutch_bar = ttk.Progressbar(pedals_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
            self.clutch_bar.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            self.clutch_value = ttk.Label(pedals_frame, text="0%", style='Value.TLabel')
            self.clutch_value.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
            
            current_row += 1
        
        # 轮胎数据区
        if DASHBOARD_CONFIG['show_tires']:
            current_row = self.create_section_label("轮胎压力 (PSI)", current_row)
            
            # 创建轮胎布局框架
            tires_frame = ttk.Frame(self.main_frame)
            tires_frame.grid(row=current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
            
            # 左前轮胎
            self.fl_pressure_label = ttk.Label(tires_frame, text="左前", style='Title.TLabel')
            self.fl_pressure_label.grid(row=0, column=0, padx=20, pady=5)
            self.fl_pressure_value = ttk.Label(tires_frame, text="0.0", style='Value.TLabel')
            self.fl_pressure_value.grid(row=1, column=0, padx=20, pady=5)
            
            # 右前轮胎
            self.fr_pressure_label = ttk.Label(tires_frame, text="右前", style='Title.TLabel')
            self.fr_pressure_label.grid(row=0, column=1, padx=20, pady=5)
            self.fr_pressure_value = ttk.Label(tires_frame, text="0.0", style='Value.TLabel')
            self.fr_pressure_value.grid(row=1, column=1, padx=20, pady=5)
            
            # 左后轮胎
            self.rl_pressure_label = ttk.Label(tires_frame, text="左后", style='Title.TLabel')
            self.rl_pressure_label.grid(row=2, column=0, padx=20, pady=5)
            self.rl_pressure_value = ttk.Label(tires_frame, text="0.0", style='Value.TLabel')
            self.rl_pressure_value.grid(row=3, column=0, padx=20, pady=5)
            
            # 右后轮胎
            self.rr_pressure_label = ttk.Label(tires_frame, text="右后", style='Title.TLabel')
            self.rr_pressure_label.grid(row=2, column=1, padx=20, pady=5)
            self.rr_pressure_value = ttk.Label(tires_frame, text="0.0", style='Value.TLabel')
            self.rr_pressure_value.grid(row=3, column=1, padx=20, pady=5)
            
            current_row += 1
        
    def update_dashboard(self):
        """更新仪表盘数据"""
        data = self.telemetry.get_telemetry()
        
        if data is not None:
            # 更新状态栏
            self.status_bar.config(text=f"已连接 ACC - 最后更新: {time.strftime('%H:%M:%S')}")
            
            if DASHBOARD_CONFIG['show_physics']:
                # 更新基础数据
                self.speed_value.config(text=f"{data.speed:.1f} km/h")
                self.rpm_value.config(text=f"{data.rpm} RPM")
                
                # 档位显示特殊处理
                gear_text = "R" if data.gear == -1 else "N" if data.gear == 0 else str(data.gear)
                self.gear_value.config(text=gear_text)
                
                self.fuel_value.config(text=f"{data.fuel:.1f} L")
            
            if DASHBOARD_CONFIG['show_pedals']:
                # 更新踏板数据
                throttle_percent = data.throttle * 100
                brake_percent = data.brake * 100
                clutch_percent = data.clutch * 100
                
                # 更新进度条
                self.throttle_bar['value'] = throttle_percent
                self.brake_bar['value'] = brake_percent
                self.clutch_bar['value'] = clutch_percent
                
                # 更新文本值
                self.throttle_value.config(text=f"{throttle_percent:.0f}%")
                self.brake_value.config(text=f"{brake_percent:.0f}%")
                self.clutch_value.config(text=f"{clutch_percent:.0f}%")
            
            if DASHBOARD_CONFIG['show_tires']:
                # 更新轮胎压力数据
                self.fl_pressure_value.config(text=f"{data.tire_pressure_fl:.1f}")
                self.fr_pressure_value.config(text=f"{data.tire_pressure_fr:.1f}")
                self.rl_pressure_value.config(text=f"{data.tire_pressure_rl:.1f}")
                self.rr_pressure_value.config(text=f"{data.tire_pressure_rr:.1f}")
                
                # 根据压力值设置颜色（简单的压力范围检查）
                self.update_tire_pressure_color(self.fl_pressure_value, data.tire_pressure_fl)
                self.update_tire_pressure_color(self.fr_pressure_value, data.tire_pressure_fr)
                self.update_tire_pressure_color(self.rl_pressure_value, data.tire_pressure_rl)
                self.update_tire_pressure_color(self.rr_pressure_value, data.tire_pressure_rr)
        else:
            # 未连接状态
            self.status_bar.config(text="等待连接 ACC... (请确保游戏已启动)")
        
        # 根据配置的更新频率更新数据
        self.root.after(self.update_interval, self.update_dashboard)
    
    def update_tire_pressure_color(self, label, pressure):
        """根据胎压值更新显示颜色"""
        if pressure < 27.0:  # 胎压过低
            label.config(foreground="blue")
        elif pressure > 30.0:  # 胎压过高
            label.config(foreground="red")
        else:  # 胎压正常
            label.config(foreground="green")
    
    def run(self):
        """运行仪表盘"""
        try:
            # 设置窗口图标（如果有）
            try:
                self.root.iconbitmap("icon.ico")
            except:
                pass  # 忽略图标加载错误
                
            # 启动主循环
            self.root.mainloop()
        except Exception as e:
            print(f"运行错误: {e}")
        finally:
            # 确保关闭资源
            self.telemetry.close()
            print("已关闭仪表盘")

if __name__ == "__main__":
    dashboard = AccDashboard()
    dashboard.run()