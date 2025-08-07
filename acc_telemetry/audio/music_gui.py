#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC遥测音乐系统GUI控制界面

这个模块提供了一个图形用户界面，用于控制和监控
ACC遥测音乐集成系统的运行状态和参数。

作者: Assistant
日期: 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
import os
from typing import Optional, Dict, Any

from .music_integration import MusicIntegration, MusicConfig


class MusicControlGUI:
    """音乐控制GUI主类"""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        初始化GUI界面
        
        Args:
            root: 可选的Tkinter根窗口，如果为None则创建新窗口
        """
        self.root = root or tk.Tk()
        self.root.title("ACC遥测音乐系统控制台")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 音乐集成系统
        self.music_system: Optional[MusicIntegration] = None
        self.config = MusicConfig()
        
        # GUI状态
        self.is_running = False
        self.status_update_thread: Optional[threading.Thread] = None
        self.stop_status_update = False
        
        # 创建GUI组件
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # 加载配置
        self._load_config()
        
        # 启动状态更新
        self._start_status_update()
    
    def _create_widgets(self):
        """创建GUI组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # 标题
        self.title_label = ttk.Label(
            self.main_frame, 
            text="🎵 ACC遥测音乐系统 🏎️",
            font=('Arial', 16, 'bold')
        )
        
        # 控制按钮框架
        self.control_frame = ttk.LabelFrame(self.main_frame, text="系统控制", padding="10")
        
        self.start_button = ttk.Button(
            self.control_frame,
            text="启动音乐系统",
            command=self._start_system,
            style="Accent.TButton"
        )
        
        self.stop_button = ttk.Button(
            self.control_frame,
            text="停止音乐系统",
            command=self._stop_system,
            state="disabled"
        )
        
        # 状态显示框架
        self.status_frame = ttk.LabelFrame(self.main_frame, text="系统状态", padding="10")
        
        # 状态指示器
        self.status_vars = {
            'system': tk.StringVar(value="已停止"),
            'telemetry': tk.StringVar(value="未连接"),
            'music_engine': tk.StringVar(value="未运行"),
            'last_update': tk.StringVar(value="无")
        }
        
        self.status_labels = {}
        status_texts = {
            'system': "系统状态:",
            'telemetry': "遥测连接:",
            'music_engine': "音乐引擎:",
            'last_update': "最后更新:"
        }
        
        for key, text in status_texts.items():
            frame = ttk.Frame(self.status_frame)
            ttk.Label(frame, text=text, width=12).pack(side=tk.LEFT)
            label = ttk.Label(frame, textvariable=self.status_vars[key], width=15)
            label.pack(side=tk.LEFT)
            self.status_labels[key] = label
            frame.pack(fill=tk.X, pady=2)
        
        # 配置框架
        self.config_frame = ttk.LabelFrame(self.main_frame, text="音乐配置", padding="10")
        
        # 创建配置控件
        self._create_config_widgets()
        
        # 实时数据显示框架
        self.data_frame = ttk.LabelFrame(self.main_frame, text="实时遥测数据", padding="10")
        
        # 创建数据显示控件
        self._create_data_widgets()
        
        # 日志框架
        self.log_frame = ttk.LabelFrame(self.main_frame, text="系统日志", padding="10")
        
        # 日志文本框
        self.log_text = tk.Text(
            self.log_frame,
            height=8,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        
        # 日志滚动条
        self.log_scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scrollbar.set)
        
        # 清除日志按钮
        self.clear_log_button = ttk.Button(
            self.log_frame,
            text="清除日志",
            command=self._clear_log
        )
    
    def _create_config_widgets(self):
        """创建配置控件"""
        # 配置变量
        self.config_vars = {
            'update_rate': tk.IntVar(value=60),
            'osc_port': tk.IntVar(value=57120),
            'bpm_min': tk.IntVar(value=80),
            'bpm_max': tk.IntVar(value=180),
            'speed_sensitivity': tk.DoubleVar(value=1.0),
            'steering_sensitivity': tk.DoubleVar(value=1.0),
            'pedal_sensitivity': tk.DoubleVar(value=1.0)
        }
        
        # 配置控件
        config_items = [
            ('更新频率 (Hz):', 'update_rate', 1, 120),
            ('OSC端口:', 'osc_port', 1024, 65535),
            ('BPM最小值:', 'bpm_min', 60, 200),
            ('BPM最大值:', 'bpm_max', 60, 200),
            ('速度敏感度:', 'speed_sensitivity', 0.1, 3.0),
            ('转向敏感度:', 'steering_sensitivity', 0.1, 3.0),
            ('踏板敏感度:', 'pedal_sensitivity', 0.1, 3.0)
        ]
        
        self.config_widgets = {}
        
        for i, (label_text, var_key, min_val, max_val) in enumerate(config_items):
            row = i // 2
            col = (i % 2) * 3
            
            # 标签
            ttk.Label(self.config_frame, text=label_text).grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2
            )
            
            # 输入框
            if isinstance(self.config_vars[var_key], tk.DoubleVar):
                widget = ttk.Spinbox(
                    self.config_frame,
                    from_=min_val,
                    to=max_val,
                    increment=0.1,
                    textvariable=self.config_vars[var_key],
                    width=8,
                    format="%.1f"
                )
            else:
                widget = ttk.Spinbox(
                    self.config_frame,
                    from_=min_val,
                    to=max_val,
                    textvariable=self.config_vars[var_key],
                    width=8
                )
            
            widget.grid(row=row, column=col+1, padx=(0, 20), pady=2)
            self.config_widgets[var_key] = widget
        
        # 配置按钮
        button_frame = ttk.Frame(self.config_frame)
        button_frame.grid(row=len(config_items)//2 + 1, column=0, columnspan=6, pady=10)
        
        ttk.Button(
            button_frame,
            text="应用配置",
            command=self._apply_config
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="保存配置",
            command=self._save_config
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="加载配置",
            command=self._load_config_dialog
        ).pack(side=tk.LEFT)
    
    def _create_data_widgets(self):
        """创建数据显示控件"""
        # 数据变量
        self.data_vars = {
            'speed': tk.StringVar(value="0 km/h"),
            'rpm': tk.StringVar(value="0 RPM"),
            'gear': tk.StringVar(value="N"),
            'throttle': tk.StringVar(value="0%"),
            'brake': tk.StringVar(value="0%"),
            'steer': tk.StringVar(value="0°")
        }
        
        # 数据显示
        data_items = [
            ('速度:', 'speed'),
            ('转速:', 'rpm'),
            ('档位:', 'gear'),
            ('油门:', 'throttle'),
            ('制动:', 'brake'),
            ('转向:', 'steer')
        ]
        
        for i, (label_text, var_key) in enumerate(data_items):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(self.data_frame, text=label_text).grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2
            )
            
            ttk.Label(
                self.data_frame,
                textvariable=self.data_vars[var_key],
                font=('Arial', 10, 'bold')
            ).grid(row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=2)
    
    def _setup_layout(self):
        """设置布局"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        self.title_label.pack(pady=(0, 20))
        
        # 控制按钮
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        self.stop_button.pack(side=tk.LEFT)
        
        # 状态显示
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 配置
        self.config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 实时数据
        self.data_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 日志
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clear_log_button.pack(pady=(10, 0))
    
    def _bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _start_system(self):
        """启动音乐系统"""
        if self.is_running:
            return
        
        try:
            # 应用当前配置
            self._apply_config()
            
            # 创建音乐系统
            self.music_system = MusicIntegration(self.config)
            
            # 启动系统
            if self.music_system.start():
                self.is_running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                self._log("音乐系统已启动")
            else:
                self._log("启动音乐系统失败")
                messagebox.showerror("错误", "启动音乐系统失败，请检查日志")
                
        except Exception as e:
            self._log(f"启动系统时发生错误: {e}")
            messagebox.showerror("错误", f"启动系统时发生错误: {e}")
    
    def _stop_system(self):
        """停止音乐系统"""
        if not self.is_running:
            return
        
        try:
            if self.music_system:
                self.music_system.stop()
                self.music_system = None
            
            self.is_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self._log("音乐系统已停止")
            
        except Exception as e:
            self._log(f"停止系统时发生错误: {e}")
    
    def _apply_config(self):
        """应用配置"""
        try:
            # 更新配置对象
            self.config.update_rate = self.config_vars['update_rate'].get()
            self.config.osc_port = self.config_vars['osc_port'].get()
            self.config.bpm_range = (
                self.config_vars['bpm_min'].get(),
                self.config_vars['bpm_max'].get()
            )
            self.config.speed_sensitivity = self.config_vars['speed_sensitivity'].get()
            self.config.steering_sensitivity = self.config_vars['steering_sensitivity'].get()
            self.config.pedal_sensitivity = self.config_vars['pedal_sensitivity'].get()
            
            # 如果系统正在运行，更新配置
            if self.music_system:
                self.music_system.update_config(self.config)
            
            self._log("配置已应用")
            
        except Exception as e:
            self._log(f"应用配置时发生错误: {e}")
            messagebox.showerror("错误", f"应用配置时发生错误: {e}")
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            filename = filedialog.asksaveasfilename(
                title="保存配置文件",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if filename:
                config_dict = {
                    'update_rate': self.config_vars['update_rate'].get(),
                    'osc_port': self.config_vars['osc_port'].get(),
                    'bpm_min': self.config_vars['bpm_min'].get(),
                    'bpm_max': self.config_vars['bpm_max'].get(),
                    'speed_sensitivity': self.config_vars['speed_sensitivity'].get(),
                    'steering_sensitivity': self.config_vars['steering_sensitivity'].get(),
                    'pedal_sensitivity': self.config_vars['pedal_sensitivity'].get()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
                self._log(f"配置已保存到: {filename}")
                
        except Exception as e:
            self._log(f"保存配置时发生错误: {e}")
            messagebox.showerror("错误", f"保存配置时发生错误: {e}")
    
    def _load_config_dialog(self):
        """从文件加载配置"""
        try:
            filename = filedialog.askopenfilename(
                title="加载配置文件",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if filename:
                self._load_config(filename)
                
        except Exception as e:
            self._log(f"加载配置时发生错误: {e}")
            messagebox.showerror("错误", f"加载配置时发生错误: {e}")
    
    def _load_config(self, filename: Optional[str] = None):
        """加载配置"""
        try:
            if filename is None:
                # 尝试加载默认配置文件
                default_config = os.path.join(os.path.dirname(__file__), 'music_config.json')
                if not os.path.exists(default_config):
                    return
                filename = default_config
            
            with open(filename, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 更新GUI控件
            for key, value in config_dict.items():
                if key in self.config_vars:
                    self.config_vars[key].set(value)
            
            self._log(f"配置已从文件加载: {filename}")
            
        except FileNotFoundError:
            pass  # 配置文件不存在，使用默认值
        except Exception as e:
            self._log(f"加载配置时发生错误: {e}")
    
    def _clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
    
    def _log(self, message: str):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
        # 限制日志行数
        lines = int(self.log_text.index(tk.END).split('.')[0])
        if lines > 1000:
            self.log_text.delete(1.0, "100.0")
    
    def _start_status_update(self):
        """启动状态更新线程"""
        self.stop_status_update = False
        self.status_update_thread = threading.Thread(target=self._status_update_loop, daemon=True)
        self.status_update_thread.start()
    
    def _status_update_loop(self):
        """状态更新循环"""
        while not self.stop_status_update:
            try:
                self._update_status()
                time.sleep(1)  # 每秒更新一次
            except Exception as e:
                print(f"状态更新错误: {e}")
    
    def _update_status(self):
        """更新状态显示"""
        try:
            if self.music_system:
                status = self.music_system.get_status()
                
                # 更新状态标签
                self.status_vars['system'].set("运行中" if status['running'] else "已停止")
                self.status_vars['telemetry'].set("已连接" if status['telemetry_connected'] else "未连接")
                self.status_vars['music_engine'].set("运行中" if status['music_engine_running'] else "未运行")
                
                if status['last_data_time']:
                    self.status_vars['last_update'].set(time.strftime("%H:%M:%S", time.localtime(status['last_data_time'])))
                
                # 更新数据显示（这里需要实际的遥测数据）
                # 暂时使用模拟数据
                if status['running']:
                    self._update_telemetry_display()
            else:
                # 系统未运行
                self.status_vars['system'].set("已停止")
                self.status_vars['telemetry'].set("未连接")
                self.status_vars['music_engine'].set("未运行")
                self.status_vars['last_update'].set("无")
                
        except Exception as e:
            print(f"更新状态时发生错误: {e}")
    
    def _update_telemetry_display(self):
        """更新遥测数据显示"""
        # 这里应该从音乐系统获取实际的遥测数据
        # 暂时使用模拟数据
        import random
        
        if self.is_running:
            self.data_vars['speed'].set(f"{random.randint(0, 200)} km/h")
            self.data_vars['rpm'].set(f"{random.randint(1000, 8000)} RPM")
            self.data_vars['gear'].set(f"{random.randint(1, 6)}")
            self.data_vars['throttle'].set(f"{random.randint(0, 100)}%")
            self.data_vars['brake'].set(f"{random.randint(0, 100)}%")
            self.data_vars['steer'].set(f"{random.randint(-45, 45)}°")
        else:
            for var in self.data_vars.values():
                var.set("0")
    
    def _on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            if messagebox.askokcancel("退出", "音乐系统正在运行，确定要退出吗？"):
                self._stop_system()
                self.stop_status_update = True
                self.root.destroy()
        else:
            self.stop_status_update = True
            self.root.destroy()
    
    def run(self):
        """运行GUI主循环"""
        self.root.mainloop()


def main():
    """主函数"""
    # 创建并运行GUI
    root = tk.Tk()
    app = MusicControlGUI(root)
    app.run()


if __name__ == "__main__":
    main()