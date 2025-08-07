import customtkinter as ctk
import json
import os
from typing import Dict, List

# 设置CustomTkinter主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TelemetrySettings(ctk.CTkFrame):
    """遥测面板设置窗口"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "telemetry_display_settings.json")
        
        # 可用的遥测数据项
        self.available_data_items = {
            # 基础车辆数据
            "基础车辆数据": {
                "speed": {"name": "速度 (km/h)", "default": True},
                "rpm": {"name": "转速 (RPM)", "default": True},
                "gear": {"name": "档位", "default": True},
                "fuel": {"name": "燃油量 (L)", "default": True},
            },
            
            # 踏板和控制
            "踏板控制": {
                "throttle": {"name": "油门踏板 (%)", "default": True},
                "brake": {"name": "刹车踏板 (%)", "default": True},
                "clutch": {"name": "离合器踏板 (%)", "default": True},
                "steer_angle": {"name": "方向盘角度 (°)", "default": False},
            },
            
            # 轮胎数据
            "轮胎数据": {
                "tire_pressure_fl": {"name": "左前轮胎压力 (PSI)", "default": True},
                "tire_pressure_fr": {"name": "右前轮胎压力 (PSI)", "default": True},
                "tire_pressure_rl": {"name": "左后轮胎压力 (PSI)", "default": True},
                "tire_pressure_rr": {"name": "右后轮胎压力 (PSI)", "default": True},
                "tire_temp_fl": {"name": "左前轮胎温度 (°C)", "default": False},
                "tire_temp_fr": {"name": "右前轮胎温度 (°C)", "default": False},
                "tire_temp_rl": {"name": "左后轮胎温度 (°C)", "default": False},
                "tire_temp_rr": {"name": "右后轮胎温度 (°C)", "default": False},
            },
            
            # 发动机和温度
            "发动机数据": {
                "water_temp": {"name": "水温 (°C)", "default": False},
                "oil_temp": {"name": "机油温度 (°C)", "default": False},
                "turbo_boost": {"name": "涡轮增压压力", "default": False},
            },
            
            # 刹车系统
            "刹车系统": {
                "brake_temp_fl": {"name": "左前刹车温度 (°C)", "default": False},
                "brake_temp_fr": {"name": "右前刹车温度 (°C)", "default": False},
                "brake_temp_rl": {"name": "左后刹车温度 (°C)", "default": False},
                "brake_temp_rr": {"name": "右后刹车温度 (°C)", "default": False},
                "brake_pressure": {"name": "刹车压力", "default": False},
                "brake_bias": {"name": "刹车平衡", "default": False},
            },
            
            # 车辆动态
            "车辆动态": {
                "acceleration_x": {"name": "横向加速度 (G)", "default": False},
                "acceleration_y": {"name": "纵向加速度 (G)", "default": False},
                "acceleration_z": {"name": "垂直加速度 (G)", "default": False},
                "velocity_x": {"name": "X轴速度", "default": False},
                "velocity_y": {"name": "Y轴速度", "default": False},
                "velocity_z": {"name": "Z轴速度", "default": False},
            },
            
            # 电子系统
            "电子系统": {
                "abs_active": {"name": "ABS状态", "default": False},
                "tc_active": {"name": "牵引力控制状态", "default": False},
                "pit_limiter": {"name": "维修站限速器", "default": False},
                "auto_shifter": {"name": "自动换挡", "default": False},
            },
            
            # 比赛信息
            "比赛信息": {
                "lap_time": {"name": "当前圈时间", "default": False},
                "best_lap": {"name": "最佳圈时间", "default": False},
                "position": {"name": "位置", "default": False},
                "lap_count": {"name": "圈数", "default": False},
            }
        }
        
        # 当前设置
        self.current_settings = self.load_settings()

        # 创建界面
        self.create_widgets()
        

        

        
    def create_widgets(self):
        """创建现代化界面组件"""
        # 主容器
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题区域
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 主标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ 遥测面板显示设置",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # 副标题
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="选择要在遥测面板中显示的数据项，支持50+种遥测参数",
            font=ctk.CTkFont(size=16),
            text_color=("gray70", "gray30")
        )
        subtitle_label.pack(pady=(0, 10))
        
        # 内容区域
        content_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # 创建滚动框架
        self.create_scrollable_frame(content_frame)
        
        # 底部按钮区域
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x")
        
        # 预设按钮区域
        preset_frame = ctk.CTkFrame(bottom_frame, corner_radius=12)
        preset_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        preset_label = ctk.CTkLabel(
            preset_frame,
            text="🚀 快速预设",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preset_label.pack(pady=(15, 10))
        
        preset_buttons_frame = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            preset_buttons_frame,
            text="基础模式",
            command=self.apply_basic_preset,
            font=ctk.CTkFont(size=13),
            height=35,
            corner_radius=8,
            fg_color="#3498db",
            hover_color="#2980b9"
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            preset_buttons_frame,
            text="专业模式",
            command=self.apply_professional_preset,
            font=ctk.CTkFont(size=13),
            height=35,
            corner_radius=8,
            fg_color="#e67e22",
            hover_color="#d35400"
        ).pack(side="left", fill="x", expand=True, padx=2.5)
        
        ctk.CTkButton(
            preset_buttons_frame,
            text="全部显示",
            command=self.apply_all_preset,
            font=ctk.CTkFont(size=13),
            height=35,
            corner_radius=8,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # 操作按钮区域
        action_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        ctk.CTkButton(
            action_frame,
            text="💾 保存设置",
            command=self.save_and_close,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            width=120,
            corner_radius=10,
            fg_color="#27ae60",
            hover_color="#229954"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            action_frame,
            text="❌ 取消",
            command=self.cancel,
            font=ctk.CTkFont(size=15),
            height=45,
            width=100,
            corner_radius=10,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).pack(side="left")
        
    def create_scrollable_frame(self, parent):
        """创建现代化可滚动的选项框架"""
        # 创建滚动框架
        self.scrollable_frame = ctk.CTkScrollableFrame(
            parent,
            corner_radius=10,
            scrollbar_button_color=("gray75", "gray25"),
            scrollbar_button_hover_color=("gray64", "gray36")
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建选项
        self.create_options(self.scrollable_frame)
        
    def create_options(self, parent):
        """创建现代化数据项选项"""
        self.checkboxes = {}
        
        # 分类图标映射
        category_icons = {
            "基础车辆数据": "🏎️",
            "踏板控制": "🦶",
            "轮胎数据": "🛞",
            "发动机数据": "🔧",
            "刹车系统": "🛑",
            "车辆动态": "📊",
            "电子系统": "⚡",
            "比赛信息": "🏁"
        }
        
        for category, items in self.available_data_items.items():
            # 分类容器
            category_frame = ctk.CTkFrame(parent, corner_radius=12)
            category_frame.pack(fill="x", pady=(0, 15), padx=10)
            
            # 分类标题
            icon = category_icons.get(category, "📋")
            category_label = ctk.CTkLabel(
                category_frame,
                text=f"{icon} {category}",
                font=ctk.CTkFont(size=18, weight="bold"),
                anchor="w"
            )
            category_label.pack(fill="x", padx=20, pady=(15, 10))
            
            # 选项网格容器
            options_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
            options_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            # 分类下的选项（使用网格布局）
            col = 0
            row = 0
            max_cols = 2  # 每行最多2个选项
            
            for key, item_info in items.items():
                var = ctk.BooleanVar()
                var.set(self.current_settings.get(key, item_info["default"]))
                self.checkboxes[key] = var
                
                # 选项容器
                option_frame = ctk.CTkFrame(options_frame, corner_radius=8, height=50)
                option_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=3)
                option_frame.grid_propagate(False)
                
                # 配置网格权重
                options_frame.grid_columnconfigure(col, weight=1)
                
                checkbox = ctk.CTkCheckBox(
                    option_frame,
                    text=item_info["name"],
                    variable=var,
                    font=ctk.CTkFont(size=13),
                    corner_radius=6,
                    border_width=2,
                    checkbox_width=20,
                    checkbox_height=20
                )
                checkbox.pack(fill="both", expand=True, padx=15, pady=10)
                
                # 更新网格位置
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                
    def apply_basic_preset(self):
        """应用基础模式预设"""
        basic_items = [
            "speed", "rpm", "gear", "fuel",
            "throttle", "brake", "clutch",
            "tire_pressure_fl", "tire_pressure_fr", 
            "tire_pressure_rl", "tire_pressure_rr"
        ]
        
        for key, var in self.checkboxes.items():
            var.set(key in basic_items)
            
    def apply_professional_preset(self):
        """应用专业模式预设"""
        professional_items = [
            "speed", "rpm", "gear", "fuel",
            "throttle", "brake", "clutch", "steer_angle",
            "tire_pressure_fl", "tire_pressure_fr", 
            "tire_pressure_rl", "tire_pressure_rr",
            "tire_temp_fl", "tire_temp_fr", 
            "tire_temp_rl", "tire_temp_rr",
            "water_temp", "brake_temp_fl", "brake_temp_fr",
            "brake_temp_rl", "brake_temp_rr",
            "acceleration_x", "acceleration_y", "acceleration_z",
            "abs_active", "tc_active"
        ]
        
        for key, var in self.checkboxes.items():
            var.set(key in professional_items)
            
    def apply_all_preset(self):
        """应用全部显示预设"""
        for var in self.checkboxes.values():
            var.set(True)
            
    def load_settings(self) -> Dict[str, bool]:
        """加载设置"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载设置失败: {e}")
        
        # 返回默认设置
        default_settings = {}
        for category, items in self.available_data_items.items():
            for key, item_info in items.items():
                default_settings[key] = item_info["default"]
        return default_settings
        
    def save_settings(self) -> Dict[str, bool]:
        """保存设置"""
        settings = {}
        for key, var in self.checkboxes.items():
            settings[key] = var.get()
            
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return settings
        except Exception as e:
            self.show_error_dialog(f"保存设置失败: {e}")
            return {}
            
    def save_and_close(self):
        """保存设置并关闭窗口"""
        settings = self.save_settings()
        if settings:
            # Pass to controller to show message
            # self.show_success_dialog("设置已保存！")
            print("Settings saved!")
            
    def cancel(self):
        """取消设置"""
        # This might need to be handled by the controller
        print("Cancel button clicked")
        

        

        

            
    @staticmethod
    def get_current_settings() -> Dict[str, bool]:
        """获取当前设置（静态方法）"""
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "telemetry_display_settings.json")
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # 返回默认设置
        return {
            "speed": True, "rpm": True, "gear": True, "fuel": True,
            "throttle": True, "brake": True, "clutch": True,
            "tire_pressure_fl": True, "tire_pressure_fr": True,
            "tire_pressure_rl": True, "tire_pressure_rr": True
        }