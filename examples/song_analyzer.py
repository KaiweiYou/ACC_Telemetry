#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块: song_analyzer

离线音乐分析工具（针对 Demucs 分轨后的单曲项目）。
- 输入: 分轨目录（包含 drums.wav, bass.wav, vocals.wav, other.wav）
- 输出: analysis.json（节拍、速度、能量等基础分析结果）

分析目标:
1) 估计节奏速度 (BPM)
2) 生成节拍时间戳 (beat_times)
3) 估计整体能量轨迹 (energy_curve, 约10Hz采样)

说明:
- 采用 librosa 进行轻量分析，优先基于 drums.wav 提取节拍
- 结果写入到分轨目录，供运行器在驾驶过程中使用
"""

import argparse
import json
import os
from typing import Any, Dict, List

import librosa
import numpy as np


def _downsample_curve(
    times: np.ndarray, values: np.ndarray, target_hz: float = 10.0
) -> Dict[str, List[float]]:
    """将高分辨率曲线下采样为目标频率，以减小输出 JSON 体积。

    Args:
        times (np.ndarray): 时间轴（秒）
        values (np.ndarray): 对应的数值序列
        target_hz (float): 目标采样频率，默认 10Hz
    Returns:
        Dict[str, List[float]]: {"times": [...], "values": [...]} 下采样结果
    """
    if len(times) == 0:
        return {"times": [], "values": []}

    duration = times[-1]
    if duration <= 0:
        return {"times": [], "values": []}

    step = 1.0 / max(1e-6, target_hz)
    t_ds = np.arange(0.0, duration, step)
    v_ds = np.interp(t_ds, times, values)
    return {"times": t_ds.tolist(), "values": v_ds.tolist()}


def analyze_stems(stems_dir: str, sr: int = 44100) -> Dict[str, Any]:
    """对分轨目录进行音乐分析。

    Args:
        stems_dir (str): 分轨目录路径
        sr (int): 采样率，默认 44100
    Returns:
        Dict[str, Any]: 分析结果字典
    """
    drums_path = os.path.join(stems_dir, "drums.wav")
    target_file = drums_path if os.path.isfile(drums_path) else None

    if target_file is None:
        raise FileNotFoundError(f"未找到 drums.wav: {drums_path}")

    # 加载鼓轨（单声道）
    y, _sr = librosa.load(target_file, sr=sr, mono=True)

    # Onset 强度包络，用于 beat tracking 与能量估计
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # Beat tracking: 估计拍速与拍点
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    # 能量曲线: RMS
    hop_length = 512
    frame_length = 2048
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    # 归一化能量到 0-1
    if len(rms) > 0:
        rms_norm = (rms - rms.min()) / max(1e-6, (rms.max() - rms.min()))
    else:
        rms_norm = rms

    energy_ds = _downsample_curve(times, rms_norm, target_hz=10.0)

    return {
        "version": 1,
        "sample_rate": sr,
        "tempo_bpm": float(tempo),
        "beat_times": beat_times,
        "energy_curve": energy_ds,
        "source": "drums.wav",
    }


def save_analysis(stems_dir: str, analysis: Dict[str, Any]) -> str:
    """保存分析结果为 JSON 文件。

    Args:
        stems_dir (str): 分轨目录
        analysis (Dict[str, Any]): 分析结果
    Returns:
        str: 写入的 JSON 文件路径
    """
    out_path = os.path.join(stems_dir, "analysis.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    return out_path


def parse_args() -> argparse.Namespace:
    """解析命令行参数。

    Returns:
        argparse.Namespace: 参数命名空间
    """
    parser = argparse.ArgumentParser(
        description="Demucs 分轨项目离线分析 (BPM/节拍/能量)"
    )
    parser.add_argument(
        "--stems-dir", type=str, required=True, help="分轨目录，包含 drums.wav 等"
    )
    return parser.parse_args()


def main() -> None:
    """程序入口: 执行分析并写出 JSON 文件。"""
    args = parse_args()
    stems_dir = args.stems_dir

    if not os.path.isdir(stems_dir):
        print(f"分轨目录不存在: {stems_dir}")
        raise SystemExit(1)

    try:
        analysis = analyze_stems(stems_dir)
        out_path = save_analysis(stems_dir, analysis)
        print(f"分析完成: {out_path}")
        print(f"Tempo (BPM): {analysis['tempo_bpm']:.1f}")
        print(f"Beat count: {len(analysis['beat_times'])}")
        print(f"Energy samples: {len(analysis['energy_curve']['times'])} @~10Hz")
    except Exception as e:
        print(f"分析失败: {e}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
