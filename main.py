#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC Telemetry 主程序
提供现代化GUI界面，用户可以选择不同的功能模式
"""

import customtkinter as ctk

import subprocess
import sys
import os
from PIL import Image, ImageTk
import threading

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ACC Telemetry")
        self.geometry("1200x800")
        self.center_window()

        # 创建主容器
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建左侧菜单栏
        self.create_sidebar()

        # 创建右侧内容区域
        self.content_area = ctk.CTkFrame(self.main_container, corner_radius=15)
        self.content_area.pack(side="left", fill="both", expand=True)

        # 初始化时显示默认标签页
        self.current_tab = ctk.StringVar(value="dashboard")
        self.switch_tab("dashboard")
        

    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        # 使用设定的窗口尺寸而不是当前尺寸
        width = 1200
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        

        

            

        
    def run_dashboard_mode(self):
        """启动仪表盘模式"""
        try:
            # 在新进程中启动仪表盘
            subprocess.Popen([sys.executable, "-c", 
                            "from acc_telemetry.ui.dashboard import AccDashboard; AccDashboard().run()"])
        except Exception as e:
            self.show_error_dialog(f"启动仪表盘失败: {e}")
            
    def open_telemetry_settings(self):
        """打开遥测面板设置窗口"""
        try:
            from acc_telemetry.ui.telemetry_settings import TelemetrySettings
            settings_window = TelemetrySettings(self)
            # 不需要调用run()，因为它是模态对话框
        except Exception as e:
            # 显示现代化错误对话框
            self.show_error_dialog(f"打开设置窗口失败: {e}")
            
    def create_sidebar(self):
        """创建左侧菜单栏"""
        sidebar = ctk.CTkFrame(self.main_container, width=200, corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=(0, 10))

        # 菜单标题
        menu_title = ctk.CTkLabel(
            sidebar,
            text="🚀 功能菜单",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        menu_title.pack(pady=(30, 20), padx=20)

        # 菜单按钮
        menu_buttons_data = [
            {"id": "dashboard", "text": "📊 实时仪表盘"},
            {"id": "telemetry", "text": "🔧 遥测配置"},
            {"id": "web", "text": "🌐 Web 遥测面板"},
            {"id": "osc", "text": "📡 OSC 数据流"},
            {"id": "music", "text": "🎵 交互音乐"}
        ]

        self.menu_buttons = {}
        for item in menu_buttons_data:
            button = ctk.CTkButton(
                sidebar,
                text=item["text"],
                command=lambda new_tab=item["id"]: self.switch_tab(new_tab),
                font=ctk.CTkFont(size=14, weight="bold"),
                height=45,
                corner_radius=10,
                anchor="w",
                border_spacing=10
            )
            button.pack(fill="x", padx=15, pady=8)
            self.menu_buttons[item["id"]] = button
    
    def switch_tab(self, new_tab):
        """切换标签页"""
        # 清空内容区域
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # 更新当前标签页
        self.current_tab.set(new_tab)
        
        # 根据标签页显示对应内容
        if new_tab == 'dashboard':
            self.create_dashboard_content(self.content_area)
        elif new_tab == 'telemetry':
            self.create_telemetry_content(self.content_area)
        elif new_tab == 'web':
            self.create_web_content(self.content_area)
        elif new_tab == 'osc':
            self.create_osc_content(self.content_area)
        elif new_tab == 'music':
            self.create_music_content(self.content_area)
        
        # 更新菜单按钮状态
        self.update_menu_buttons(self.menu_buttons, new_tab)
    
    def update_menu_buttons(self, menu_buttons, active_tab):
        """更新菜单按钮状态"""
        for tab_id, button in menu_buttons.items():
            if tab_id == active_tab:
                button.configure(fg_color=("#1f538d", "#14375e"))
            else:
                button.configure(fg_color=("#3a7ebf", "#1f538d"))
    
    def create_dashboard_content(self, parent):
        """创建仪表盘内容页面"""
        from acc_telemetry.ui.dashboard import AccDashboard
        dashboard = AccDashboard(parent)
        dashboard.pack(fill="both", expand=True)
    
    def create_telemetry_content(self, parent):
        """创建遥测配置内容页面"""
        from acc_telemetry.ui.telemetry_settings import TelemetrySettings
        settings_frame = TelemetrySettings(parent, self)
        settings_frame.pack(fill="both", expand=True)
    
    def create_web_content(self, parent):
        """创建Web遥测面板内容页面"""
        import socket
        import threading
        
        # Web服务器进程跟踪
        self.web_server = None
        self.web_server_thread = None
        
        # 标题
        title = ctk.CTkLabel(
            parent,
            text="🌐 Web 遥测面板",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(30, 10))
        
        # 描述
        desc = ctk.CTkLabel(
            parent,
            text="启动Web服务器，通过浏览器访问实时遥测数据\n支持手机、平板等移动设备访问",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30")
        )
        desc.pack(pady=(0, 20))
        
        # Web服务器配置表单
        form_frame = ctk.CTkFrame(parent, corner_radius=15)
        form_frame.pack(fill="x", padx=40, pady=20)
        
        # 端口配置
        port_label = ctk.CTkLabel(
            form_frame,
            text="🔌 服务器端口",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        port_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        port_var = ctk.StringVar(value="8080")
        port_entry = ctk.CTkEntry(
            form_frame,
            textvariable=port_var,
            placeholder_text="例如: 8080",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        port_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # 获取本机IP地址
        def get_local_ip():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except Exception:
                return "127.0.0.1"
        
        local_ip = get_local_ip()
        
        # 访问地址显示
        access_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        access_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        access_label = ctk.CTkLabel(
            access_frame,
            text="📱 访问地址",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        access_label.pack(anchor="w", pady=(0, 10))
        
        local_access = ctk.CTkLabel(
            access_frame,
            text=f"本机访问: http://localhost:{port_var.get()}",
            font=ctk.CTkFont(size=14),
            text_color=("#4CAF50", "#4CAF50")
        )
        local_access.pack(anchor="w", pady=2)
        
        network_access = ctk.CTkLabel(
            access_frame,
            text=f"局域网访问: http://{local_ip}:{port_var.get()}",
            font=ctk.CTkFont(size=14),
            text_color=("#2196F3", "#2196F3")
        )
        network_access.pack(anchor="w", pady=2)
        
        # 更新访问地址的函数
        def update_access_urls(*args):
            port = port_var.get()
            local_access.configure(text=f"本机访问: http://localhost:{port}")
            network_access.configure(text=f"局域网访问: http://{local_ip}:{port}")
        
        port_var.trace("w", update_access_urls)
        
        # 状态显示
        status_frame = ctk.CTkFrame(parent, corner_radius=15)
        status_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="🔴 服务器未启动",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_label.pack(pady=20)
        
        # 控制按钮
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=40, pady=20)
        
        def start_web_server():
            try:
                port = int(port_var.get())
                
                from acc_telemetry.web import WebTelemetryServer
                self.web_server = WebTelemetryServer(host='0.0.0.0', port=port)
                
                def run_server():
                    try:
                        self.web_server.start()
                    except Exception as e:
                        self.after(0, lambda: self.show_error_dialog(f"Web服务器启动失败: {e}"))
                        self.after(0, lambda: status_label.configure(text="🔴 服务器启动失败"))
                
                self.web_server_thread = threading.Thread(target=run_server)
                self.web_server_thread.daemon = True
                self.web_server_thread.start()
                
                status_label.configure(text="🟢 服务器运行中")
                start_btn.configure(state="disabled")
                stop_btn.configure(state="normal")
                
            except ValueError:
                self.show_error_dialog("请输入有效的端口号")
            except Exception as e:
                self.show_error_dialog(f"启动失败: {e}")
        
        def stop_web_server():
            try:
                if self.web_server:
                    self.web_server.stop()
                    self.web_server = None
                
                status_label.configure(text="🔴 服务器已停止")
                start_btn.configure(state="normal")
                stop_btn.configure(state="disabled")
                
            except Exception as e:
                self.show_error_dialog(f"停止失败: {e}")
        
        def open_browser():
            import webbrowser
            port = port_var.get()
            webbrowser.open(f"http://localhost:{port}")
        
        start_btn = ctk.CTkButton(
            button_frame,
            text="🚀 启动服务器",
            command=start_web_server,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        start_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        stop_btn = ctk.CTkButton(
            button_frame,
            text="🛑 停止服务器",
            command=stop_web_server,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            state="disabled",
            fg_color="#f44336",
            hover_color="#da190b"
        )
        stop_btn.pack(side="left", padx=(10, 10), fill="x", expand=True)
        
        open_btn = ctk.CTkButton(
            button_frame,
            text="🌐 打开浏览器",
            command=open_browser,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        open_btn.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # 使用说明
        info_frame = ctk.CTkFrame(parent, corner_radius=15)
        info_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        info_title = ctk.CTkLabel(
            info_frame,
            text="📋 使用说明",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        info_text = ctk.CTkLabel(
            info_frame,
            text="1. 确保ACC游戏正在运行\n2. 点击'启动服务器'按钮\n3. 在浏览器中访问显示的地址\n4. 手机访问请使用局域网地址\n5. 确保防火墙允许端口访问",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30"),
            justify="left"
        )
        info_text.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_osc_content(self, parent):
        """创建OSC配置内容页面"""
        # OSC进程跟踪
        self.osc_process = None
        
        # 标题
        title = ctk.CTkLabel(
            parent,
            text="🌐 OSC 数据流",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(30, 10))
        
        # 描述
        desc = ctk.CTkLabel(
            parent,
            text="通过OSC协议实时传输遥测数据到外部设备",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30")
        )
        desc.pack(pady=(0, 20))
        
        # OSC配置表单
        form_frame = ctk.CTkFrame(parent, corner_radius=15)
        form_frame.pack(fill="x", padx=40, pady=20)
        
        # IP地址配置
        ip_label = ctk.CTkLabel(
            form_frame,
            text="🌐 目标IP地址",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ip_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        ip_var = ctk.StringVar(value="127.0.0.1")
        ip_entry = ctk.CTkEntry(
            form_frame,
            textvariable=ip_var,
            placeholder_text="例如: 192.168.1.100",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        ip_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # 端口配置
        port_label = ctk.CTkLabel(
            form_frame,
            text="🔌 目标端口",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        port_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        port_var = ctk.StringVar(value="8000")
        port_entry = ctk.CTkEntry(
            form_frame,
            textvariable=port_var,
            placeholder_text="例如: 8000",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        port_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # 状态显示标签
        status_label = ctk.CTkLabel(
            parent,
            text="状态: 未启动",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray70", "gray30")
        )
        status_label.pack(pady=(10, 0))
        
        # 错误提示标签
        error_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#e74c3c"
        )
        
        def start_osc_transmission():
            ip = ip_var.get().strip()
            port = port_var.get().strip()
            
            if not ip or not port:
                error_label.configure(text="请填写完整的IP地址和端口")
                error_label.pack(pady=(0, 10))
                return
                
            try:
                port_int = int(port)
                if port_int < 1 or port_int > 65535:
                    raise ValueError()
            except ValueError:
                error_label.configure(text="端口必须是1-65535之间的整数")
                error_label.pack(pady=(0, 10))
                return
                
            try:
                # 在新进程中启动OSC发送器
                self.osc_process = subprocess.Popen([sys.executable, "-c", 
                                f"from acc_telemetry.utils.osc_sender import ACCDataSender; ACCDataSender('{ip}', {port_int}).run()"])
                
                # 更新状态和按钮
                status_label.configure(text=f"状态: 正在发送到 {ip}:{port_int}", text_color="#2ca02c")
                start_btn.configure(state="disabled")
                stop_btn.configure(state="normal")
                error_label.pack_forget()  # 隐藏错误信息
                
            except Exception as e:
                error_label.configure(text=f"启动OSC发送器失败: {e}")
                error_label.pack(pady=(0, 10))
        
        def stop_osc_transmission():
            try:
                if self.osc_process and self.osc_process.poll() is None:
                    self.osc_process.terminate()
                    self.osc_process.wait(timeout=5)  # 等待最多5秒
                    
                # 更新状态和按钮
                status_label.configure(text="状态: 已停止", text_color=("gray70", "gray30"))
                start_btn.configure(state="normal")
                stop_btn.configure(state="disabled")
                self.osc_process = None
                error_label.pack_forget()  # 隐藏错误信息
                
            except subprocess.TimeoutExpired:
                # 如果进程没有正常终止，强制杀死
                self.osc_process.kill()
                self.osc_process = None
                status_label.configure(text="状态: 强制停止", text_color="#e74c3c")
                start_btn.configure(state="normal")
                stop_btn.configure(state="disabled")
            except Exception as e:
                error_label.configure(text=f"停止OSC发送器失败: {e}")
                error_label.pack(pady=(0, 10))
        
        # 按钮容器
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # 启动按钮
        start_btn = ctk.CTkButton(
            button_frame,
            text="📡 启动发送",
            command=start_osc_transmission,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color="#2ca02c",
            hover_color="#28a028"
        )
        start_btn.pack(side="left", padx=(0, 10))
        
        # 停止按钮
        stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹️ 停止发送",
            command=stop_osc_transmission,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=150,
            corner_radius=15,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            state="disabled"
        )
        stop_btn.pack(side="left", padx=(10, 0))
    

        

    def create_music_content(self, parent):
        """创建交互音乐内容页面"""
        try:
            # 导入交互音乐GUI和遥测数据读取器
            from acc_telemetry.audio.music_gui import InteractiveMusicGUI
            from acc_telemetry.core.telemetry import ACCTelemetry
            
            # 初始化遥测数据读取器（如果还没有的话）
            if not hasattr(self, 'music_telemetry_reader'):
                self.music_telemetry_reader = ACCTelemetry()
                self.music_telemetry_reader.connect()
            
            # 创建遥测数据获取回调函数
            def get_telemetry_data():
                """获取当前遥测数据"""
                try:
                    # 从共享内存读取遥测数据，返回TelemetryData对象
                    return self.music_telemetry_reader.get_telemetry()
                except Exception as e:
                    print(f"获取遥测数据失败: {e}")
                    return None
            
            # 创建交互音乐界面
            music_gui = InteractiveMusicGUI(parent, get_telemetry_data)
            music_gui.pack(fill="both", expand=True)
            
            # 保存引用以便清理
            if not hasattr(self, 'music_guis'):
                self.music_guis = []
            self.music_guis.append(music_gui)
            
        except ImportError as e:
            # 如果导入失败，显示错误信息和安装指导
            self._show_music_import_error(parent, str(e))
        except Exception as e:
            # 其他错误
            self._show_music_general_error(parent, str(e))
    
    def _show_music_import_error(self, parent, error_msg: str):
        """显示音乐模块导入错误界面
        
        Args:
            parent: 父窗口
            error_msg: 错误消息
        """
        # 标题
        title = ctk.CTkLabel(
            parent,
            text="🎵 交互音乐功能",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(30, 10))
        
        # 错误信息
        error_frame = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffebee", "#4a1a1a"))
        error_frame.pack(fill="x", padx=40, pady=20)
        
        error_title = ctk.CTkLabel(
            error_frame,
            text="❌ 模块导入失败",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#d32f2f", "#f44336")
        )
        error_title.pack(pady=(20, 10))
        
        error_desc = ctk.CTkLabel(
            error_frame,
            text="交互音乐功能需要额外的音频库支持。\n请安装以下依赖包:",
            font=ctk.CTkFont(size=14),
            text_color=("#666666", "#cccccc")
        )
        error_desc.pack(pady=(0, 15))
        
        # 依赖包列表
        deps_frame = ctk.CTkFrame(error_frame, corner_radius=10)
        deps_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        deps_text = "pip install pygame numpy"
        deps_label = ctk.CTkLabel(
            deps_frame,
            text=deps_text,
            font=ctk.CTkFont(size=12, family="Consolas"),
            text_color=("#2e7d32", "#4caf50")
        )
        deps_label.pack(pady=10)
        
        # 安装按钮
        def install_dependencies():
            """安装依赖包"""
            try:
                import subprocess
                import sys
                
                # 显示安装进度
                install_btn.configure(text="正在安装...", state="disabled")
                
                def run_install():
                    try:
                        # 安装pygame
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
                        # 安装numpy
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
                        
                        # 安装成功
                        self.after(0, lambda: [
                            install_btn.configure(text="安装成功！", fg_color="#4caf50"),
                            self.after(2000, lambda: self.switch_tab('music'))  # 2秒后重新加载
                        ])
                    except subprocess.CalledProcessError as e:
                        self.after(0, lambda: [
                            install_btn.configure(text="安装失败", state="normal", fg_color="#f44336"),
                            self.show_error_dialog(f"依赖包安装失败: {e}")
                        ])
                
                # 在后台线程中运行安装
                threading.Thread(target=run_install, daemon=True).start()
                
            except Exception as e:
                self.show_error_dialog(f"安装过程出错: {e}")
        
        install_btn = ctk.CTkButton(
            error_frame,
            text="🔧 自动安装依赖",
            command=install_dependencies,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2196f3",
            hover_color="#1976d2"
        )
        install_btn.pack(pady=(0, 20))
        
        # 详细错误信息（可折叠）
        details_frame = ctk.CTkFrame(parent, corner_radius=15)
        details_frame.pack(fill="x", padx=40, pady=10)
        
        details_title = ctk.CTkLabel(
            details_frame,
            text="🔍 详细错误信息",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        details_title.pack(pady=(15, 5))
        
        details_text = ctk.CTkTextbox(
            details_frame,
            height=100,
            font=ctk.CTkFont(size=11, family="Consolas")
        )
        details_text.pack(fill="x", padx=15, pady=(0, 15))
        details_text.insert("1.0", error_msg)
        details_text.configure(state="disabled")
    
    def _show_music_general_error(self, parent, error_msg: str):
        """显示音乐功能一般错误界面
        
        Args:
            parent: 父窗口
            error_msg: 错误消息
        """
        # 标题
        title = ctk.CTkLabel(
            parent,
            text="🎵 交互音乐功能",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(30, 10))
        
        # 错误信息
        error_frame = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffebee", "#4a1a1a"))
        error_frame.pack(fill="x", padx=40, pady=20)
        
        error_title = ctk.CTkLabel(
            error_frame,
            text="⚠️ 功能初始化失败",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#ff9800", "#ffb74d")
        )
        error_title.pack(pady=(20, 10))
        
        error_desc = ctk.CTkLabel(
            error_frame,
            text="交互音乐功能初始化时遇到问题。\n请检查系统音频设备和相关配置。",
            font=ctk.CTkFont(size=14),
            text_color=("#666666", "#cccccc")
        )
        error_desc.pack(pady=(0, 15))
        
        # 重试按钮
        retry_btn = ctk.CTkButton(
            error_frame,
            text="🔄 重试",
            command=lambda: self.switch_tab('music'),
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#ff9800",
            hover_color="#f57c00"
        )
        retry_btn.pack(pady=(0, 20))
        
        # 详细错误信息
        details_frame = ctk.CTkFrame(parent, corner_radius=15)
        details_frame.pack(fill="x", padx=40, pady=10)
        
        details_title = ctk.CTkLabel(
            details_frame,
            text="🔍 错误详情",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        details_title.pack(pady=(15, 5))
        
        details_text = ctk.CTkTextbox(
            details_frame,
            height=80,
            font=ctk.CTkFont(size=11, family="Consolas")
        )
        details_text.pack(fill="x", padx=15, pady=(0, 15))
        details_text.insert("1.0", error_msg)
        details_text.configure(state="disabled")
        
    def show_error_dialog(self, message: str):
        """显示现代化错误对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("错误")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # 错误消息
        ctk.CTkLabel(
            dialog,
            text="❌ 操作失败",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e74c3c"
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        ).pack(pady=10)
        
        # 确认按钮
        ctk.CTkButton(
            dialog,
            text="确定",
            command=dialog.destroy,
            width=100,
            height=35,
            corner_radius=10,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(pady=20)
        


def main():
    """主函数"""
    # 检查是否在正确的目录中
    if not os.path.exists('acc_telemetry'):
        print("错误: 请在项目根目录中运行此程序")
        sys.exit(1)
        
    # 启动GUI
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()