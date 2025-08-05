# ACC_Telemetry 示例程序

本目录包含了多个示例程序，展示了如何使用ACC_Telemetry库的不同功能。这些示例可以帮助您了解如何将ACC遥测数据用于各种应用场景。

## 示例列表

### 1. OSC接收器示例

**文件:** `osc_receiver_example.py`

**描述:** 展示如何使用python-osc库接收从ACC_Telemetry发送的OSC数据。

**使用方法:**

如果直接运行示例：
```bash
python osc_receiver_example.py [port]
```

如果已安装acc_telemetry包：
```bash
python -m acc_telemetry.examples.osc_receiver_example [port]
```

**参数:**
- `port` - 监听的端口号，默认为8000

**要求:**
- 安装python-osc库: `pip install python-osc`
- 运行ACC游戏和ACC_Telemetry的OSC发送器

### 2. 数据可视化示例

**文件:** `data_visualization_example.py`

**描述:** 使用matplotlib绘制ACC遥测数据的实时图表，包括速度、转速、踏板状态和轮胎压力。

**使用方法:**

如果直接运行示例：
```bash
python data_visualization_example.py
```

如果已安装acc_telemetry包：
```bash
python -m acc_telemetry.examples.data_visualization_example
```

**要求:**
- 安装matplotlib和numpy库: `pip install matplotlib numpy`
- 运行ACC游戏

### 3. 数据记录器示例

**文件:** `data_logger_example.py`

**描述:** 将ACC遥测数据记录到CSV文件中，以便进行离线分析。

**使用方法:**

如果直接运行示例：
```bash
python data_logger_example.py [输出文件名]
```

如果已安装acc_telemetry包：
```bash
python -m acc_telemetry.examples.data_logger_example [输出文件名]
```

**参数:**
- `输出文件名` - 可选，默认为"acc_telemetry_日期时间.csv"

**要求:**
- 运行ACC游戏

### 4. 数据分析示例

**文件:** `data_analysis_example.py`

**描述:** 加载和分析之前记录的ACC遥测数据，计算基本统计信息并生成分析图表。

**使用方法:**

如果直接运行示例：
```bash
python data_analysis_example.py [输入文件]
```

如果已安装acc_telemetry包：
```bash
python -m acc_telemetry.examples.data_analysis_example [输入文件]
```

**参数:**
- `输入文件` - 包含遥测数据的CSV文件路径

**要求:**
- 安装pandas、matplotlib和numpy库: `pip install pandas matplotlib numpy`
- 已有记录的遥测数据CSV文件（可以使用data_logger_example.py生成）

### 5. Arduino集成示例

**目录:** `arduino_integration_example/`

**文件:**
- `arduino_integration_example.ino` - Arduino代码
- `arduino_serial_bridge.py` - Python桥接程序

**描述:** 展示如何将ACC遥测数据与Arduino集成，用于驱动物理仪表盘、LED指示灯或其他硬件设备。

**使用方法:**
1. 将Arduino代码上传到Arduino板
2. 运行Python桥接程序:

如果直接运行示例：
```bash
python arduino_integration_example/arduino_serial_bridge.py [COM端口] [波特率]
```

如果已安装acc_telemetry包：
```bash
python -m acc_telemetry.examples.arduino_integration_example.arduino_serial_bridge [COM端口] [波特率]
```

**参数:**
- `COM端口` - Arduino的串口端口，例如COM3（Windows）或/dev/ttyACM0（Linux）
- `波特率` - 串口通信波特率，默认为115200

**要求:**
- Arduino Uno/Mega/Nano等
- 安装pyserial库: `pip install pyserial`
- 运行ACC游戏

## 注意事项

- 所有示例都需要ACC游戏正在运行
- 部分示例需要安装额外的Python库
- 示例程序可以根据您的需求进行修改和扩展

## 自定义开发

这些示例程序展示了ACC_Telemetry库的基本用法，您可以基于这些示例开发自己的应用程序。例如：

- 创建自定义仪表盘
- 开发赛车数据分析工具
- 构建物理反馈系统
- 与其他硬件或软件集成

如果您有任何问题或建议，请参考主项目的README文件或提交Issue。