# ACC_Telemetry 配置文件

# OSC发送配置
OSC_CONFIG = {
    'ip': '192.168.10.66',  # 目标IP地址
    'port': 8000,           # 目标端口
    'update_rate': 60       # 每秒更新次数 (Hz)
}

# 仪表盘配置
DASHBOARD_CONFIG = {
    'update_rate': 60,       # 每秒更新次数 (Hz)
    'width': 600,            # 窗口宽度
    'height': 800,           # 窗口高度
    'theme': 'default',      # 界面主题 ('default', 'dark', 'light')
    'font_family': 'Arial'   # 字体
}

# 高级配置
ADVANCED_CONFIG = {
    'debug_mode': False,     # 是否启用调试模式
    'timeout': 5.0,          # 共享内存读取超时时间 (秒)
    'retry_interval': 2.0    # 连接失败后重试间隔 (秒)
}