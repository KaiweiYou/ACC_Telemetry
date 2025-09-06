#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块: batch_song_processor

批量歌曲处理工具：
- 自动扫描指定目录中的音频文件
- 使用 Demucs 进行分轨处理
- 生成 analysis.json 分析文件
- 创建标准化的歌曲目录结构
"""

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def find_audio_files(directory: str, extensions: List[str] = None) -> List[Path]:
    """查找目录中的音频文件

    Args:
        directory: 搜索目录
        extensions: 音频文件扩展名列表

    Returns:
        音频文件路径列表
    """
    if extensions is None:
        extensions = [".mp3", ".wav", ".flac", ".m4a", ".ogg"]

    directory = Path(directory)
    audio_files = []

    for ext in extensions:
        audio_files.extend(directory.rglob(f"*{ext}"))

    return sorted(audio_files)


def create_song_directory(songs_root: str, song_name: str) -> Path:
    """创建标准化的歌曲目录

    Args:
        songs_root: 歌曲根目录
        song_name: 歌曲名称

    Returns:
        歌曲目录路径
    """
    song_dir = Path(songs_root) / song_name
    song_dir.mkdir(parents=True, exist_ok=True)
    return song_dir


def run_demucs(input_file: str, output_dir: str, model: str = "htdemucs") -> bool:
    """运行 Demucs 分轨处理

    Args:
        input_file: 输入音频文件
        output_dir: 输出目录
        model: Demucs 模型名称

    Returns:
        处理是否成功
    """
    try:
        cmd = [
            "demucs",
            "--out",
            output_dir,
            "--name",
            model,
            "--mp3",
            "--mp3-bitrate",
            "320",
            input_file,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("错误: 未找到 demucs 命令，请确保已安装 demucs")
        return False


def run_analysis(song_dir: str) -> bool:
    """运行歌曲分析

    Args:
        song_dir: 歌曲目录

    Returns:
        分析是否成功
    """
    try:
        # 构建分析命令
        analysis_script = Path(__file__).parent / "song_analyzer.py"
        cmd = ["python", str(analysis_script), song_dir]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"分析失败: {e}")
        return False


def process_single_song(
    input_file: str, songs_root: str, skip_existing: bool = True
) -> Dict[str, Any]:
    """处理单首歌曲

    Args:
        input_file: 输入音频文件路径
        songs_root: 歌曲根目录
        skip_existing: 是否跳过已存在的歌曲

    Returns:
        处理结果信息
    """
    input_path = Path(input_file)
    song_name = input_path.stem
    song_dir = create_song_directory(songs_root, song_name)

    result = {
        "song_name": song_name,
        "input_file": str(input_path),
        "song_dir": str(song_dir),
        "success": False,
        "messages": [],
    }

    # 检查是否已存在
    if skip_existing and (song_dir / "analysis.json").exists():
        result["messages"].append("歌曲已存在，跳过处理")
        result["success"] = True
        return result

    print(f"处理歌曲: {song_name}")

    # 步骤1: 运行 Demucs 分轨
    print("  运行 Demucs 分轨...")
    if not run_demucs(str(input_path), str(song_dir)):
        result["messages"].append("Demucs 分轨失败")
        return result

    # 查找 Demucs 输出目录
    demucs_output = None
    for item in song_dir.iterdir():
        if item.is_dir() and item.name.startswith("htdemucs"):
            demucs_output = item / song_name
            break

    if not demucs_output or not demucs_output.exists():
        result["messages"].append("未找到 Demucs 输出目录")
        return result

    # 步骤2: 移动分轨文件到根目录
    print("  整理分轨文件...")
    stems = ["drums.wav", "bass.wav", "vocals.wav", "other.wav"]
    for stem in stems:
        src_file = demucs_output / stem
        dst_file = song_dir / stem
        if src_file.exists():
            shutil.move(str(src_file), str(dst_file))

    # 清理 Demucs 输出目录
    if demucs_output.parent.exists():
        shutil.rmtree(str(demucs_output.parent))

    # 步骤3: 运行分析
    print("  运行音乐分析...")
    if not run_analysis(str(song_dir)):
        result["messages"].append("音乐分析失败")
        return result

    result["success"] = True
    result["messages"].append("处理完成")
    print(f"  完成: {song_name}")

    return result


def batch_process(
    input_directory: str, songs_root: str, **kwargs
) -> List[Dict[str, Any]]:
    """批量处理目录中的音频文件

    Args:
        input_directory: 输入音频文件目录
        songs_root: 歌曲输出根目录
        **kwargs: 其他参数

    Returns:
        处理结果列表
    """
    audio_files = find_audio_files(input_directory)

    if not audio_files:
        print("未找到音频文件")
        return []

    print(f"找到 {len(audio_files)} 个音频文件")

    results = []
    for audio_file in audio_files:
        result = process_single_song(str(audio_file), songs_root, **kwargs)
        results.append(result)

    return results


def generate_summary_report(
    results: List[Dict[str, Any]], output_file: str = None
) -> None:
    """生成处理总结报告

    Args:
        results: 处理结果列表
        output_file: 输出报告文件路径，None 则打印到控制台
    """
    total_songs = len(results)
    successful = sum(1 for r in results if r["success"])
    failed = total_songs - successful

    report = {
        "summary": {
            "total_songs": total_songs,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_songs if total_songs > 0 else 0,
        },
        "details": results,
    }

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"报告已保存到: {output_file}")
    else:
        print("\n=== 处理总结 ===")
        print(f"总歌曲数: {total_songs}")
        print(f"成功: {successful}")
        print(f"失败: {failed}")
        print(f"成功率: {report['summary']['success_rate']:.1%}")

        if failed > 0:
            print("\n失败的歌曲:")
            for result in results:
                if not result["success"]:
                    print(f"  - {result['song_name']}: {', '.join(result['messages'])}")


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description="批量歌曲处理工具")
    parser.add_argument("input_dir", help="输入音频文件目录")
    parser.add_argument("--output-dir", "-o", default="./songs", help="输出歌曲目录")
    parser.add_argument("--skip-existing", action="store_true", help="跳过已存在的歌曲")
    parser.add_argument("--report", "-r", help="生成处理报告文件")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际处理")

    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)

    print("=== 批量歌曲处理开始 ===")
    print(f"输入目录: {args.input_dir}")
    print(f"输出目录: {args.output_dir}")
    print(f"跳过已存在: {args.skip_existing}")

    if args.dry_run:
        audio_files = find_audio_files(args.input_dir)
        print(f"\n预览模式 - 找到 {len(audio_files)} 个文件:")
        for file in audio_files:
            print(f"  - {file.name}")
        return

    # 执行批量处理
    results = batch_process(
        args.input_dir, args.output_dir, skip_existing=args.skip_existing
    )

    # 生成报告
    generate_summary_report(results, args.report)


if __name__ == "__main__":
    main()
