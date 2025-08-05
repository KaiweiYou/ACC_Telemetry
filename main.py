#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC Telemetry 主程序
提供GUI界面，用户可以选择不同的功能模式
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class ACCTelemetryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ACC 遥测数据工具")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 设置窗口居中
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """创建主界面组件"""
        # 主标题
        title_label = ttk.Label(
            self.root, 
            text="ACC 遥测数据工具", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # 版本信息
        version_label = ttk.Label(
            self.root, 
            text="版本 1.0.0", 
            font=("Arial", 10)
        )
        version_label.pack(pady=(0, 20))
        
        # 功能按钮区域
        self.create_function_buttons()
        
        # 分隔线
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=20)
        
        # 底部信息
        info_label = ttk.Label(
            self.root, 
            text="请确保 ACC 游戏正在运行", 
            font=("Arial", 9),
            foreground="gray"
        )
        info_label.pack(pady=(0, 10))
        
    def create_function_buttons(self):
        """创建功能按钮"""
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        # 仪表盘模式
        dashboard_frame = ttk.LabelFrame(button_frame, text="仪表盘模式", padding=15)
        dashboard_frame.pack(fill='x', pady=(0, 15))
        
        dashboard_desc = ttk.Label(
            dashboard_frame, 
            text="显示实时遥测数据的图形界面",
            font=("Arial", 9)
        )
        dashboard_desc.pack(pady=(0, 10))
        
        dashboard_btn = ttk.Button(
            dashboard_frame, 
            text="启动仪表盘", 
            command=self.run_dashboard_mode,
            style='Accent.TButton'
        )
        dashboard_btn.pack()
        
        # OSC发送模式
        osc_frame = ttk.LabelFrame(button_frame, text="OSC 数据发送", padding=15)
        osc_frame.pack(fill='x', pady=(0, 15))
        
        osc_desc = ttk.Label(
            osc_frame, 
            text="通过OSC协议发送遥测数据到指定设备",
            font=("Arial", 9)
        )
        osc_desc.pack(pady=(0, 10))
        
        osc_btn = ttk.Button(
            osc_frame, 
            text="启动OSC发送", 
            command=self.run_osc_mode,
            style='Accent.TButton'
        )
        osc_btn.pack()
        
    def run_dashboard_mode(self):
        """启动仪表盘模式"""
        try:
            # 在新进程中启动仪表盘
            subprocess.Popen([sys.executable, "-c", 
                            "from acc_telemetry.ui.dashboard import AccDashboard; AccDashboard().run()"])
            messagebox.showinfo("成功", "仪表盘已在新窗口中启动")
        except Exception as e:
            messagebox.showerror("错误", f"启动仪表盘失败: {e}")
            
    def run_osc_mode(self):
        """启动OSC发送模式"""
        self.show_osc_config_dialog()
        
    def show_osc_config_dialog(self):
        """显示OSC配置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("OSC 配置")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"300x200+{x}+{y}")
        
        # IP地址输入
        ttk.Label(dialog, text="目标IP地址:").pack(pady=(20, 5))
        ip_var = tk.StringVar(value="192.168.10.66")
        ip_entry = ttk.Entry(dialog, textvariable=ip_var, width=20)
        ip_entry.pack(pady=(0, 10))
        
        # 端口输入
        ttk.Label(dialog, text="目标端口:").pack(pady=(0, 5))
        port_var = tk.StringVar(value="8000")
        port_entry = ttk.Entry(dialog, textvariable=port_var, width=20)
        port_entry.pack(pady=(0, 20))
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack()
        
        def start_osc():
            ip = ip_var.get().strip()
            port = port_var.get().strip()
            
            if not ip or not port:
                messagebox.showerror("错误", "请填写完整的IP地址和端口")
                return
                
            try:
                port_int = int(port)
                if port_int < 1 or port_int > 65535:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("错误", "端口必须是1-65535之间的整数")
                return
                
            try:
                # 在新进程中启动OSC发送器
                subprocess.Popen([sys.executable, "-c", 
                                f"from acc_telemetry.utils.osc_sender import ACCDataSender; ACCDataSender('{ip}', {port_int}).run()"])
                messagebox.showinfo("成功", f"OSC发送器已启动\n目标地址: {ip}:{port_int}")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"启动OSC发送器失败: {e}")
        
        ttk.Button(button_frame, text="启动", command=start_osc).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side='left')
        
    def run(self):
        """运行主程序"""
        self.root.mainloop()

def main():
    """主函数"""
    # 检查是否在正确的目录中
    if not os.path.exists('acc_telemetry'):
        print("错误: 请在项目根目录中运行此程序")
        sys.exit(1)
        
    # 启动GUI
    app = ACCTelemetryGUI()
    app.run()

if __name__ == "__main__":
    main()