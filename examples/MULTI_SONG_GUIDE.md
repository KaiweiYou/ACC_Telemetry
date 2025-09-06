# 多歌曲功能使用指南

## 概述

ACC_Telemetry 现在支持多歌曲功能，您可以一次性添加和管理多首歌曲，实现更丰富的音乐交互体验。

## 文件结构要求

### 歌曲目录结构
```
songs/
├── song1/
│   ├── drums.wav
│   ├── bass.wav
│   ├── vocals.wav
│   ├── other.wav
│   └── analysis.json
├── song2/
│   ├── drums.wav
│   ├── bass.wav
│   ├── vocals.wav
│   ├── other.wav
│   └── analysis.json
└── ...
```

### 必需文件
- **分轨文件**: `drums.wav`, `bass.wav`, `vocals.wav`, `other.wav`
- **分析文件**: `analysis.json` (由 song_analyzer.py 生成)

## 快速开始

### 1. 批量处理歌曲

使用批量处理工具自动处理多首歌曲：

```bash
# 处理整个音乐目录
python examples/batch_song_processor.py "C:\Music" --output-dir ./songs --skip-existing

# 仅预览，不实际处理
python examples/batch_song_processor.py "C:\Music" --dry-run

# 生成处理报告
python examples/batch_song_processor.py "C:\Music" --report processing_report.json
```

### 2. 启动多歌曲运行器

```bash
# 启动交互式控制台
python examples/multi_song_runner.py

# 指定自定义歌曲目录
set ACC_SONGS_DIR=C:\MyMusic && python examples/multi_song_runner.py
```

### 3. 交互式命令

在控制台中可以使用以下命令：

- `list` - 显示所有可用歌曲
- `play [n]` - 播放指定编号的歌曲
- `next` - 播放下一首
- `prev` - 播放上一首
- `mode [sequential/random/repeat]` - 设置播放模式
- `info` - 显示当前歌曲信息
- `quit` - 退出程序

## 播放模式说明

### Sequential (顺序播放)
按列表顺序播放歌曲，播放完最后一首后停止。

### Random (随机播放)
从所有可用歌曲中随机选择一首播放。

### Repeat (单曲循环)
重复播放当前选中的歌曲。

## 高级功能

### 自动切换
多歌曲运行器支持自动切换到下一首歌曲，无需手动操作。

### 配置文件
编辑 `examples/song_config.json` 来自定义行为：

```json
{
  "playback_settings": {
    "mode": "random",
    "auto_advance": true,
    "shuffle_on_start": true
  }
}
```

## 歌曲准备流程

### 手动准备
1. 使用 Demucs 分离音频分轨
2. 运行 song_analyzer.py 生成 analysis.json
3. 将文件组织到标准目录结构中

### 自动准备
使用批量处理工具自动完成所有步骤：

```bash
# 完整流程
python examples/batch_song_processor.py "音乐目录" --output-dir ./songs
```

## 故障排除

### 常见问题

1. **找不到歌曲**
   - 检查文件结构是否正确
   - 确保包含所有必需文件
   - 验证文件扩展名

2. **Demucs 未找到**
   - 安装 demucs: `pip install demucs`
   - 或使用 conda: `conda install -c conda-forge demucs`

3. **分析失败**
   - 检查音频文件是否损坏
   - 确保文件格式支持
   - 查看错误日志

### 调试模式

启用详细日志：

```bash
python examples/multi_song_runner.py --verbose
```

## 性能优化

### 批量处理建议
- 一次处理不超过 50 首歌曲
- 使用 SSD 提高 I/O 性能
- 关闭其他大型应用程序

### 内存管理
- 每首歌曲占用约 100-500MB 内存
- 根据系统内存限制并发处理数量

## 扩展功能

### 自定义分析
可以通过修改 `song_analyzer.py` 来添加自定义分析功能：

- 添加新的音乐特征提取
- 修改 BPM 检测算法
- 增加情感分析

### 集成外部播放器
可以与其他音乐播放器集成：

- Spotify API
- 本地音乐库
- 在线流媒体服务

## 示例工作流程

### 完整设置流程

1. **准备音乐文件**
   ```bash
   mkdir my_music
   # 复制音乐文件到 my_music
   ```

2. **批量处理**
   ```bash
   python examples/batch_song_processor.py "my_music" --output-dir ./songs
   ```

3. **启动交互模式**
   ```bash
   python examples/multi_song_runner.py
   ```

4. **享受多歌曲体验**
   - 在控制台输入命令
   - 体验不同歌曲的交互效果
   - 切换播放模式探索不同体验

## 技术支持

如需更多帮助：
- 查看 `examples/README.md`
- 提交 GitHub Issue
- 查看日志文件获取详细信息