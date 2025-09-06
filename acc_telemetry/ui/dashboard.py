# -*- coding: utf-8 -*-
import json
import os

import customtkinter as ctk

from ..core.telemetry import ACCTelemetry


class AccDashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=15)
        self.pack(fill="both", expand=True)

        # 延迟初始化标志
        self._initialized = False
        self._telemetry_connected = False
        
        # 初始化基础UI结构（轻量级）
        self._create_base_structure()
        
        # 延迟初始化遥测和其他重组件
        self.after(100, self._delayed_init)

    def _create_base_structure(self):
        """创建基础UI结构（轻量级）"""
        # 创建加载界面
        self.loading_frame = ctk.CTkFrame(self)
        self.loading_frame.pack(fill="both", expand=True)
        
        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="正在初始化仪表盘...",
            font=ctk.CTkFont(size=16)
        )
        self.loading_label.pack(expand=True)

    def _delayed_init(self):
        """延迟初始化重组件"""
        try:
            # 在后台线程中初始化遥测
            self.after(50, self._init_telemetry_async)
        except Exception as e:
            print(f"延迟初始化失败: {e}")
            self._show_init_error(str(e))

    def _init_telemetry_async(self):
        """异步初始化遥测连接"""
        def init_worker():
            try:
                telemetry = ACCTelemetry()
                # 尝试连接，但不阻塞
                return telemetry
            except Exception as e:
                print(f"遥测初始化失败: {e}")
                return None
        
        def on_init_complete(telemetry):
            self.telemetry = telemetry
            self._telemetry_connected = telemetry is not None
            
            # 移除加载界面
            self.loading_frame.pack_forget()
            
            # 继续初始化
            self._complete_init()
        
        # 使用after方法模拟异步
        telemetry = init_worker()
        self.after(0, lambda: on_init_complete(telemetry))

    def _complete_init(self):
        """完成剩余初始化"""
        try:
            # 加载显示设置
            self.load_display_settings()
            
            # 创建主框架
            self.create_scrollable_frame()
            
            # 创建显示标签
            self.create_dashboard_widgets()
            
            # 开始更新循环（如果遥测已连接）
            if self._telemetry_connected:
                self.update_dashboard()
            
            self._initialized = True
            
        except Exception as e:
            print(f"完成初始化失败: {e}")
            self._show_init_error(str(e))

    def _show_init_error(self, error_msg):
        """显示初始化错误"""
        self.loading_label.configure(
            text=f"初始化失败: {error_msg}",
            text_color="red"
        )

    def load_display_settings(self):
        """加载显示设置"""
        settings_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "telemetry_display_settings.json",
        )
        try:
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    self.display_settings = json.load(f)
            else:
                # 默认显示基础数据
                self.display_settings = {
                    "speed": True,
                    "rpm": True,
                    "gear": True,
                    "fuel": True,
                    "throttle": True,
                    "brake": True,
                    "clutch": True,
                    "tire_pressure_fl": True,
                    "tire_pressure_fr": True,
                    "tire_pressure_rl": True,
                    "tire_pressure_rr": True,
                }
        except Exception as e:
            print(f"加载设置失败: {e}")
            self.display_settings = {}

    def create_scrollable_frame(self):
        """创建可滚动的主框架"""
        self.scrollable_frame = ctk.CTkScrollableFrame(self, corner_radius=15)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 主框架
        self.main_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 配置网格权重，使四列能够正确显示
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(3, weight=1)

    def create_section_label(self, text, row, column=0):
        """创建分区标签"""
        label = ctk.CTkLabel(
            self.main_frame, text=text, font=ctk.CTkFont(size=18, weight="bold")
        )
        if column == 0:
            label.grid(row=row, column=0, columnspan=2, pady=(20, 10), sticky="w")
        else:
            label.grid(row=row, column=2, columnspan=2, pady=(20, 10), sticky="w")
        return row + 1

    def create_dashboard_widgets(self):
        """根据设置动态创建仪表盘控件"""
        current_row = 0
        self.data_labels = {}  # 存储所有数据标签的引用

        # 定义数据项配置
        data_config = {
            # 基础数据
            "speed": {"label": "速度", "unit": "km/h", "category": "基础数据"},
            "rpm": {"label": "转速", "unit": "RPM", "category": "基础数据"},
            "gear": {"label": "档位", "unit": "", "category": "基础数据"},
            "fuel": {"label": "燃油", "unit": "L", "category": "基础数据"},
            # 踏板数据
            "throttle": {"label": "油门", "unit": "%", "category": "踏板数据"},
            "brake": {"label": "刹车", "unit": "%", "category": "踏板数据"},
            "clutch": {"label": "离合", "unit": "%", "category": "踏板数据"},
            # 轮胎压力
            "tire_pressure_fl": {
                "label": "轮胎压力-左前",
                "unit": "PSI",
                "category": "轮胎压力",
            },
            "tire_pressure_fr": {
                "label": "轮胎压力-右前",
                "unit": "PSI",
                "category": "轮胎压力",
            },
            "tire_pressure_rl": {
                "label": "轮胎压力-左后",
                "unit": "PSI",
                "category": "轮胎压力",
            },
            "tire_pressure_rr": {
                "label": "轮胎压力-右后",
                "unit": "PSI",
                "category": "轮胎压力",
            },
            # 轮胎温度
            "tire_temp_fl": {
                "label": "轮胎温度-左前",
                "unit": "°C",
                "category": "轮胎温度",
            },
            "tire_temp_fr": {
                "label": "轮胎温度-右前",
                "unit": "°C",
                "category": "轮胎温度",
            },
            "tire_temp_rl": {
                "label": "轮胎温度-左后",
                "unit": "°C",
                "category": "轮胎温度",
            },
            "tire_temp_rr": {
                "label": "轮胎温度-右后",
                "unit": "°C",
                "category": "轮胎温度",
            },
            # 刹车温度
            "brake_temp_fl": {
                "label": "刹车温度-左前",
                "unit": "°C",
                "category": "刹车温度",
            },
            "brake_temp_fr": {
                "label": "刹车温度-右前",
                "unit": "°C",
                "category": "刹车温度",
            },
            "brake_temp_rl": {
                "label": "刹车温度-左后",
                "unit": "°C",
                "category": "刹车温度",
            },
            "brake_temp_rr": {
                "label": "刹车温度-右后",
                "unit": "°C",
                "category": "刹车温度",
            },
            # 车辆动态
            "acceleration_x": {"label": "横向G力", "unit": "G", "category": "车辆动态"},
            "acceleration_y": {"label": "纵向G力", "unit": "G", "category": "车辆动态"},
            "acceleration_z": {"label": "垂直G力", "unit": "G", "category": "车辆动态"},
            "steer_angle": {"label": "转向角度", "unit": "°", "category": "车辆动态"},
            # 引擎数据
            "engine_temp": {"label": "水温", "unit": "°C", "category": "引擎数据"},
            "turbo_boost": {"label": "涡轮增压", "unit": "bar", "category": "引擎数据"},
            # 车轮滑移
            "wheel_slip_fl": {
                "label": "车轮滑移-左前",
                "unit": "",
                "category": "车轮滑移",
            },
            "wheel_slip_fr": {
                "label": "车轮滑移-右前",
                "unit": "",
                "category": "车轮滑移",
            },
            "wheel_slip_rl": {
                "label": "车轮滑移-左后",
                "unit": "",
                "category": "车轮滑移",
            },
            "wheel_slip_rr": {
                "label": "车轮滑移-右后",
                "unit": "",
                "category": "车轮滑移",
            },
            # 辅助系统
            "drs": {"label": "DRS状态", "unit": "", "category": "辅助系统"},
            "tc": {"label": "牵引力控制", "unit": "", "category": "辅助系统"},
            "abs": {"label": "ABS状态", "unit": "", "category": "辅助系统"},
            # 圈速数据
            "lap_time": {"label": "当前圈时间", "unit": "ms", "category": "圈速数据"},
            "last_lap": {"label": "上一圈时间", "unit": "ms", "category": "圈速数据"},
            "best_lap": {"label": "最佳圈时间", "unit": "ms", "category": "圈速数据"},
        }

        # 按类别组织数据
        categories = {}
        for field, config in data_config.items():
            if self.display_settings.get(field, False):
                category = config["category"]
                if category not in categories:
                    categories[category] = []
                categories[category].append((field, config))

        # 创建各类别的显示控件 - 两列布局
        left_column_row = 0
        right_column_row = 0
        current_column = 0  # 0为左列，1为右列

        category_list = list(categories.items())

        for i, (category, items) in enumerate(category_list):
            if items:  # 只有当类别中有要显示的项目时才创建标题
                if current_column == 0:
                    # 左列
                    left_column_row = self.create_section_label(
                        category, left_column_row, 0
                    )

                    for field, config in items:
                        # 创建标签和数值显示
                        label = ctk.CTkLabel(
                            self.main_frame,
                            text=f"{config['label']}:",
                            font=ctk.CTkFont(size=14),
                        )
                        label.grid(
                            row=left_column_row, column=0, sticky="w", padx=10, pady=5
                        )

                        value_label = ctk.CTkLabel(
                            self.main_frame,
                            text="--",
                            font=ctk.CTkFont(size=14, weight="bold"),
                        )
                        value_label.grid(
                            row=left_column_row, column=1, sticky="w", padx=10, pady=5
                        )

                        # 存储标签引用
                        self.data_labels[field] = {
                            "label": label,
                            "value": value_label,
                            "unit": config["unit"],
                        }

                        left_column_row += 1
                else:
                    # 右列
                    right_column_row = self.create_section_label(
                        category, right_column_row, 1
                    )

                    for field, config in items:
                        # 创建标签和数值显示
                        label = ctk.CTkLabel(
                            self.main_frame,
                            text=f"{config['label']}:",
                            font=ctk.CTkFont(size=14),
                        )
                        label.grid(
                            row=right_column_row, column=2, sticky="w", padx=10, pady=5
                        )

                        value_label = ctk.CTkLabel(
                            self.main_frame,
                            text="--",
                            font=ctk.CTkFont(size=14, weight="bold"),
                        )
                        value_label.grid(
                            row=right_column_row, column=3, sticky="w", padx=10, pady=5
                        )

                        # 存储标签引用
                        self.data_labels[field] = {
                            "label": label,
                            "value": value_label,
                            "unit": config["unit"],
                        }

                        right_column_row += 1

                # 交替列
                current_column = 1 - current_column

    def update_dashboard(self):
        """优化后的动态更新仪表盘数据，减少CPU占用"""
        if not self._initialized or not self._telemetry_connected:
            return

        # 降低更新频率至约30fps以减少CPU占用
        self.after(33, self._update_dashboard_async)

    def _update_dashboard_async(self):
        """异步更新仪表盘数据"""
        if not hasattr(self, 'data_labels'):
            return

        try:
            data = self.telemetry.get_telemetry()
            if data is not None:
                # 批量更新，减少UI重绘
                self._batch_update_labels(data)
        except Exception as e:
            print(f"更新仪表盘数据失败: {e}")

        # 继续更新循环
        self.update_dashboard()

    def _batch_update_labels(self, data):
        """批量更新标签，仅在值变化时更新"""
        for field, widgets in self.data_labels.items():
            try:
                value = getattr(data, field)
                unit = widgets["unit"]

                # 根据数据类型格式化显示
                display_text = self._format_display_value(field, value, unit)
                
                # 仅在值变化时更新UI
                current_text = widgets["value"].cget("text")
                if current_text != display_text:
                    widgets["value"].configure(text=display_text)

            except AttributeError:
                widgets["value"].configure(text="N/A")
            except Exception:
                widgets["value"].configure(text="Error")

    def _format_display_value(self, field, value, unit):
        """根据字段类型格式化显示值"""
        if field == "gear":
            if value == 0:
                return "R"
            elif value == 1:
                return "N"
            else:
                return str(value - 1)
        elif field in ["throttle", "brake", "clutch"]:
            return f"{value * 100:.0f}{unit}"
        elif field in ["drs", "tc", "abs"]:
            return "开启" if value else "关闭"
        elif field in ["lap_time", "last_lap", "best_lap"]:
            if value > 0:
                seconds = value / 1000
                minutes = int(seconds // 60)
                seconds = seconds % 60
                return f"{minutes}:{seconds:06.3f}"
            else:
                return "--:---.---"
        elif isinstance(value, float):
            if field in ["acceleration_x", "acceleration_y", "acceleration_z"]:
                return f"{value:.2f}{unit}"
            elif field in ["wheel_slip_fl", "wheel_slip_fr", "wheel_slip_rl", "wheel_slip_rr"]:
                return f"{value:.3f}"
            else:
                return f"{value:.1f}{unit}"
        else:
            return f"{value}{unit}"

    def cleanup(self):
        """清理资源，停止更新循环"""
        try:
            # 停止更新循环
            if hasattr(self, 'update_dashboard'):
                # 取消after回调
                pass
            
            # 清理遥测连接
            if hasattr(self, 'telemetry') and self.telemetry:
                self.telemetry = None
                
            # 清理数据标签引用
            if hasattr(self, 'data_labels'):
                self.data_labels.clear()
                
            # 清理UI组件
            for widget in [self.main_frame, self.scrollable_frame, self.loading_frame]:
                if hasattr(widget, 'destroy') and widget.winfo_exists():
                    try:
                        widget.destroy()
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"清理dashboard资源时出错: {e}")


if __name__ == "__main__":
    # This is for testing purposes only
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Dashboard Test")
            self.geometry("800x600")
            dashboard = AccDashboard(self)
            dashboard.pack(fill="both", expand=True)

    app = TestApp()
    app.mainloop()