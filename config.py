
# ACC_Telemetry 配置文件

# OSC发送配置
OSC_CONFIG = {
    # OSC发送目标IP地址
    'ip': '127.0.0.1',
    # OSC发送目标端口
    'port': 8000,
    # 数据更新频率 (Hz)
    'update_rate': 60
}

# 终端显示配置
TERMINAL_CONFIG = {
    # 是否显示物理数据 (速度、转速、档位、燃油)
    'show_physics': True,
    # 是否显示踏板数据 (油门、刹车、离合器)
    'show_pedals': True,
    # 是否显示轮胎数据 (轮胎压力)
    'show_tires': True,
    # 终端更新频率 (Hz)
    'update_rate': 10
}

# 仪表盘配置
DASHBOARD_CONFIG = {
    # 窗口尺寸
    'window_width': 800,
    'window_height': 600,
    # 是否显示物理数据 (速度、转速、档位、燃油)
    'show_physics': True,
    # 是否显示踏板数据 (油门、刹车、离合器)
    'show_pedals': True,
    # 是否显示轮胎数据 (轮胎压力)
    'show_tires': True,
    # 主题设置 ('default', 'dark', 'light')
    'theme': 'dark',
    # 仪表盘更新频率 (Hz)
    'update_rate': 60
}

# 数据记录配置
LOGGING_CONFIG = {
    # 是否启用数据记录
    'enabled': False,
    # 记录格式 ('csv', 'json')
    'format': 'csv',
    # 记录频率 (Hz)
    'rate': 10,
    # 记录文件路径 (None表示使用默认路径)
    'path': None
}

# 高级配置
ADVANCED_CONFIG = {
    # 调试模式
    'debug_mode': False,
    # 共享内存读取超时 (秒)
    'timeout': 1.0,
    # 重试间隔 (秒)
    'retry_interval': 0.1
}
