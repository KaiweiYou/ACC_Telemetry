#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC Telemetry 主程序
提供现代化GUI界面，用户可以选择不同的功能模式
"""

__version__ = "1.0.0"

import logging
import os
import subprocess
import sys
import threading

import customtkinter as ctk
from PIL import Image, ImageTk

# 导入自定义模块
from acc_telemetry.utils.config import get_config
from acc_telemetry.utils.error_handling import setup_exception_handling
from acc_telemetry.utils.logging_config import setup_logging

# 初始化配置和日志
config = get_config()
logger = setup_logging("acc_telemetry", log_to_console=True)
setup_exception_handling()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 从配置中获取应用设置
        app_title = config.get_str("APP_TITLE", "ACC Telemetry")
        app_width = config.get_int("APP_WIDTH", 1200)
        app_height = config.get_int("APP_HEIGHT", 800)

        logger.info(f"启动应用程序: {app_title} v{__version__}")

        self.title(app_title)
        self.geometry(f"{app_width}x{app_height}")
        self.center_window(app_width, app_height)

        # 绑定窗口关闭事件，确保资源被正确释放
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # 记录应用程序启动完成
        logger.debug("应用程序界面初始化完成")
        # 创建主容器
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建左侧菜单栏
        self.create_sidebar()

        # 创建右侧内容区域
        self.content_area = ctk.CTkFrame(self.main_container, corner_radius=15)
        self.content_area.pack(side="left", fill="both", expand=True)

        # 组件缓存，避免重复创建
        self._content_cache = {}
        
        # 初始化时显示默认标签页
        self.current_tab = ctk.StringVar(value="")  # 初始为空，确保首次加载
        # 延迟加载，确保UI完全初始化
        self.after(100, lambda: self.switch_tab("dashboard"))

    def center_window(self, width=1200, height=800):
        """将窗口居中显示

        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def run_dashboard_mode(self):
        """启动仪表盘模式"""
        try:
            # 在新进程中启动仪表盘
            subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    "from acc_telemetry.ui.dashboard import AccDashboard; AccDashboard().run()",
                ]
            )
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
            sidebar, text="🚀 功能菜单", font=ctk.CTkFont(size=20, weight="bold")
        )
        menu_title.pack(pady=(30, 20), padx=20)

        # 菜单按钮
        menu_buttons_data = [
            {"id": "dashboard", "text": "📊 实时仪表盘"},
            {"id": "telemetry", "text": "🔧 遥测配置"},
            {"id": "web", "text": "🌐 Web 遥测面板"},
            {"id": "osc", "text": "📡 OSC 数据流"},
            {"id": "music", "text": "🎵 音乐控制"},
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
                border_spacing=10,
            )
            button.pack(fill="x", padx=15, pady=8)
            self.menu_buttons[item["id"]] = button

    def switch_tab(self, new_tab):
        """切换标签页 - 简化版，无加载提示"""
        if self.current_tab.get() == new_tab:
            return

        self.current_tab.set(new_tab)

        # 直接获取或创建内容
        content_widget = self._get_or_create_content(new_tab)
        if content_widget:
            self._show_content(content_widget)

        # 更新菜单按钮状态
        self.update_menu_buttons(self.menu_buttons, new_tab)

    def _get_or_create_content(self, tab_name):
        """获取或创建内容组件 - 使用缓存避免重复创建"""
        try:
            # 检查缓存
            if tab_name in self._content_cache:
                cached_widget = self._content_cache[tab_name]
                if cached_widget.winfo_exists():
                    return cached_widget
                else:
                    # 组件已销毁，从缓存中移除
                    del self._content_cache[tab_name]
            
            # 创建新组件
            content = self._create_content_sync(tab_name)
            if content:
                self._content_cache[tab_name] = content
            return content
        except Exception as e:
            logger.error(f"创建 {tab_name} 页面失败: {e}")
            return self._create_error_page(tab_name, str(e))

    def _show_content(self, content_widget):
        """显示指定组件，清理其他组件但保留缓存"""
        if not content_widget:
            return
            
        # 清理内容区域的所有子组件（但不销毁缓存的组件）
        for widget in self.content_area.winfo_children():
            try:
                widget.pack_forget()  # 隐藏而非销毁
            except Exception as e:
                logger.warning(f"隐藏组件时出错: {e}")
        
        # 确保组件存在且有效
        if content_widget.winfo_exists():
            # 如果组件已有父容器，先移除
            if content_widget.winfo_parent():
                content_widget.pack_forget()
            
            # 显示新组件
            content_widget.pack(fill="both", expand=True)
            self.content_area.update_idletasks()

    def _create_error_page(self, tab_name, error_msg):
        """创建错误页面"""
        error_frame = ctk.CTkFrame(self.content_area)
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=f"加载 {tab_name} 失败\n{error_msg}",
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        error_label.pack(expand=True)
        
        return error_frame

    def _show_loading_indicator(self, tab_name):
        """显示加载指示器（已废弃，保留空方法）"""
        pass

    def _create_content_sync(self, tab_name):
        """同步创建组件内容"""
        try:
            content_widget = None
            
            # 根据标签页创建对应内容
            if tab_name == "dashboard":
                content_widget = self.create_dashboard_content(self.content_area)
            elif tab_name == "telemetry":
                content_widget = self.create_telemetry_content(self.content_area)
            elif tab_name == "web":
                content_widget = self.create_web_content(self.content_area)
            elif tab_name == "osc":
                content_widget = self.create_osc_content(self.content_area)
            elif tab_name == "music":
                content_widget = self.create_music_content(self.content_area)
            
            return content_widget
                
        except Exception as e:
            logger.error(f"创建 {tab_name} 页面失败: {e}")
            return self._create_error_page(tab_name, str(e))

    def _show_error_page(self, tab_name, error_msg):
        """显示错误页面"""
        error_frame = ctk.CTkFrame(self.content_area)
        error_frame.pack(fill="both", expand=True)
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=f"加载 {tab_name} 失败\n{error_msg}",
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        error_label.pack(expand=True)

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
        return dashboard

    def create_telemetry_content(self, parent):
        """创建遥测配置内容页面"""
        from acc_telemetry.ui.telemetry_settings import TelemetrySettings

        settings_frame = TelemetrySettings(parent, self)
        return settings_frame

    def create_web_content(self, parent):
        """创建Web遥测面板内容页面"""
        import socket
        import threading

        # 创建主容器
        web_frame = ctk.CTkFrame(parent)

        # Web服务器进程跟踪
        self.web_server = None
        self.web_server_thread = None

        # 标题
        title = ctk.CTkLabel(
            web_frame, text="🌐 Web 遥测面板", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(30, 10))

        # 描述
        desc = ctk.CTkLabel(
            web_frame,
            text="启动Web服务器，通过浏览器访问实时遥测数据\n支持手机、平板等移动设备访问",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30"),
        )
        desc.pack(pady=(0, 20))

        # Web服务器配置表单
        form_frame = ctk.CTkFrame(web_frame, corner_radius=15)
        form_frame.pack(fill="x", padx=40, pady=20)

        # 端口配置
        port_label = ctk.CTkLabel(
            form_frame, text="🔌 服务器端口", font=ctk.CTkFont(size=16, weight="bold")
        )
        port_label.pack(anchor="w", padx=20, pady=(20, 5))

        port_var = ctk.StringVar(value="8080")
        port_entry = ctk.CTkEntry(
            form_frame,
            textvariable=port_var,
            placeholder_text="例如: 8080",
            height=40,
            font=ctk.CTkFont(size=14),
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
            access_frame, text="📱 访问地址", font=ctk.CTkFont(size=16, weight="bold")
        )
        access_label.pack(anchor="w", pady=(0, 10))

        local_access = ctk.CTkLabel(
            access_frame,
            text=f"本机访问: http://localhost:{port_var.get()}",
            font=ctk.CTkFont(size=14),
            text_color=("#4CAF50", "#4CAF50"),
        )
        local_access.pack(anchor="w", pady=2)

        network_access = ctk.CTkLabel(
            access_frame,
            text=f"局域网访问: http://{local_ip}:{port_var.get()}",
            font=ctk.CTkFont(size=14),
            text_color=("#2196F3", "#2196F3"),
        )
        network_access.pack(anchor="w", pady=2)

        # 更新访问地址的函数
        def update_access_urls(*args):
            port = port_var.get()
            local_access.configure(text=f"本机访问: http://localhost:{port}")
            network_access.configure(text=f"局域网访问: http://{local_ip}:{port}")

        port_var.trace("w", update_access_urls)

        # 状态显示
        status_frame = ctk.CTkFrame(web_frame, corner_radius=15)
        status_frame.pack(fill="x", padx=40, pady=(0, 20))

        status_label = ctk.CTkLabel(
            status_frame,
            text="🔴 服务器未启动",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        status_label.pack(pady=20)

        # 控制按钮
        button_frame = ctk.CTkFrame(web_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=40, pady=20)

        def start_web_server():
            try:
                port = int(port_var.get())

                from acc_telemetry.web import WebTelemetryServer

                self.web_server = WebTelemetryServer(host="0.0.0.0", port=port)

                def run_server():
                    try:
                        self.web_server.start()
                    except Exception as e:
                        self.after(
                            0, lambda: self.show_error_dialog(f"Web服务器启动失败: {e}")
                        )
                        self.after(
                            0, lambda: status_label.configure(text="🔴 服务器启动失败")
                        )

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
            hover_color="#45a049",
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
            hover_color="#da190b",
        )
        stop_btn.pack(side="left", padx=(10, 10), fill="x", expand=True)

        open_btn = ctk.CTkButton(
            button_frame,
            text="🌐 打开浏览器",
            command=open_browser,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#2196F3",
            hover_color="#1976D2",
        )
        open_btn.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # 使用说明
        info_frame = ctk.CTkFrame(web_frame, corner_radius=15)
        info_frame.pack(fill="x", padx=40, pady=(0, 20))

        info_title = ctk.CTkLabel(
            info_frame, text="📋 使用说明", font=ctk.CTkFont(size=16, weight="bold")
        )
        info_title.pack(anchor="w", padx=20, pady=(20, 10))

        info_text = ctk.CTkLabel(
            info_frame,
            text="1. 确保ACC游戏正在运行\n2. 点击'启动服务器'按钮\n3. 在浏览器中访问显示的地址\n4. 手机访问请使用局域网地址\n5. 确保防火墙允许端口访问",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30"),
            justify="left",
        )
        info_text.pack(anchor="w", padx=20, pady=(0, 20))

        return web_frame

    def create_osc_content(self, parent):
        """创建OSC配置内容页面"""
        # OSC进程跟踪
        self.osc_process = None

        # 创建主容器
        osc_frame = ctk.CTkFrame(parent)

        # 标题
        title = ctk.CTkLabel(
            osc_frame, text="🌐 OSC 数据流", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(30, 10))

        # 描述
        desc = ctk.CTkLabel(
            osc_frame,
            text="通过OSC协议实时传输遥测数据到外部设备",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30"),
        )
        desc.pack(pady=(0, 20))

        # OSC配置表单
        form_frame = ctk.CTkFrame(osc_frame, corner_radius=15)
        form_frame.pack(fill="x", padx=40, pady=20)

        # IP地址配置
        ip_label = ctk.CTkLabel(
            form_frame, text="🌐 目标IP地址", font=ctk.CTkFont(size=16, weight="bold")
        )
        ip_label.pack(anchor="w", padx=20, pady=(20, 5))

        ip_var = ctk.StringVar(value="127.0.0.1")
        ip_entry = ctk.CTkEntry(
            form_frame,
            textvariable=ip_var,
            placeholder_text="例如: 192.168.1.100",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        ip_entry.pack(fill="x", padx=20, pady=(0, 15))

        # 端口配置
        port_label = ctk.CTkLabel(
            form_frame, text="🔌 目标端口", font=ctk.CTkFont(size=16, weight="bold")
        )
        port_label.pack(anchor="w", padx=20, pady=(0, 5))

        port_var = ctk.StringVar(value="8000")
        port_entry = ctk.CTkEntry(
            form_frame,
            textvariable=port_var,
            placeholder_text="例如: 8000",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        port_entry.pack(fill="x", padx=20, pady=(0, 20))

        # 状态显示标签
        status_label = ctk.CTkLabel(
            osc_frame,
            text="状态: 未启动",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray70", "gray30"),
        )
        status_label.pack(pady=(10, 0))

        # 错误提示标签
        error_label = ctk.CTkLabel(
            osc_frame, text="", font=ctk.CTkFont(size=13), text_color="#e74c3c"
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
                self.osc_process = subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        f"from acc_telemetry.utils.osc_sender import ACCDataSender; ACCDataSender('{ip}', {port_int}).run()",
                    ]
                )

                # 更新状态和按钮
                status_label.configure(
                    text=f"状态: 正在发送到 {ip}:{port_int}", text_color="#2ca02c"
                )
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
                status_label.configure(
                    text="状态: 已停止", text_color=("gray70", "gray30")
                )
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
        button_frame = ctk.CTkFrame(osc_frame, fg_color="transparent")
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
            hover_color="#28a028",
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
            state="disabled",
        )
        stop_btn.pack(side="left", padx=(10, 0))

        return osc_frame

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
            text_color="#e74c3c",
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            dialog, text=message, font=ctk.CTkFont(size=14), wraplength=350
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
            hover_color="#c0392b",
        ).pack(pady=20)

    def create_music_content(self, parent):
        """创建音乐控制内容页面

        集成 MBUX Sound Drive 的音乐控制面板，提供启动/停止与参数监控。
        """
        # 创建主容器
        music_frame = ctk.CTkFrame(parent)

        # 标题
        title = ctk.CTkLabel(
            music_frame, text="🎵 MBUX Sound Drive", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(30, 10))

        # 描述
        desc = ctk.CTkLabel(
            music_frame,
            text="ACC 音乐同步系统 - 让音乐与驾驶完美融合\n支持分轨播放和实时同步",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30"),
        )
        desc.pack(pady=(0, 20))

        # 创建音乐控制面板
        from acc_telemetry.ui.music_control import MusicControlPanel
        panel = MusicControlPanel(music_frame)
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        return music_frame

    def on_close(self):
        """窗口关闭回调，清理子页面资源并安全退出"""
        logger.info("应用程序正在关闭，清理资源...")
        try:
            # 清理页面组件（如音乐控制面板）
            if hasattr(self, "_page_contents"):
                for widget in list(self._page_contents.values()):
                    try:
                        if hasattr(widget, "cleanup") and callable(widget.cleanup):
                            widget.cleanup()
                    except Exception as e:
                        logger.error(f"清理组件出错: {e}")

            # 停止 Web 服务器
            if hasattr(self, "web_server") and self.web_server:
                try:
                    logger.debug("正在停止Web服务器...")
                    self.web_server.stop()
                except Exception as e:
                    logger.warning(f"停止Web服务器时出错: {e}")
                self.web_server = None

            # 终止 OSC 进程
            if hasattr(self, "osc_process") and self.osc_process:
                try:
                    logger.debug("正在终止OSC进程...")
                    if self.osc_process.poll() is None:
                        self.osc_process.terminate()
                except Exception as e:
                    logger.warning(f"终止OSC进程时出错: {e}")
                self.osc_process = None

            logger.info("应用程序已安全关闭")
        finally:
            # 销毁窗口
            self.destroy()


def main():
    """主函数"""
    try:
        # 检查是否在正确的目录中
        if not os.path.exists("acc_telemetry"):
            logger.error("错误: 请在项目根目录中运行此程序")
            return 1

        # 记录启动信息
        logger.info(f"ACC Telemetry v{__version__} 启动中...")
        logger.debug(f"调试模式: {config.get_bool('APP_DEBUG', False)}")

        # 启动GUI
        app = App()
        app.mainloop()

        return 0
    except Exception as e:
        logger.critical(f"程序启动失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
