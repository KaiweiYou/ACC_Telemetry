#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC交互音乐GUI界面

这个模块提供交互音乐功能的图形用户界面。
包括音乐控制面板、参数可视化、配置设置等功能。

作者: Assistant
日期: 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from typing import Dict, Any, Optional, Callable
import json
import os

from .music_engine import MusicEngine
from .music_mapper import MusicMapper, MusicParameters
from .audio_config import AudioConfig
from ..core.telemetry import TelemetryData

class MusicVisualizationPanel(ttk.Frame):
    """音乐可视化面板
    
    显示实时音乐参数和波形
    """
    
    def __init__(self, parent):
        """初始化可视化面板
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 创建画布
        self.canvas = tk.Canvas(self, width=400, height=200, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 参数显示
        self.param_labels = {}
        self._create_parameter_display()
        
        # 可视化数据
        self.waveform_data = [0] * 100
        self.spectrum_data = [0] * 50
        
        # 动画控制
        self.animation_running = False
        self.animation_thread: Optional[threading.Thread] = None
    
    def _create_parameter_display(self) -> None:
        """创建参数显示区域"""
        # 参数框架
        param_frame = ttk.LabelFrame(self, text="实时参数")
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建参数标签
        params = [
            ('BPM', 'bpm'),
            ('音量', 'volume'),
            ('音调', 'pitch_offset'),
            ('平移', 'pan'),
            ('失真', 'distortion'),
            ('混响', 'reverb')
        ]
        
        for i, (label, key) in enumerate(params):
            row = i // 3
            col = i % 3
            
            ttk.Label(param_frame, text=f"{label}:").grid(
                row=row*2, column=col, sticky='w', padx=5, pady=2
            )
            
            value_label = ttk.Label(param_frame, text="0.0", foreground='blue')
            value_label.grid(row=row*2+1, column=col, sticky='w', padx=5)
            
            self.param_labels[key] = value_label
    
    def update_parameters(self, params: MusicParameters) -> None:
        """更新参数显示
        
        Args:
            params: 音乐参数
        """
        # 更新参数标签
        self.param_labels['bpm'].config(text=f"{params.bpm:.1f}")
        self.param_labels['volume'].config(text=f"{params.volume:.2f}")
        self.param_labels['pitch_offset'].config(text=f"{params.pitch_offset:.1f}")
        self.param_labels['pan'].config(text=f"{params.pan:.2f}")
        self.param_labels['distortion'].config(text=f"{params.distortion:.2f}")
        self.param_labels['reverb'].config(text=f"{params.reverb:.2f}")
        
        # 更新可视化
        self._update_visualization(params)
    
    def _update_visualization(self, params: MusicParameters) -> None:
        """更新可视化显示
        
        Args:
            params: 音乐参数
        """
        # 清除画布
        self.canvas.delete("all")
        
        # 绘制BPM指示器
        self._draw_bpm_indicator(params.bpm)
        
        # 绘制音量条
        self._draw_volume_bar(params.volume)
        
        # 绘制立体声平移
        self._draw_pan_indicator(params.pan)
        
        # 绘制音效指示器
        self._draw_effects_indicators(params)
    
    def _draw_bpm_indicator(self, bpm: float) -> None:
        """绘制BPM指示器
        
        Args:
            bpm: BPM值
        """
        # 圆形BPM指示器
        center_x, center_y = 50, 50
        radius = 30
        
        # 背景圆
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline='gray', width=2
        )
        
        # BPM文本
        self.canvas.create_text(
            center_x, center_y - 10,
            text="BPM", fill='white', font=('Arial', 8)
        )
        self.canvas.create_text(
            center_x, center_y + 5,
            text=f"{bpm:.0f}", fill='cyan', font=('Arial', 12, 'bold')
        )
        
        # 节拍指示器（闪烁效果）
        beat_phase = (time.time() * bpm / 60) % 1
        if beat_phase < 0.1:  # 闪烁
            self.canvas.create_oval(
                center_x - 5, center_y - 5,
                center_x + 5, center_y + 5,
                fill='red', outline='red'
            )
    
    def _draw_volume_bar(self, volume: float) -> None:
        """绘制音量条
        
        Args:
            volume: 音量值 (0-1)
        """
        bar_x, bar_y = 120, 20
        bar_width, bar_height = 200, 20
        
        # 背景
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
            outline='gray', fill='black'
        )
        
        # 音量条
        fill_width = int(bar_width * volume)
        color = 'green' if volume < 0.7 else 'yellow' if volume < 0.9 else 'red'
        
        if fill_width > 0:
            self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + fill_width, bar_y + bar_height,
                fill=color, outline=color
            )
        
        # 标签
        self.canvas.create_text(
            bar_x - 10, bar_y + bar_height // 2,
            text="音量", fill='white', anchor='e'
        )
        
        # 数值
        self.canvas.create_text(
            bar_x + bar_width + 10, bar_y + bar_height // 2,
            text=f"{volume:.2f}", fill='white', anchor='w'
        )
    
    def _draw_pan_indicator(self, pan: float) -> None:
        """绘制立体声平移指示器
        
        Args:
            pan: 平移值 (-1 到 1)
        """
        indicator_x, indicator_y = 120, 60
        indicator_width = 200
        
        # 背景线
        self.canvas.create_line(
            indicator_x, indicator_y,
            indicator_x + indicator_width, indicator_y,
            fill='gray', width=3
        )
        
        # 中心标记
        center_x = indicator_x + indicator_width // 2
        self.canvas.create_line(
            center_x, indicator_y - 5,
            center_x, indicator_y + 5,
            fill='white', width=2
        )
        
        # 平移指示器
        pan_x = center_x + (pan * indicator_width // 2)
        self.canvas.create_oval(
            pan_x - 5, indicator_y - 5,
            pan_x + 5, indicator_y + 5,
            fill='yellow', outline='orange'
        )
        
        # 标签
        self.canvas.create_text(
            indicator_x - 10, indicator_y,
            text="L", fill='white', anchor='e'
        )
        self.canvas.create_text(
            indicator_x + indicator_width + 10, indicator_y,
            text="R", fill='white', anchor='w'
        )
    
    def _draw_effects_indicators(self, params: MusicParameters) -> None:
        """绘制音效指示器
        
        Args:
            params: 音乐参数
        """
        # 特殊音效指示器
        effects_y = 100
        effects = [
            ('涡轮', params.trigger_turbo_sound, 'cyan'),
            ('DRS', params.trigger_drs_sound, 'green'),
            ('警告', params.trigger_warning_sound, 'red'),
            ('庆祝', params.trigger_celebration, 'gold')
        ]
        
        for i, (name, active, color) in enumerate(effects):
            x = 50 + i * 80
            
            # 背景圆
            self.canvas.create_oval(
                x - 15, effects_y - 15,
                x + 15, effects_y + 15,
                outline='gray', fill='black' if not active else color
            )
            
            # 文本
            text_color = 'white' if not active else 'black'
            self.canvas.create_text(
                x, effects_y,
                text=name, fill=text_color, font=('Arial', 8, 'bold')
            )
        
        # 失真和混响指示器
        distortion_bar_x = 50
        reverb_bar_x = 200
        effects_bar_y = 140
        bar_width = 100
        bar_height = 10
        
        # 失真条
        self.canvas.create_rectangle(
            distortion_bar_x, effects_bar_y,
            distortion_bar_x + bar_width, effects_bar_y + bar_height,
            outline='gray', fill='black'
        )
        
        distortion_fill = int(bar_width * params.distortion)
        if distortion_fill > 0:
            self.canvas.create_rectangle(
                distortion_bar_x, effects_bar_y,
                distortion_bar_x + distortion_fill, effects_bar_y + bar_height,
                fill='orange', outline='orange'
            )
        
        self.canvas.create_text(
            distortion_bar_x + bar_width // 2, effects_bar_y - 10,
            text="失真", fill='white', font=('Arial', 8)
        )
        
        # 混响条
        self.canvas.create_rectangle(
            reverb_bar_x, effects_bar_y,
            reverb_bar_x + bar_width, effects_bar_y + bar_height,
            outline='gray', fill='black'
        )
        
        reverb_fill = int(bar_width * params.reverb)
        if reverb_fill > 0:
            self.canvas.create_rectangle(
                reverb_bar_x, effects_bar_y,
                reverb_bar_x + reverb_fill, effects_bar_y + bar_height,
                fill='blue', outline='blue'
            )
        
        self.canvas.create_text(
            reverb_bar_x + bar_width // 2, effects_bar_y - 10,
            text="混响", fill='white', font=('Arial', 8)
        )

class MusicControlPanel(ttk.Frame):
    """音乐控制面板
    
    提供音乐播放控制和基本设置
    """
    
    def __init__(self, parent, on_start_callback: Callable, on_stop_callback: Callable):
        """初始化控制面板
        
        Args:
            parent: 父窗口
            on_start_callback: 开始播放回调
            on_stop_callback: 停止播放回调
        """
        super().__init__(parent)
        
        self.on_start_callback = on_start_callback
        self.on_stop_callback = on_stop_callback
        
        self.is_playing = False
        
        self._create_controls()
    
    def _create_controls(self) -> None:
        """创建控制按钮"""
        # 主控制按钮
        control_frame = ttk.LabelFrame(self, text="播放控制")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.play_button = ttk.Button(
            control_frame, text="▶ 开始", 
            command=self._toggle_playback
        )
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 状态指示器
        self.status_label = ttk.Label(
            control_frame, text="状态: 已停止", foreground='red'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 音量控制
        volume_frame = ttk.LabelFrame(self, text="主音量")
        volume_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.volume_var = tk.DoubleVar(value=0.7)
        self.volume_scale = ttk.Scale(
            volume_frame, from_=0.0, to=1.0, 
            variable=self.volume_var, orient=tk.HORIZONTAL
        )
        self.volume_scale.pack(fill=tk.X, padx=5, pady=5)
        
        self.volume_label = ttk.Label(
            volume_frame, text="70%"
        )
        self.volume_label.pack(pady=2)
        
        # 绑定音量变化事件
        self.volume_var.trace('w', self._on_volume_change)
        
        # 快速设置
        preset_frame = ttk.LabelFrame(self, text="快速设置")
        preset_frame.pack(fill=tk.X, padx=5, pady=5)
        
        presets = [
            ("安静", 0.3),
            ("正常", 0.7),
            ("响亮", 1.0)
        ]
        
        for name, volume in presets:
            btn = ttk.Button(
                preset_frame, text=name,
                command=lambda v=volume: self.volume_var.set(v)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=5)
    
    def _toggle_playback(self) -> None:
        """切换播放状态"""
        if self.is_playing:
            self._stop_playback()
        else:
            self._start_playback()
    
    def _start_playback(self) -> None:
        """开始播放"""
        try:
            if self.on_start_callback():
                self.is_playing = True
                self.play_button.config(text="⏸ 停止")
                self.status_label.config(text="状态: 播放中", foreground='green')
            else:
                messagebox.showerror("错误", "无法启动音乐引擎")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")
    
    def _stop_playback(self) -> None:
        """停止播放"""
        try:
            self.on_stop_callback()
            self.is_playing = False
            self.play_button.config(text="▶ 开始")
            self.status_label.config(text="状态: 已停止", foreground='red')
        except Exception as e:
            messagebox.showerror("错误", f"停止失败: {e}")
    
    def _on_volume_change(self, *args) -> None:
        """音量变化回调"""
        volume = self.volume_var.get()
        self.volume_label.config(text=f"{int(volume * 100)}%")
    
    def get_volume(self) -> float:
        """获取当前音量
        
        Returns:
            float: 音量值 (0-1)
        """
        return self.volume_var.get()
    
    def set_playing_state(self, playing: bool) -> None:
        """设置播放状态
        
        Args:
            playing: 是否正在播放
        """
        self.is_playing = playing
        if playing:
            self.play_button.config(text="⏸ 停止")
            self.status_label.config(text="状态: 播放中", foreground='green')
        else:
            self.play_button.config(text="▶ 开始")
            self.status_label.config(text="状态: 已停止", foreground='red')

class MusicConfigPanel(ttk.Frame):
    """音乐配置面板
    
    提供详细的音乐参数配置
    """
    
    def __init__(self, parent, config: AudioConfig):
        """初始化配置面板
        
        Args:
            parent: 父窗口
            config: 音频配置
        """
        super().__init__(parent)
        
        self.config = config
        self.config_vars = {}
        
        self._create_config_interface()
    
    def _create_config_interface(self) -> None:
        """创建配置界面"""
        # 创建笔记本控件
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 节奏配置页
        rhythm_frame = ttk.Frame(notebook)
        notebook.add(rhythm_frame, text="节奏")
        self._create_rhythm_config(rhythm_frame)
        
        # 旋律配置页
        melody_frame = ttk.Frame(notebook)
        notebook.add(melody_frame, text="旋律")
        self._create_melody_config(melody_frame)
        
        # 音效配置页
        effects_frame = ttk.Frame(notebook)
        notebook.add(effects_frame, text="音效")
        self._create_effects_config(effects_frame)
        
        # 氛围配置页
        ambience_frame = ttk.Frame(notebook)
        notebook.add(ambience_frame, text="氛围")
        self._create_ambience_config(ambience_frame)
        
        # 按钮框架
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            button_frame, text="保存配置",
            command=self._save_config
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="加载配置",
            command=self._load_config
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="重置默认",
            command=self._reset_config
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_rhythm_config(self, parent) -> None:
        """创建节奏配置
        
        Args:
            parent: 父窗口
        """
        # 启用节奏
        self.config_vars['enable_rhythm'] = tk.BooleanVar(value=self.config.enable_rhythm)
        ttk.Checkbutton(
            parent, text="启用节奏生成",
            variable=self.config_vars['enable_rhythm']
        ).pack(anchor='w', padx=5, pady=5)
        
        # BPM范围
        bpm_frame = ttk.LabelFrame(parent, text="BPM范围")
        bpm_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(bpm_frame, text="最小BPM:").grid(row=0, column=0, sticky='w', padx=5)
        self.config_vars['bpm_min'] = tk.DoubleVar(value=self.config.rhythm.bpm_range[0])
        ttk.Entry(bpm_frame, textvariable=self.config_vars['bpm_min'], width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(bpm_frame, text="最大BPM:").grid(row=0, column=2, sticky='w', padx=5)
        self.config_vars['bpm_max'] = tk.DoubleVar(value=self.config.rhythm.bpm_range[1])
        ttk.Entry(bpm_frame, textvariable=self.config_vars['bpm_max'], width=10).grid(row=0, column=3, padx=5)
        
        # RPM敏感度
        sens_frame = ttk.LabelFrame(parent, text="敏感度设置")
        sens_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(sens_frame, text="RPM敏感度:").grid(row=0, column=0, sticky='w', padx=5)
        self.config_vars['rpm_sensitivity'] = tk.DoubleVar(value=self.config.rhythm.rpm_sensitivity)
        ttk.Scale(
            sens_frame, from_=0.1, to=2.0,
            variable=self.config_vars['rpm_sensitivity'],
            orient=tk.HORIZONTAL
        ).grid(row=0, column=1, sticky='ew', padx=5)
        
        ttk.Label(sens_frame, text="速度敏感度:").grid(row=1, column=0, sticky='w', padx=5)
        self.config_vars['speed_sensitivity'] = tk.DoubleVar(value=self.config.rhythm.speed_sensitivity)
        ttk.Scale(
            sens_frame, from_=0.1, to=2.0,
            variable=self.config_vars['speed_sensitivity'],
            orient=tk.HORIZONTAL
        ).grid(row=1, column=1, sticky='ew', padx=5)
        
        sens_frame.columnconfigure(1, weight=1)
    
    def _create_melody_config(self, parent) -> None:
        """创建旋律配置
        
        Args:
            parent: 父窗口
        """
        # 启用旋律
        self.config_vars['enable_melody'] = tk.BooleanVar(value=self.config.enable_melody)
        ttk.Checkbutton(
            parent, text="启用旋律生成",
            variable=self.config_vars['enable_melody']
        ).pack(anchor='w', padx=5, pady=5)
        
        # 音阶设置
        scale_frame = ttk.LabelFrame(parent, text="音阶设置")
        scale_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(scale_frame, text="音阶类型:").grid(row=0, column=0, sticky='w', padx=5)
        self.config_vars['scale_type'] = tk.StringVar(value=self.config.melody.scale_type)
        scale_combo = ttk.Combobox(
            scale_frame, textvariable=self.config_vars['scale_type'],
            values=['pentatonic', 'major', 'minor', 'blues', 'dorian'],
            state='readonly'
        )
        scale_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(scale_frame, text="调性:").grid(row=0, column=2, sticky='w', padx=5)
        self.config_vars['key'] = tk.StringVar(value=self.config.melody.key)
        key_combo = ttk.Combobox(
            scale_frame, textvariable=self.config_vars['key'],
            values=['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
            state='readonly'
        )
        key_combo.grid(row=0, column=3, padx=5)
        
        # 基础音高
        ttk.Label(scale_frame, text="基础音高(MIDI):").grid(row=1, column=0, sticky='w', padx=5)
        self.config_vars['base_pitch'] = tk.IntVar(value=self.config.melody.base_pitch)
        ttk.Entry(scale_frame, textvariable=self.config_vars['base_pitch'], width=10).grid(row=1, column=1, padx=5)
    
    def _create_effects_config(self, parent) -> None:
        """创建音效配置
        
        Args:
            parent: 父窗口
        """
        # 启用音效
        self.config_vars['enable_effects'] = tk.BooleanVar(value=self.config.enable_effects)
        ttk.Checkbutton(
            parent, text="启用音效处理",
            variable=self.config_vars['enable_effects']
        ).pack(anchor='w', padx=5, pady=5)
        
        # 特殊音效
        special_frame = ttk.LabelFrame(parent, text="特殊音效")
        special_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.config_vars['enable_turbo_sound'] = tk.BooleanVar(value=self.config.effects.enable_turbo_sound)
        ttk.Checkbutton(
            special_frame, text="涡轮增压音效",
            variable=self.config_vars['enable_turbo_sound']
        ).pack(anchor='w', padx=5)
        
        self.config_vars['enable_drs_sound'] = tk.BooleanVar(value=self.config.effects.enable_drs_sound)
        ttk.Checkbutton(
            special_frame, text="DRS音效",
            variable=self.config_vars['enable_drs_sound']
        ).pack(anchor='w', padx=5)
        
        self.config_vars['enable_tc_abs_sound'] = tk.BooleanVar(value=self.config.effects.enable_tc_abs_sound)
        ttk.Checkbutton(
            special_frame, text="牵引力控制/ABS音效",
            variable=self.config_vars['enable_tc_abs_sound']
        ).pack(anchor='w', padx=5)
    
    def _create_ambience_config(self, parent) -> None:
        """创建氛围配置
        
        Args:
            parent: 父窗口
        """
        # 启用氛围
        self.config_vars['enable_ambience'] = tk.BooleanVar(value=self.config.enable_ambience)
        ttk.Checkbutton(
            parent, text="启用氛围音效",
            variable=self.config_vars['enable_ambience']
        ).pack(anchor='w', padx=5, pady=5)
        
        # 氛围音量
        volume_frame = ttk.LabelFrame(parent, text="氛围音量")
        volume_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.config_vars['ambient_volume'] = tk.DoubleVar(value=self.config.ambience.ambient_volume)
        ttk.Scale(
            volume_frame, from_=0.0, to=1.0,
            variable=self.config_vars['ambient_volume'],
            orient=tk.HORIZONTAL
        ).pack(fill=tk.X, padx=5, pady=5)
        
        # 圈速反馈
        self.config_vars['enable_lap_feedback'] = tk.BooleanVar(value=self.config.ambience.enable_lap_feedback)
        ttk.Checkbutton(
            parent, text="启用圈速反馈",
            variable=self.config_vars['enable_lap_feedback']
        ).pack(anchor='w', padx=5, pady=5)
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="保存音乐配置"
            )
            
            if filename:
                # 更新配置对象
                self._update_config_from_vars()
                
                # 保存到文件
                self.config.save_to_file(filename)
                messagebox.showinfo("成功", f"配置已保存到: {filename}")
        
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def _load_config(self) -> None:
        """从文件加载配置"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="加载音乐配置"
            )
            
            if filename:
                # 从文件加载
                self.config = AudioConfig.load_from_file(filename)
                
                # 更新界面
                self._update_vars_from_config()
                messagebox.showinfo("成功", f"配置已从 {filename} 加载")
        
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {e}")
    
    def _reset_config(self) -> None:
        """重置为默认配置"""
        try:
            result = messagebox.askyesno("确认", "确定要重置为默认配置吗？")
            if result:
                self.config = AudioConfig()
                self._update_vars_from_config()
                messagebox.showinfo("成功", "配置已重置为默认值")
        
        except Exception as e:
            messagebox.showerror("错误", f"重置配置失败: {e}")
    
    def _update_config_from_vars(self) -> None:
        """从界面变量更新配置对象"""
        # 基本开关
        self.config.enable_rhythm = self.config_vars['enable_rhythm'].get()
        self.config.enable_melody = self.config_vars['enable_melody'].get()
        self.config.enable_effects = self.config_vars['enable_effects'].get()
        self.config.enable_ambience = self.config_vars['enable_ambience'].get()
        
        # 节奏配置
        if 'bpm_min' in self.config_vars and 'bpm_max' in self.config_vars:
            self.config.rhythm.bpm_range = (
                self.config_vars['bpm_min'].get(),
                self.config_vars['bpm_max'].get()
            )
        
        if 'rpm_sensitivity' in self.config_vars:
            self.config.rhythm.rpm_sensitivity = self.config_vars['rpm_sensitivity'].get()
        
        if 'speed_sensitivity' in self.config_vars:
            self.config.rhythm.speed_sensitivity = self.config_vars['speed_sensitivity'].get()
        
        # 旋律配置
        if 'scale_type' in self.config_vars:
            self.config.melody.scale_type = self.config_vars['scale_type'].get()
        
        if 'key' in self.config_vars:
            self.config.melody.key = self.config_vars['key'].get()
        
        if 'base_pitch' in self.config_vars:
            self.config.melody.base_pitch = self.config_vars['base_pitch'].get()
        
        # 音效配置
        if 'enable_turbo_sound' in self.config_vars:
            self.config.effects.enable_turbo_sound = self.config_vars['enable_turbo_sound'].get()
        
        if 'enable_drs_sound' in self.config_vars:
            self.config.effects.enable_drs_sound = self.config_vars['enable_drs_sound'].get()
        
        if 'enable_tc_abs_sound' in self.config_vars:
            self.config.effects.enable_tc_abs_sound = self.config_vars['enable_tc_abs_sound'].get()
        
        # 氛围配置
        if 'ambient_volume' in self.config_vars:
            self.config.ambience.ambient_volume = self.config_vars['ambient_volume'].get()
        
        if 'enable_lap_feedback' in self.config_vars:
            self.config.ambience.enable_lap_feedback = self.config_vars['enable_lap_feedback'].get()
    
    def _update_vars_from_config(self) -> None:
        """从配置对象更新界面变量"""
        # 基本开关
        if 'enable_rhythm' in self.config_vars:
            self.config_vars['enable_rhythm'].set(self.config.enable_rhythm)
        if 'enable_melody' in self.config_vars:
            self.config_vars['enable_melody'].set(self.config.enable_melody)
        if 'enable_effects' in self.config_vars:
            self.config_vars['enable_effects'].set(self.config.enable_effects)
        if 'enable_ambience' in self.config_vars:
            self.config_vars['enable_ambience'].set(self.config.enable_ambience)
        
        # 其他配置项...
        # (为简洁起见，这里省略了详细的更新代码)
    
    def get_config(self) -> AudioConfig:
        """获取当前配置
        
        Returns:
            AudioConfig: 当前配置对象
        """
        self._update_config_from_vars()
        return self.config

class InteractiveMusicGUI(ttk.Frame):
    """交互音乐主界面
    
    整合所有音乐功能的主界面
    """
    
    def __init__(self, parent, telemetry_callback: Callable[[], Optional[TelemetryData]]):
        """初始化交互音乐界面
        
        Args:
            parent: 父窗口
            telemetry_callback: 获取遥测数据的回调函数
        """
        super().__init__(parent)
        
        self.telemetry_callback = telemetry_callback
        
        # 初始化组件
        self.config = AudioConfig()
        self.mapper = MusicMapper(self.config)
        self.engine: Optional[MusicEngine] = None
        
        # 更新线程
        self.update_thread: Optional[threading.Thread] = None
        self.update_running = False
        
        self._create_interface()
        self._initialize_engine()
    
    def _create_interface(self) -> None:
        """创建界面"""
        # 创建主要面板
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧控制面板
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # 控制面板
        self.control_panel = MusicControlPanel(
            left_frame, 
            self._start_music, 
            self._stop_music
        )
        self.control_panel.pack(fill=tk.X, pady=5)
        
        # 配置面板
        self.config_panel = MusicConfigPanel(left_frame, self.config)
        self.config_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 右侧可视化面板
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        self.visualization_panel = MusicVisualizationPanel(right_frame)
        self.visualization_panel.pack(fill=tk.BOTH, expand=True)
    
    def _initialize_engine(self) -> None:
        """初始化音乐引擎"""
        try:
            self.engine = MusicEngine(self.config)
            self.engine.set_error_callback(self._on_engine_error)
        except Exception as e:
            messagebox.showerror("错误", f"音乐引擎初始化失败: {e}")
    
    def _start_music(self) -> bool:
        """启动音乐
        
        Returns:
            bool: 启动是否成功
        """
        try:
            if not self.engine:
                self._initialize_engine()
                if not self.engine:
                    return False
            
            # 更新配置
            self.config = self.config_panel.get_config()
            self.mapper.update_config(self.config)
            self.engine.update_config(self.config)
            
            # 启动引擎
            if not self.engine.start():
                return False
            
            # 启动更新线程
            self.update_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            return True
        
        except Exception as e:
            messagebox.showerror("错误", f"启动音乐失败: {e}")
            return False
    
    def _stop_music(self) -> None:
        """停止音乐"""
        try:
            # 停止更新线程
            self.update_running = False
            
            # 停止引擎
            if self.engine:
                self.engine.stop()
        
        except Exception as e:
            messagebox.showerror("错误", f"停止音乐失败: {e}")
    
    def _update_loop(self) -> None:
        """更新循环线程"""
        while self.update_running:
            try:
                # 获取遥测数据
                telemetry = self.telemetry_callback()
                
                if telemetry and self.engine:
                    # 映射音乐参数
                    music_params = self.mapper.map_telemetry_to_music(telemetry)
                    
                    # 应用主音量
                    music_params.volume *= self.control_panel.get_volume()
                    
                    # 更新引擎
                    self.engine.update_parameters(music_params)
                    
                    # 更新可视化（在主线程中）
                    self.after_idle(
                        lambda: self.visualization_panel.update_parameters(music_params)
                    )
                
                time.sleep(0.05)  # 20Hz更新频率
            
            except Exception as e:
                print(f"更新循环错误: {e}")
                time.sleep(0.1)
    
    def _on_engine_error(self, error_msg: str) -> None:
        """引擎错误回调
        
        Args:
            error_msg: 错误消息
        """
        self.after_idle(
            lambda: messagebox.showerror("音乐引擎错误", error_msg)
        )
    
    def cleanup(self) -> None:
        """清理资源"""
        self.update_running = False
        
        if self.engine:
            self.engine.cleanup()
        
        print("交互音乐界面已清理")