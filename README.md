# ACC_Telemetry

## 项目简介

这是一个用于读取、显示和传输Assetto Corsa Competizione (ACC)赛车模拟游戏遥测数据的工具集。通过读取ACC游戏的共享内存，可以实时获取车辆的各种状态数据，包括速度、转速、档位、轮胎压力、踏板状态等信息。

## 功能特点

- **数据读取**：通过共享内存读取ACC游戏的实时遥测数据
- **终端显示**：在命令行终端中实时显示遥测数据
- **图形界面**：提供基于Tkinter的图形化仪表盘
- **OSC传输**：支持通过OSC协议将数据发送到其他应用程序或设备

## 安装方法

### 前提条件

- Python 3.8 或更高版本
- 安装了Assetto Corsa Competizione游戏

### 安装步骤

1. 克隆或下载本仓库
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

3. 或者直接安装此包：

```bash
pip install .
```

## 使用方法

### 通过主程序使用

安装后，可以通过以下命令使用：

```bash
acc-telemetry [mode]
```

或者直接运行主程序：

```bash
python main.py [mode]
```

其中`[mode]`可以是以下选项之一：
- `terminal`：在终端中显示遥测数据
- `dashboard`：启动图形化仪表盘
- `osc`：将数据通过OSC协议发送

### 直接运行脚本

也可以直接运行各个模块：

#### 终端显示

```bash
python telemetry.py
```

或者使用重构后的模块：

```bash
python -m acc_telemetry.core.telemetry
```

#### 图形界面仪表盘

```bash
python dashboard.py
```

或者使用重构后的模块：

```bash
python -m acc_telemetry.ui.dashboard
```

#### OSC数据发送

```bash
python osc_sender.py
```

或者使用重构后的模块：

```bash
python -m acc_telemetry.utils.osc_sender
```

默认发送到`192.168.10.66:8000`，可以通过修改配置文件更改目标地址。

## 配置说明

可以通过修改`config.py`文件来自定义程序的行为：

- OSC发送目标IP和端口
- 数据更新频率
- 界面显示选项

## 项目结构

```
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖包列表
├── config.py                 # 配置文件
├── main.py                   # 主程序入口
├── telemetry.py              # 遥测数据读取和终端显示（兼容旧版本）
├── dashboard.py              # 图形界面仪表盘（兼容旧版本）
├── osc_sender.py             # OSC数据发送（兼容旧版本）
├── setup.py                  # 安装配置文件
├── acc_telemetry/            # 核心包
│   ├── __init__.py
│   ├── core/                 # 核心功能模块
│   │   ├── __init__.py
│   │   └── telemetry.py      # 遥测数据读取和处理
│   ├── ui/                   # 用户界面模块
│   │   ├── __init__.py
│   │   └── dashboard.py      # 图形化仪表盘
│   └── utils/                # 工具函数模块
│       ├── __init__.py
│       └── osc_sender.py     # OSC数据发送
├── tests/                    # 测试目录
│   └── __init__.py
└── examples/                 # 示例代码
    ├── README.md
    ├── data_logger_example.py
    ├── data_analysis_example.py
    ├── data_visualization_example.py
    ├── osc_receiver_example.py
    └── arduino_integration_example/
        ├── arduino_serial_bridge.py
        └── acc_telemetry_display.ino
```

## 参考资料

- [ACC共享内存文档](https://www.assettocorsa.net/forum/index.php?threads/acc-shared-memory-documentation.59965/)
- [ACC官方论坛](https://www.assettocorsa.net/forum/index.php?forums/assetto-corsa-competizione.1016/)

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。

## 贡献指南

欢迎提交问题报告和功能建议。如果您想贡献代码，请先创建issue讨论您的想法。
