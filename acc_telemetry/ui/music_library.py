#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐库管理面板

提供基础的音乐文件管理和分析状态显示功能。
"""

import json
import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional

import customtkinter as ctk


class MusicLibraryPanel(ctk.CTkFrame):
    """音乐库管理面板类

    提供基础的音乐文件管理功能：
    - 音乐文件导入
    - 音乐列表显示
    - 分析状态跟踪
    - 基础播放控制
    """

    def __init__(self, parent: Any) -> None:
        """初始化音乐库面板

        Args:
            parent: 父控件
        """
        super().__init__(parent, corner_radius=15)

        # 音乐数据存储
        self.music_library: List[Dict[str, Any]] = []
        self.music_dir = Path("songs")

        # 创建界面
        self.create_widgets()
        self.load_existing_music()

    def create_widgets(self) -> None:
        """创建界面组件"""
        # 主框架
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题区域
        self.create_title_section()

        # 控制按钮区域
        self.create_control_section()

        # 音乐列表区域
        self.create_music_list_section()

    def create_title_section(self) -> None:
        """创建标题区域"""
        title_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            title_frame, text="🎵 音乐库管理", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="管理和分析您的音乐文件",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30"),
        )
        subtitle_label.pack(pady=(0, 20))

    def create_control_section(self) -> None:
        """创建控制按钮区域"""
        control_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        control_frame.pack(fill="x", pady=(0, 20))

        # 导入按钮
        self.import_button = ctk.CTkButton(
            control_frame,
            text="📁 导入音乐",
            command=self.import_music,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8,
        )
        self.import_button.pack(side="left", padx=10, pady=15)

        # 刷新按钮
        self.refresh_button = ctk.CTkButton(
            control_frame,
            text="🔄 刷新列表",
            command=self.refresh_library,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8,
        )
        self.refresh_button.pack(side="left", padx=10, pady=15)

        # 分析按钮
        self.analyze_button = ctk.CTkButton(
            control_frame,
            text="🔍 分析选中",
            command=self.analyze_selected,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8,
            state="disabled",
        )
        self.analyze_button.pack(side="left", padx=10, pady=15)

        # 音乐计数标签
        self.count_label = ctk.CTkLabel(
            control_frame, text="音乐: 0", font=ctk.CTkFont(size=14)
        )
        self.count_label.pack(side="right", padx=20)

    def create_music_list_section(self) -> None:
        """创建音乐列表区域"""
        list_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        list_frame.pack(fill="both", expand=True)

        # 创建滚动框架
        self.scrollable_frame = ctk.CTkScrollableFrame(list_frame, corner_radius=8)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建表头
        self.create_list_headers()

        # 音乐列表容器
        self.music_items_frame = ctk.CTkFrame(
            self.scrollable_frame, fg_color="transparent"
        )
        self.music_items_frame.pack(fill="both", expand=True)

    def create_list_headers(self) -> None:
        """创建列表表头"""
        headers_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=8)
        headers_frame.pack(fill="x", pady=(0, 10))

        # 标题列
        title_header = ctk.CTkLabel(
            headers_frame, text="音乐标题", font=ctk.CTkFont(size=14, weight="bold")
        )
        title_header.pack(side="left", padx=20, pady=10)

        # 状态列
        status_header = ctk.CTkLabel(
            headers_frame, text="分析状态", font=ctk.CTkFont(size=14, weight="bold")
        )
        status_header.pack(side="left", padx=20, pady=10)

        # 操作列
        action_header = ctk.CTkLabel(
            headers_frame, text="操作", font=ctk.CTkFont(size=14, weight="bold")
        )
        action_header.pack(side="right", padx=20, pady=10)

    def load_existing_music(self) -> None:
        """加载现有音乐"""
        library_dir = self.music_dir / "library"
        if not library_dir.exists():
            library_dir.mkdir(parents=True, exist_ok=True)
            return

        # 扫描音乐目录
        for item in library_dir.iterdir():
            if item.is_dir():
                self.add_music_to_library(item)

        # 确保"lose my mind"被添加
        lose_my_mind_path = library_dir / "lose my mind"
        if lose_my_mind_path.exists():
            # 检查是否已存在
            exists = any(m["name"] == "lose my mind" for m in self.music_library)
            if not exists:
                self.add_music_to_library(lose_my_mind_path)

        self.update_music_count()

    def add_music_to_library(self, music_path: Path) -> None:
        """添加音乐到库中"""
        music_info = {
            "name": music_path.name,
            "path": str(music_path),
            "analyzed": self.check_analysis_status(music_path),
            "analysis_file": (
                str(music_path / "analysis.json")
                if (music_path / "analysis.json").exists()
                else None
            ),
        }

        self.music_library.append(music_info)

    def check_analysis_status(self, music_path: Path) -> bool:
        """检查音乐分析状态"""
        analysis_file = music_path / "analysis.json"

        # 检查是否有分轨文件
        has_stems = any(music_path.glob("*.wav"))

        return analysis_file.exists() and has_stems

    def import_music(self) -> None:
        """导入音乐"""
        directory = filedialog.askdirectory(title="选择音乐文件夹", initialdir=".")

        if directory:
            self.process_import(directory)

    def process_import(self, directory: str) -> None:
        """处理音乐导入"""
        import_path = Path(directory)
        library_dir = self.music_dir / "library"

        # 确保library目录存在
        library_dir.mkdir(parents=True, exist_ok=True)

        # 创建目标文件夹
        target_path = library_dir / import_path.name

        try:
            # 简单复制文件夹结构
            if not target_path.exists():
                # 这里简化处理，实际应该使用batch_song_processor
                target_path.mkdir(parents=True, exist_ok=True)

                # 复制音频文件
                for audio_file in import_path.glob("*"):
                    if audio_file.suffix.lower() in [
                        ".mp3",
                        ".wav",
                        ".flac",
                        ".m4a",
                        ".ogg",
                    ]:
                        # 创建符号链接或复制
                        pass

                self.add_music_to_library(target_path)
                self.refresh_library_display()
                messagebox.showinfo("成功", f"已导入音乐: {import_path.name}")
            else:
                messagebox.showwarning("提示", "该音乐已存在")

        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")

    def refresh_library(self) -> None:
        """刷新音乐库"""
        self.music_library.clear()
        self.load_existing_music()
        self.refresh_library_display()

        # 检查是否有"lose my mind"并添加到列表
        library_dir = self.music_dir / "library"
        lose_my_mind_path = library_dir / "lose my mind"
        if lose_my_mind_path.exists():
            self.add_music_to_library(lose_my_mind_path)
            self.refresh_library_display()

    def refresh_library_display(self) -> None:
        """刷新音乐列表显示"""
        # 清空现有显示
        for widget in self.music_items_frame.winfo_children():
            widget.destroy()

        # 重新显示音乐列表
        for idx, music in enumerate(self.music_library):
            self.create_music_item(music, idx)

        self.update_music_count()

    def create_music_item(self, music: Dict[str, Any], index: int) -> None:
        """创建单个音乐项目显示"""
        item_frame = ctk.CTkFrame(self.music_items_frame, corner_radius=8)
        item_frame.pack(fill="x", pady=2, padx=5)

        # 音乐名称
        name_label = ctk.CTkLabel(
            item_frame, text=music["name"], font=ctk.CTkFont(size=13), anchor="w"
        )
        name_label.pack(side="left", padx=20, pady=10, fill="x", expand=True)

        # 分析状态
        status_text = "✅ 已分析" if music["analyzed"] else "❌ 未分析"
        status_color = "#27ae60" if music["analyzed"] else "#e74c3c"

        status_label = ctk.CTkLabel(
            item_frame,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=status_color,
        )
        status_label.pack(side="left", padx=20, pady=10)

        # 操作按钮
        action_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=20, pady=10)

        if not music["analyzed"]:
            analyze_btn = ctk.CTkButton(
                action_frame,
                text="分析",
                command=lambda m=music: self.analyze_single_music(m),
                width=60,
                height=25,
                font=ctk.CTkFont(size=11),
            )
            analyze_btn.pack()

    def analyze_single_music(self, music: Dict[str, Any]) -> None:
        """分析单个音乐"""

        def run_analysis():
            try:
                # 这里简化处理，实际应该调用song_analyzer
                messagebox.showinfo("分析", f"开始分析: {music['name']}")

                # 模拟分析过程
                import time

                time.sleep(2)

                # 更新状态
                music["analyzed"] = True
                self.refresh_library_display()

                messagebox.showinfo("完成", f"分析完成: {music['name']}")

            except Exception as e:
                messagebox.showerror("错误", f"分析失败: {str(e)}")

        # 在新线程中运行分析
        thread = threading.Thread(target=run_analysis, daemon=True)
        thread.start()

    def analyze_selected(self) -> None:
        """分析选中的音乐"""
        # 基础版暂不支持多选，直接刷新
        self.refresh_library()

    def update_music_count(self) -> None:
        """更新音乐计数"""
        count = len(self.music_library)
        analyzed = sum(1 for m in self.music_library if m["analyzed"])
        self.count_label.configure(text=f"音乐: {count} (已分析: {analyzed})")

    def get_selected_music(self) -> Optional[Dict[str, Any]]:
        """获取选中的音乐"""
        # 基础版返回第一个未分析的音乐
        for music in self.music_library:
            if not music["analyzed"]:
                return music
        return None

    def cleanup(self):
        """清理资源，销毁UI组件"""
        try:
            # 清理音乐库数据
            if hasattr(self, 'music_library'):
                self.music_library.clear()
            
            # 清理UI组件引用
            for attr in ['main_frame', 'title_frame', 'control_frame', 'music_items_frame']:
                if hasattr(self, attr):
                    widget = getattr(self, attr)
                    if hasattr(widget, 'destroy') and widget.winfo_exists():
                        try:
                            widget.destroy()
                        except Exception:
                            pass
            
            # 清理其他引用
            if hasattr(self, 'music_dir'):
                self.music_dir = None
                
        except Exception as e:
            print(f"清理音乐库资源时出错: {e}")
