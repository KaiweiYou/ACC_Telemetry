# 自动音乐处理指南

本指南介绍如何使用自动音乐处理工具来批量处理音乐文件，自动完成分轨、分析和标准化目录创建，为多歌曲播放系统做准备。

## 功能特点

- **一键式处理**：自动完成整个音乐库的处理流程
- **批量分轨**：使用Demucs自动将歌曲分离为鼓、贝斯、人声和其他轨道
- **自动分析**：生成必要的音频分析文件
- **标准化目录**：创建符合多歌曲播放器要求的标准目录结构
- **交互式配置**：简单的配置选项，无需编辑代码
- **依赖检查**：自动检查并提示安装必要的依赖

## 安装依赖

在使用自动音乐处理工具前，需要安装以下依赖：

1. **Demucs** - 用于音频分轨：
   ```
   pip install demucs
   ```

2. **FFmpeg** - 用于音频处理：
   - Windows: 下载FFmpeg并添加到系统PATH
   - 或使用Conda: `conda install ffmpeg`

3. **Python库** - 自动安装的依赖：
   ```
   pip install numpy librosa soundfile matplotlib
   ```

> 注意：工具会自动检查这些依赖并提示安装。

## 目录结构

推荐的目录结构如下：

```
ACC_Telemetry/
├── examples/
│   ├── auto_music_processor.py    # 自动处理工具
│   ├── auto_process_config.json   # 配置文件
│   ├── batch_song_processor.py    # 批处理核心
│   ├── song_analyzer.py           # 歌曲分析工具
│   └── multi_song_runner.py       # 多歌曲播放器
├── music_input/                   # 输入音乐目录（自动创建）
│   ├── song1.mp3
│   ├── song2.mp3
│   └── ...
└── songs/                         # 处理后的歌曲目录
    ├── song1/
    │   ├── drums.wav
    │   ├── bass.wav
    │   ├── vocals.wav
    │   ├── other.wav
    │   └── analysis.json
    ├── song2/
    │   └── ...
    └── ...
```

## 快速开始

### 步骤 1: 准备音乐文件

1. 创建`music_input`目录（或在配置中指定的目录）
2. 将要处理的音乐文件（MP3、WAV、FLAC等）放入该目录

### 步骤 2: 运行自动处理工具

```
python examples/auto_music_processor.py
```

### 步骤 3: 选择处理方式

工具启动后，会提供三种处理方式：

1. **一键处理**：使用上次的配置直接开始处理
2. **交互式设置**：通过问答方式配置处理选项
3. **预览模式**：仅查看将要处理的文件，不执行实际处理

### 步骤 4: 等待处理完成

处理过程会显示进度信息。完成后，处理报告将保存在输出目录中。

### 步骤 5: 使用多歌曲播放器

处理完成后，可以使用多歌曲播放器播放处理好的歌曲：

```
python examples/multi_song_runner.py
```

## 配置选项

可以通过编辑`auto_process_config.json`文件或使用交互式设置来配置处理选项：

| 选项 | 说明 | 默认值 |
|------|------|--------|
| input_directory | 输入音乐文件目录 | ./music_input |
| output_directory | 输出处理后的歌曲目录 | ./songs |
| audio_extensions | 支持的音频文件扩展名 | [.mp3, .wav, .flac, .m4a, .ogg] |
| demucs_model | 使用的Demucs模型 | htdemucs |
| skip_existing | 是否跳过已存在的歌曲 | true |
| auto_cleanup | 是否自动清理临时文件 | true |

## 常见问题

### 1. 处理时间过长

音频分轨是计算密集型操作，处理时间取决于：
- 歌曲数量和长度
- CPU性能和是否有GPU加速
- Demucs模型复杂度

对于大型音乐库，建议分批处理。

### 2. 分轨质量不佳

如果分轨质量不理想，可以尝试：
- 使用不同的Demucs模型（在配置文件中修改）
- 确保输入音频质量良好
- 对特别重要的歌曲使用专业工具手动分轨

### 3. 内存不足错误

处理高质量音频可能需要大量内存。如果遇到内存不足：
- 关闭其他内存密集型应用
- 分批处理较少的歌曲
- 降低音频质量或长度

## 高级用法

### 自定义分析参数

如需自定义音频分析参数，可以编辑`song_analyzer.py`文件中的相关参数。

### 命令行参数

也可以直接使用`batch_song_processor.py`进行更灵活的命令行操作：

```
python examples/batch_song_processor.py [输入目录] --output-dir [输出目录] --skip-existing --report [报告文件]
```

### 集成到自动化流程

可以将处理脚本集成到自动化流程中，例如：

```python
from examples.auto_music_processor import AutoMusicProcessor

processor = AutoMusicProcessor()
config = processor.load_config()
config["input_directory"] = "path/to/new/music"
processor.process_music_library(config)
```

## 故障排除

如果遇到问题：

1. 确保所有依赖都已正确安装
2. 检查输入音频文件是否可以正常播放
3. 查看处理报告中的错误信息
4. 尝试使用预览模式确认文件可以被正确识别

如需更多帮助，请参考Demucs文档或提交问题报告。