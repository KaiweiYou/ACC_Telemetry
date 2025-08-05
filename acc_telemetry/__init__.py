"""ACC_Telemetry - Assetto Corsa Competizione 遥测数据处理库"""

__version__ = "1.0.0"
__author__ = "ACC_Telemetry Team"

# 导入主要的类和函数
from .core.telemetry import ACCTelemetry, TelemetryData
from .ui.dashboard import AccDashboard
from .utils.osc_sender import ACCDataSender

__all__ = [
    'ACCTelemetry',
    'TelemetryData', 
    'AccDashboard',
    'ACCDataSender'
]