# 🎵 ACC遥测音乐系统 🏎️

## 概述

ACC遥测音乐系统是一个创新的项目，它将Assetto Corsa Competizione (ACC) 的实时遥测数据转换为动态音乐体验。类似于奔驰的MBUX Sound Drive功能，这个系统通过数据声化技术，让驾驶体验变成一场音乐演出。

## 功能特性

### 🎼 音乐化映射
- **节奏控制**: 车速和引擎转速控制音乐的BPM和节奏复杂度
- **和声生成**: 转向角度和档位影响音调和和声结构
- **动态表现**: 油门和制动控制音量和音乐强度
- **音色变化**: 引擎温度和轮胎压力影响滤波器和音色特性
- **空间效果**: 横向G力控制立体声平衡和空间音效

### 🔧 技术架构
- **实时处理**: 60Hz高频率数据更新，确保音乐与驾驶同步
- **SuperCollider集成**: 使用专业音频合成引擎生成高质量音乐
- **OSC通信**: 通过Open Sound Control协议实现低延迟数据传输
- **模块化设计**: 可扩展的架构，支持自定义音乐映射规则

### 🖥️ 用户界面
- **图形界面**: 直观的GUI控制面板，实时监控系统状态
- **命令行模式**: 轻量级CLI模式，适合高级用户
- **配置管理**: 灵活的参数配置和预设保存/加载
- **实时监控**: 遥测数据和音乐参数的实时显示

## 系统要求

### 软件要求
- **Python**: 3.7或更高版本
- **SuperCollider**: 3.11或更高版本
- **ACC游戏**: 启用遥测数据输出
- **操作系统**: Windows 10/11 (主要测试平台)

### Python依赖
```bash
pip install python-osc
pip install tkinter  # 通常随Python安装
```

### 可选依赖 (用于创建快捷方式)
```bash
pip install winshell pywin32
```

## 安装和设置

### 1. 下载和安装SuperCollider
1. 访问 [SuperCollider官网](https://supercollider.github.io/) 下载并安装
2. 启动SuperCollider IDE
3. 打开项目中的 `supercollider/acc_music_engine.scd` 文件
4. 运行脚本 (Ctrl+Enter 或点击运行按钮)

### 2. 配置ACC遥测
1. 启动ACC游戏
2. 进入设置 → 常规 → 遥测
3. 启用遥测数据输出
4. 确保输出格式为共享内存

### 3. 启动音乐系统

#### 方法一: GUI模式 (推荐)
```bash
python start_music_system.py
```

#### 方法二: 命令行模式
```bash
python start_music_system.py --cli
```

#### 方法三: 创建桌面快捷方式
```bash
python start_music_system.py --shortcut
```

## 使用指南

### GUI界面操作

1. **启动系统**
   - 点击"启动音乐系统"按钮
   - 系统会自动连接ACC遥测数据
   - SuperCollider音乐引擎开始工作

2. **配置参数**
   - 调整更新频率 (建议30-60Hz)
   - 设置BPM范围 (推荐80-180)
   - 调节敏感度参数
   - 保存/加载配置预设

3. **监控状态**
   - 实时查看系统运行状态
   - 监控遥测数据连接
   - 观察音乐参数变化

### 命令行操作

```bash
# 显示帮助
python start_music_system.py --help

# 检查系统依赖
python start_music_system.py --check-deps

# 显示系统信息
python start_music_system.py --info

# 使用自定义配置
python start_music_system.py --cli --config my_config.json

# 启用详细日志
python start_music_system.py --verbose
```

## 音乐映射规则

### 节奏 (Rhythm)
- **速度 → BPM**: 0-300 km/h 映射到 80-180 BPM
- **转速 → 节奏复杂度**: 高转速增加副节拍和装饰音
- **档位 → 节奏模式**: 不同档位触发不同的节奏模式

### 和声 (Harmony)
- **转向 → 音调偏移**: 左右转向改变基础音调 (±12半音)
- **档位 → 音调高度**: 档位越高，基础音调越高
- **速度 → 和声密度**: 高速时增加和声复杂度

### 动态 (Dynamics)
- **油门 → 音量**: 油门深度直接影响音乐音量
- **制动 → 音色变化**: 制动时改变音色特性
- **加速度 → 音乐强度**: 急加速/减速影响音乐的戏剧性

### 音色 (Timbre)
- **引擎温度 → 滤波频率**: 温度越高，音色越明亮
- **轮胎压力 → 共振**: 压力影响音色的共振特性
- **引擎负载 → 失真度**: 高负载时增加音色的复杂度

### 空间 (Spatial)
- **横向G力 → 立体声平衡**: 转弯时音乐在左右声道间移动
- **速度 → 混响深度**: 高速时增加空间感
- **制动 → 延迟效果**: 制动时增加回声效果

## 配置文件格式

```json
{
  "update_rate": 60,
  "osc_port": 57120,
  "bpm_min": 80,
  "bpm_max": 180,
  "speed_sensitivity": 1.0,
  "steering_sensitivity": 1.0,
  "pedal_sensitivity": 1.0
}
```

## 故障排除

### 常见问题

1. **无法连接ACC遥测数据**
   - 确保ACC游戏正在运行
   - 检查遥测设置是否正确启用
   - 确认没有其他程序占用遥测数据

2. **SuperCollider连接失败**
   - 确保SuperCollider正在运行
   - 检查OSC端口是否正确 (默认57120)
   - 确认防火墙没有阻止连接

3. **音乐没有声音**
   - 检查SuperCollider音频设置
   - 确认系统音量和音频设备
   - 查看SuperCollider控制台是否有错误信息

4. **系统性能问题**
   - 降低更新频率 (30Hz或更低)
   - 关闭不必要的音乐元素
   - 检查CPU和内存使用情况

### 日志文件
系统运行时会生成日志文件 `acc_music_system.log`，包含详细的错误信息和调试数据。

## 高级功能

### 自定义音乐映射

可以通过修改 `supercollider_engine.py` 中的映射函数来创建自定义的音乐规则：

```python
def custom_mapping(self, data):
    # 自定义映射逻辑
    bpm = self.calculate_custom_bpm(data)
    pitch = self.calculate_custom_pitch(data)
    return {'bpm': bpm, 'pitch': pitch}
```

### 扩展SuperCollider脚本

可以修改 `supercollider/acc_music_engine.scd` 来添加新的音频合成器和效果：

```supercollider
// 添加新的合成器定义
SynthDef(\customSynth, {
    // 自定义合成器代码
}).add;
```

### 多车支持

系统支持同时处理多辆车的遥测数据，可以为每辆车分配不同的音乐通道。

## 开发和贡献

### 项目结构
```
ACC_Telemetry/
├── acc_telemetry/
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── supercollider_engine.py    # SuperCollider引擎
│   │   ├── music_integration.py       # 音乐集成主类
│   │   └── music_gui.py              # GUI界面
│   ├── telemetry.py                  # 遥测数据处理
│   └── ...
├── supercollider/
│   └── acc_music_engine.scd          # SuperCollider脚本
├── start_music_system.py             # 启动脚本
└── MUSIC_SYSTEM_README.md            # 本文档
```

### 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone <repository_url>
cd ACC_Telemetry

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/
```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 致谢

- **SuperCollider社区**: 提供了强大的音频合成平台
- **ACC开发团队**: 提供了丰富的遥测数据接口
- **奔驰MBUX Sound Drive**: 提供了创意灵感
- **开源社区**: 提供了各种优秀的库和工具

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues]()
- 邮箱: [your-email@example.com]()
- 讨论区: [项目讨论区]()

---

**享受音乐化的驾驶体验！** 🎵🏎️