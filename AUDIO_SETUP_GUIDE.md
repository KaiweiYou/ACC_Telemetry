# ACC Telemetry 音频配置指南

## 问题描述
当使用Moonlight串流连接到电脑时，游戏声音可以听到，但音乐引擎的声音无法串流过来。

## 原因分析
音乐引擎使用pygame的音频系统，默认输出到系统默认音频设备。Moonlight串流可能无法捕获到特定音频设备的输出。

## 解决方案

### 方法1: 使用Steam Streaming音频设备（推荐）

1. **运行诊断工具**查看可用设备：
   ```bash
   python audio_device_checker.py
   ```

2. **修改配置文件**：
   编辑 `acc_telemetry/config/audio_config.json`，设置：
   ```json
   {
     "global": {
       "output_device": "扬声器 (Steam Streaming Microphone)",
       "audio_engine": "pygame_stems"
     }
   }
   ```

3. **重启应用程序**使配置生效。

### 方法2: 使用虚拟音频设备

#### 方案A: VoiceMeeter Banana（免费）
1. 下载并安装 [VoiceMeeter Banana](https://vb-audio.com/Voicemeeter/banana.htm)
2. 将音乐引擎输出到 VoiceMeeter Input
3. 在Moonlight设置中启用音频重定向

#### 方案B: VB-Cable（免费）
1. 下载并安装 [VB-Cable](https://vb-audio.com/Cable/)
2. 将音乐引擎输出到 VB-Cable Input
3. 配置Moonlight捕获VB-Cable输出

### 方法3: 使用Windows立体声混音

1. **启用立体声混音**：
   - 右键点击任务栏音量图标 → 声音设置
   - 点击"更多声音设置"
   - 在"录制"选项卡中启用"立体声混音"

2. **配置音频输出**：
   在 `acc_telemetry/config/audio_config.json` 中设置：
   ```json
   {
     "global": {
       "output_device": "立体声混音"
     }
   }
   ```

## 配置文件详解

### 音频引擎配置
```json
{
  "global": {
    "audio_engine": "pygame_stems",  // 使用分轨音频引擎
    "output_device": "设备名称",       // 指定输出设备
    "master_volume": 0.8,            // 主音量 (0.0-1.0)
    "sample_rate": 44100,            // 采样率 (Hz)
    "buffer_size": 512               // 缓冲区大小
  }
}
```

### 获取设备名称
运行诊断工具后，你会看到类似输出：
```
2. 可用音频输出设备:
   [0] PHL 279M1RV (NVIDIA High Definition Audio) <- 默认
   [1] 扬声器 (Steam Streaming Microphone)
   [2] VoiceMeeter Input (VB-Audio VoiceMeeter VAIO)
```

### 常见问题

#### Q: 修改配置后仍无声音
- 确保重启了ACC Telemetry应用
- 检查设备名称是否完全匹配（包括空格和括号）
- 验证设备是否被其他应用占用

#### Q: 声音延迟很高
- 减少缓冲区大小：`"buffer_size": 256`
- 使用有线网络连接
- 关闭其他音频处理软件

#### Q: 音质不好
- 提高采样率：`"sample_rate": 48000`
- 确保使用高质量音频设备
- 检查网络带宽

## 验证配置

1. **启动应用**并进入音乐控制面板
2. **播放测试音乐**
3. **检查Moonlight客户端**是否能听到音乐
4. **查看日志**确认设备设置生效

## 技术支持

如果问题仍未解决：
1. 检查Windows音频设置
2. 更新音频驱动
3. 尝试不同的音频设备
4. 查看应用日志获取更多信息

## 设备推荐顺序

1. **Steam Streaming音频设备**（最简单，推荐）
2. **VoiceMeeter Banana**（功能强大，免费）
3. **VB-Cable**（轻量级，免费）
4. **Windows立体声混音**（系统自带，但可能延迟较高）