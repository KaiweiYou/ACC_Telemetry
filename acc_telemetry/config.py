# ACC_Telemetry 配置文件

# OSC发送配置
OSC_CONFIG = {
    'ip': '192.168.10.66',  # 目标IP地址
    'port': 8000,           # 目标端口
    'update_rate': 60       # 每秒更新次数 (Hz)
}

# 终端显示配置
TERMINAL_CONFIG = {
    'update_rate': 1,        # 每秒更新次数 (Hz)
    'show_pedals': True,     # 是否显示踏板数据
    'show_tires': True,      # 是否显示轮胎数据
    'show_physics': True     # 是否显示物理数据
}

# 仪表盘配置
DASHBOARD_CONFIG = {
    'update_rate': 60,       # 每秒更新次数 (Hz)
    'width': 600,            # 窗口宽度
    'height': 800,           # 窗口高度
    'theme': 'default',      # 界面主题 ('default', 'dark', 'light')
    'font_family': 'Arial',  # 字体
    'show_pedals': True,     # 是否显示踏板数据
    'show_tires': True,      # 是否显示轮胎数据
    'show_physics': True     # 是否显示物理数据
}

# 数据记录配置
LOGGING_CONFIG = {
    'enabled': False,         # 是否启用数据记录
    'log_dir': './logs',      # 日志保存目录
    'log_format': 'csv',      # 日志格式 ('csv', 'json')
    'update_rate': 10,        # 每秒记录次数 (Hz)
    'max_log_size': 100       # 单个日志文件最大大小 (MB)
}

# 高级配置
ADVANCED_CONFIG = {
    'debug_mode': False,      # 是否启用调试模式
    'timeout': 5.0,           # 共享内存读取超时时间 (秒)
    'retry_interval': 2.0     # 连接失败后重试间隔 (秒)
}