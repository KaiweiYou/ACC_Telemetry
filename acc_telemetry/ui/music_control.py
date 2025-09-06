#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐控制面板组件

提供 MBUX Sound Drive 功能的用户界面和音乐库管理功能。

作者: Assistant
日期: 2024
"""

import threading
from typing import Any, Dict, Optional

import customtkinter as ctk

from acc_telemetry.audio import AudioConfig, MBUXSoundDriveController
from acc_telemetry.ui.music_library import MusicLibraryPanel


class MusicControlPanel(ctk.CTkFrame):
    """音乐控制面板类

    提供 MBUX Sound Drive 功能的图形界面控制，包括：
    - 启动/停止音乐引擎
    - 实时参数监控
    - 分轨音量控制、静音和独奏
    - 自动暂停/恢复设置
    - 淡入淡出控制
    - 日志设置控制
    - 基础配置调节
    - 状态显示
    """

    def __init__(self, parent: Any) -> None:
        """初始化音乐控制面板

        Args:
            parent: 父控件
        """
        super().__init__(parent, corner_radius=15)

        # 音乐控制器
        self.controller: Optional[MBUXSoundDriveController] = None
        self.is_running = False

        # UI 更新线程
        self.update_thread: Optional[threading.Thread] = None
        self.should_update = False

        # 分轨控制变量
        self.stem_volume_sliders: Dict[str, ctk.CTkSlider] = {}
        self.stem_mute_switches: Dict[str, ctk.CTkSwitch] = {}
        self.stem_solo_switches: Dict[str, ctk.CTkSwitch] = {}

        # 创建标签页界面
        self.create_tabbed_interface()

    def create_tabbed_interface(self) -> None:
        """创建标签页界面"""
        # 创建标签页容器
        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加标签页
        self.tabview.add("音乐库管理")
        self.tabview.add("MBUX 控制")

        # 创建音乐库管理面板
        self.music_library = MusicLibraryPanel(self.tabview.tab("音乐库管理"))
        self.music_library.pack(fill="both", expand=True)

        # 创建MBUX控制面板
        self.create_mbux_control_panel()

    def create_mbux_control_panel(self) -> None:
        """创建MBUX控制面板"""
        # 创建滚动框架以容纳所有控件
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.tabview.tab("MBUX 控制"), corner_radius=10
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 主标题
        title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="🎵 MBUX Sound Drive 音乐控制",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(20, 10))

        # 副标题描述
        desc_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="将驾驶输入转化为实时音乐表现，体验「驾驶即作曲」的沉浸式音乐体验",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30"),
        )
        desc_label.pack(pady=(0, 20))

        # 状态显示区域
        self.create_status_section()

        # 控制按钮区域
        self.create_control_section()

        # 分轨音量控制区域
        self.create_stems_control_section()

        # 自动暂停设置区域
        self.create_auto_pause_section()

        # 淡入淡出设置区域
        self.create_fade_section()

        # 日志设置区域
        self.create_logging_section()

        # 参数监控区域
        self.create_monitoring_section()

        # 配置调节区域
        self.create_config_section()

    def create_widgets(self) -> None:
        """创建界面组件（保留兼容性）"""
        self.create_tabbed_interface()

    def create_status_section(self) -> None:
        """创建状态显示区域"""
        status_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        status_frame.pack(fill="x", padx=20, pady=(0, 15))

        # 状态标题
        status_title = ctk.CTkLabel(
            status_frame, text="🎯 系统状态", font=ctk.CTkFont(size=16, weight="bold")
        )
        status_title.pack(anchor="w", padx=15, pady=(15, 5))

        # 状态指示器容器
        status_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_container.pack(fill="x", padx=15, pady=(0, 15))

        # 主要状态指示器
        self.status_label = ctk.CTkLabel(
            status_container,
            text="🔴 音乐引擎未启动",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e74c3c",
        )
        self.status_label.pack(anchor="w", pady=(0, 5))

        # 暂停状态指示器
        self.pause_status_label = ctk.CTkLabel(
            status_container, text="", font=ctk.CTkFont(size=12), text_color="#f39c12"
        )
        self.pause_status_label.pack(anchor="w")

    def create_control_section(self) -> None:
        """创建控制按钮区域"""
        control_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        control_frame.pack(fill="x", padx=20, pady=(0, 15))

        control_title = ctk.CTkLabel(
            control_frame, text="🎮 控制面板", font=ctk.CTkFont(size=16, weight="bold")
        )
        control_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 按钮容器
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 启动按钮
        self.start_button = ctk.CTkButton(
            button_frame,
            text="🎵 启动音乐引擎",
            command=self.start_music_engine,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#27ae60",
            hover_color="#229954",
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 停止按钮
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹️ 停止音乐引擎",
            command=self.stop_music_engine,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            state="disabled",
            fg_color="#e74c3c",
            hover_color="#c0392b",
        )
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def create_stems_control_section(self) -> None:
        """创建分轨控制区域"""
        stems_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        stems_frame.pack(fill="x", padx=20, pady=(0, 15))

        stems_title = ctk.CTkLabel(
            stems_frame, text="🎛️ 分轨音量控制", font=ctk.CTkFont(size=16, weight="bold")
        )
        stems_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 分轨列表
        stems = [
            ("drums", "🥁 鼓"),
            ("bass", "🎸 低音"),
            ("vocals", "🎤 人声"),
            ("other", "🎵 其他"),
        ]

        for stem_key, stem_name in stems:
            # 每个分轨的容器
            stem_container = ctk.CTkFrame(stems_frame, fg_color="transparent")
            stem_container.pack(fill="x", padx=15, pady=(0, 10))

            # 分轨名称标签
            stem_label = ctk.CTkLabel(
                stem_container,
                text=stem_name,
                font=ctk.CTkFont(size=14, weight="bold"),
                width=80,
            )
            stem_label.pack(side="left", padx=(0, 10))

            # 音量滑块
            volume_slider = ctk.CTkSlider(
                stem_container,
                from_=0.0,
                to=2.0,
                number_of_steps=200,
                command=lambda value, stem=stem_key: self.on_stem_volume_change(
                    stem, value
                ),
                width=150,
            )
            volume_slider.set(0.8)  # 默认音量
            volume_slider.pack(side="left", padx=(0, 10))
            self.stem_volume_sliders[stem_key] = volume_slider

            # 静音开关
            mute_switch = ctk.CTkSwitch(
                stem_container,
                text="静音",
                command=lambda stem=stem_key: self.on_stem_mute_toggle(stem),
                width=60,
            )
            mute_switch.pack(side="left", padx=(0, 10))
            self.stem_mute_switches[stem_key] = mute_switch

            # 独奏开关
            solo_switch = ctk.CTkSwitch(
                stem_container,
                text="独奏",
                command=lambda stem=stem_key: self.on_stem_solo_toggle(stem),
                width=60,
            )
            solo_switch.pack(side="left")
            self.stem_solo_switches[stem_key] = solo_switch

    def create_auto_pause_section(self) -> None:
        """创建自动暂停设置区域"""
        pause_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        pause_frame.pack(fill="x", padx=20, pady=(0, 15))

        pause_title = ctk.CTkLabel(
            pause_frame, text="⏸️ 自动暂停设置", font=ctk.CTkFont(size=16, weight="bold")
        )
        pause_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 自动暂停超时设置
        timeout_container = ctk.CTkFrame(pause_frame, fg_color="transparent")
        timeout_container.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            timeout_container,
            text="⏱️ 自动暂停超时 (秒):",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        self.auto_pause_timeout_slider = ctk.CTkSlider(
            timeout_container,
            from_=1.0,
            to=10.0,
            number_of_steps=90,
            command=self.on_auto_pause_timeout_change,
        )
        self.auto_pause_timeout_slider.set(3.0)  # 默认3秒
        self.auto_pause_timeout_slider.pack(
            side="right", fill="x", expand=True, padx=(10, 0)
        )

        # 超时数值显示
        self.timeout_value_label = ctk.CTkLabel(
            timeout_container, text="3.0s", font=ctk.CTkFont(size=12), width=40
        )
        self.timeout_value_label.pack(side="right", padx=(10, 0))

    def create_fade_section(self) -> None:
        """创建淡入淡出设置区域"""
        fade_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        fade_frame.pack(fill="x", padx=20, pady=(0, 15))

        fade_title = ctk.CTkLabel(
            fade_frame, text="🌊 淡入淡出设置", font=ctk.CTkFont(size=16, weight="bold")
        )
        fade_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 启用淡入淡出开关
        fade_enable_container = ctk.CTkFrame(fade_frame, fg_color="transparent")
        fade_enable_container.pack(fill="x", padx=15, pady=(0, 10))

        self.fade_enable_switch = ctk.CTkSwitch(
            fade_enable_container,
            text="启用淡入淡出效果",
            command=self.on_fade_enable_toggle,
        )
        self.fade_enable_switch.pack(side="left")

        # 淡入淡出时长设置
        fade_duration_container = ctk.CTkFrame(fade_frame, fg_color="transparent")
        fade_duration_container.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            fade_duration_container,
            text="⏲️ 淡入淡出时长 (秒):",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        self.fade_duration_slider = ctk.CTkSlider(
            fade_duration_container,
            from_=0.1,
            to=2.0,
            number_of_steps=190,
            command=self.on_fade_duration_change,
        )
        self.fade_duration_slider.set(0.5)  # 默认0.5秒
        self.fade_duration_slider.pack(
            side="right", fill="x", expand=True, padx=(10, 0)
        )

        # 时长数值显示
        self.fade_duration_value_label = ctk.CTkLabel(
            fade_duration_container, text="0.5s", font=ctk.CTkFont(size=12), width=40
        )
        self.fade_duration_value_label.pack(side="right", padx=(10, 0))

    def create_logging_section(self) -> None:
        """创建日志设置区域"""
        log_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        log_frame.pack(fill="x", padx=20, pady=(0, 15))

        log_title = ctk.CTkLabel(
            log_frame, text="📝 日志设置", font=ctk.CTkFont(size=16, weight="bold")
        )
        log_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 日志级别选择
        log_level_container = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_level_container.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            log_level_container,
            text="📊 日志级别:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        self.log_level_var = ctk.StringVar(value="INFO")
        self.log_level_menu = ctk.CTkOptionMenu(
            log_level_container,
            variable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            command=self.on_log_level_change,
        )
        self.log_level_menu.pack(side="right")

        # 详细日志开关
        verbose_container = ctk.CTkFrame(log_frame, fg_color="transparent")
        verbose_container.pack(fill="x", padx=15, pady=(0, 15))

        self.verbose_logging_switch = ctk.CTkSwitch(
            verbose_container,
            text="启用详细日志输出",
            command=self.on_verbose_logging_toggle,
        )
        self.verbose_logging_switch.pack(side="left")

    def create_monitoring_section(self) -> None:
        """创建参数监控区域"""
        monitor_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        monitor_frame.pack(fill="x", padx=20, pady=(0, 15))

        monitor_title = ctk.CTkLabel(
            monitor_frame,
            text="📊 实时音乐参数",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        monitor_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 参数网格
        params_grid = ctk.CTkFrame(monitor_frame, fg_color="transparent")
        params_grid.pack(fill="x", padx=15, pady=(0, 15))

        # 参数标签字典
        self.param_labels = {}

        # 第一行：BPM 和音量
        row1 = ctk.CTkFrame(params_grid, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        # BPM
        bpm_frame = ctk.CTkFrame(row1, corner_radius=8)
        bpm_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            bpm_frame, text="🥁 BPM", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)
        self.param_labels["bpm"] = ctk.CTkLabel(
            bpm_frame,
            text="--",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3498db",
        )
        self.param_labels["bpm"].pack(pady=(0, 5))

        # 音量/存在感
        volume_frame = ctk.CTkFrame(row1, corner_radius=8)
        volume_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            volume_frame, text="🔊 存在感", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)
        self.param_labels["volume"] = ctk.CTkLabel(
            volume_frame,
            text="--",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e67e22",
        )
        self.param_labels["volume"].pack(pady=(0, 5))

        # 第二行：音调和声像
        row2 = ctk.CTkFrame(params_grid, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        # 基础音调
        pitch_frame = ctk.CTkFrame(row2, corner_radius=8)
        pitch_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            pitch_frame, text="🎼 音调", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)
        self.param_labels["pitch"] = ctk.CTkLabel(
            pitch_frame,
            text="--",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#9b59b6",
        )
        self.param_labels["pitch"].pack(pady=(0, 5))

        # 空间声像
        pan_frame = ctk.CTkFrame(row2, corner_radius=8)
        pan_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            pan_frame, text="🎧 声像", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)
        self.param_labels["pan"] = ctk.CTkLabel(
            pan_frame,
            text="--",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1abc9c",
        )
        self.param_labels["pan"].pack(pady=(0, 5))

    def create_config_section(self) -> None:
        """创建配置调节区域"""
        config_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=12)
        config_frame.pack(fill="x", padx=20, pady=(0, 20))

        config_title = ctk.CTkLabel(
            config_frame, text="⚙️ 快速配置", font=ctk.CTkFont(size=16, weight="bold")
        )
        config_title.pack(anchor="w", padx=15, pady=(15, 10))

        # 主音量滑块
        volume_container = ctk.CTkFrame(config_frame, fg_color="transparent")
        volume_container.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            volume_container, text="🎚️ 主音量:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        self.master_volume_slider = ctk.CTkSlider(
            volume_container,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            command=self.on_volume_change,
        )
        self.master_volume_slider.set(0.8)  # 默认音量
        self.master_volume_slider.pack(
            side="right", fill="x", expand=True, padx=(10, 0)
        )

        # 更新频率滑块
        rate_container = ctk.CTkFrame(config_frame, fg_color="transparent")
        rate_container.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            rate_container,
            text="🔄 更新频率:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        self.update_rate_slider = ctk.CTkSlider(
            rate_container,
            from_=10,
            to=120,
            number_of_steps=110,
            command=self.on_rate_change,
        )
        self.update_rate_slider.set(60)  # 默认60Hz
        self.update_rate_slider.pack(side="right", fill="x", expand=True, padx=(10, 0))

    # ------------------------------------------------------------------
    # 控制逻辑
    # ------------------------------------------------------------------

    def start_music_engine(self) -> None:
        """启动音乐引擎"""
        try:
            if self.is_running:
                return

            # 创建配置
            config = AudioConfig()
            config.master_volume = self.master_volume_slider.get()
            config.update_rate = int(self.update_rate_slider.get())

            # 设置分轨音量配置
            for stem_key, slider in self.stem_volume_sliders.items():
                if not hasattr(config, "stem_volumes"):
                    config.stem_volumes = {}
                config.stem_volumes[stem_key] = slider.get()

            # 设置自动暂停配置
            config.auto_pause_timeout = self.auto_pause_timeout_slider.get()

            # 设置淡入淡出配置
            config.enable_fade_transition = self.fade_enable_switch.get()
            config.fade_duration = self.fade_duration_slider.get()

            # 设置日志配置
            config.log_level = self.log_level_var.get()
            config.enable_verbose_logging = self.verbose_logging_switch.get()

            # 强制使用分轨后端 (pygame)
            config.audio_engine = "stems"

            # 创建控制器
            self.controller = MBUXSoundDriveController(config=config)
            self.controller.start()

            # 启动后输出实际后端信息
            try:
                status = self.controller.engine.get_status()
                print(
                    f"[音乐控制面板] 音频后端: {status.get('backend')} | 运行: {status.get('is_running')} | stems_dir: {status.get('stems_dir', '<未设置>')}"
                )
            except Exception as _:
                pass

            # 更新状态
            self.is_running = True
            self.status_label.configure(text="🟢 音乐引擎运行中", text_color="#27ae60")

            # 更新按钮状态
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="disabled")  # 在初始化完成后再启用

            # 启动UI更新线程
            self.should_update = True
            self.update_thread = threading.Thread(
                target=self.update_ui_loop, daemon=True
            )
            self.update_thread.start()

            print("[音乐控制面板] MBUX 音乐引擎已启动")

            # 延迟启用停止按钮
            self.after(1000, lambda: self.stop_button.configure(state="normal"))

        except Exception as e:
            self.show_error(f"启动音乐引擎失败: {e}")

    def stop_music_engine(self) -> None:
        """停止音乐引擎"""
        try:
            if not self.is_running:
                return

            # 停止UI更新
            self.should_update = False

            # 停止控制器
            if self.controller:
                self.controller.stop()
                self.controller = None

            # 更新状态
            self.is_running = False
            self.status_label.configure(text="🔴 音乐引擎已停止", text_color="#e74c3c")
            self.pause_status_label.configure(text="")

            # 更新按钮状态
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

            # 清空参数显示
            for label in self.param_labels.values():
                label.configure(text="--")

            print("[音乐控制面板] MBUX 音乐引擎已停止")

        except Exception as e:
            self.show_error(f"停止音乐引擎失败: {e}")

    # ------------------------------------------------------------------
    # 回调函数
    # ------------------------------------------------------------------

    def on_volume_change(self, value: float) -> None:
        """主音量变化回调"""
        if self.controller and self.is_running:
            self.controller.engine.set_master_volume(value)

    def on_stem_volume_change(self, stem: str, value: float) -> None:
        """分轨音量变化回调"""
        if self.controller and self.is_running:
            self.controller.engine.set_stem_volume(stem, value)

    def on_stem_mute_toggle(self, stem: str) -> None:
        """分轨静音切换回调"""
        if self.controller and self.is_running:
            muted = self.stem_mute_switches[stem].get()
            self.controller.engine.set_stem_mute(stem, muted)

    def on_stem_solo_toggle(self, stem: str) -> None:
        """分轨独奏切换回调"""
        if self.controller and self.is_running:
            solo = self.stem_solo_switches[stem].get()
            self.controller.engine.set_stem_solo(stem, solo)

    def on_auto_pause_timeout_change(self, value: float) -> None:
        """自动暂停超时变化回调"""
        self.timeout_value_label.configure(text=f"{value:.1f}s")
        if self.controller and self.is_running:
            # 更新控制器配置
            self.controller.config.auto_pause_timeout = value

    def on_fade_enable_toggle(self) -> None:
        """淡入淡出启用切换回调"""
        if self.controller and self.is_running:
            enabled = self.fade_enable_switch.get()
            self.controller.config.enable_fade_transition = enabled

    def on_fade_duration_change(self, value: float) -> None:
        """淡入淡出时长变化回调"""
        self.fade_duration_value_label.configure(text=f"{value:.1f}s")
        if self.controller and self.is_running:
            self.controller.config.fade_duration = value

    def on_log_level_change(self, value: str) -> None:
        """日志级别变化回调"""
        if self.controller and self.is_running:
            self.controller.config.log_level = value

    def on_verbose_logging_toggle(self) -> None:
        """详细日志切换回调"""
        if self.controller and self.is_running:
            verbose = self.verbose_logging_switch.get()
            self.controller.config.enable_verbose_logging = verbose

    def on_rate_change(self, value: float) -> None:
        """更新频率变化回调"""
        # 更新频率需要重新启动控制器
        pass  # 暂时不处理实时更改

    def update_ui_loop(self) -> None:
        """UI更新循环"""
        import time

        while self.should_update and self.is_running:
            try:
                if self.controller:
                    # 获取控制器状态
                    controller_status = self.controller.get_status()

                    # 更新暂停状态显示
                    if controller_status.get("paused_due_to_no_data", False):
                        pause_text = "⏸️ 自动暂停 - 无数据输入"
                        pause_color = "#f39c12"
                    elif self.controller.engine.is_paused():
                        pause_text = "⏸️ 已暂停"
                        pause_color = "#e67e22"
                    else:
                        pause_text = ""
                        pause_color = "#27ae60"

                    # 在主线程中更新UI
                    self.after(
                        0, self.update_pause_status_display, pause_text, pause_color
                    )

                    # 更新音乐参数
                    if self.controller.engine.current_params:
                        params = self.controller.engine.current_params
                        self.after(0, self.update_parameters_display, params)

                time.sleep(0.1)  # 10Hz更新频率

            except Exception as e:
                print(f"[音乐控制面板] UI更新错误: {e}")
                time.sleep(0.2)

    def update_pause_status_display(self, text: str, color: str) -> None:
        """更新暂停状态显示（主线程中执行）"""
        try:
            self.pause_status_label.configure(text=text, text_color=color)
        except Exception as e:
            print(f"[音乐控制面板] 暂停状态显示更新错误: {e}")

    def update_parameters_display(self, params) -> None:
        """更新参数显示（主线程中执行）"""
        try:
            self.param_labels["bpm"].configure(text=f"{params.bpm:.1f}")
            self.param_labels["volume"].configure(text=f"{params.volume:.2f}")
            self.param_labels["pitch"].configure(text=f"{params.base_pitch}")

            # 声像显示
            pan_text = "中央"
            if params.pan > 0.1:
                pan_text = f"右 {params.pan:.2f}"
            elif params.pan < -0.1:
                pan_text = f"左 {abs(params.pan):.2f}"
            self.param_labels["pan"].configure(text=pan_text)

        except Exception as e:
            print(f"[音乐控制面板] 参数显示更新错误: {e}")

    def show_error(self, message: str) -> None:
        """显示错误信息"""
        print(f"[音乐控制面板] 错误: {message}")
        # 这里可以添加错误对话框显示逻辑

    def cleanup(self) -> None:
        """清理资源"""
        self.should_update = False
        if self.is_running:
            self.stop_music_engine()
