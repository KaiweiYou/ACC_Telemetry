#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACC_Telemetry 安装脚本

这个脚本用于帮助用户快速安装和配置ACC_Telemetry项目。
它将检查必要的依赖项，创建配置文件，并提供基本的使用说明。

使用方法:
    python install.py
"""

import os
import sys
import subprocess
import shutil
import platform

def print_header():
    """打印安装脚本头部信息"""
    print("\n====================================")
    print("    ACC_Telemetry 安装程序     ")
    print("====================================")
    print("这个脚本将帮助您安装和配置ACC_Telemetry项目。")
    print("====================================")

def check_python_version():
    """检查Python版本"""
    print("\n[1/5] 检查Python版本...")
    
    major, minor = sys.version_info[:2]
    print(f"检测到Python版本: {major}.{minor}")
    
    if major < 3 or (major == 3 and minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        return False
    
    print("✓ Python版本符合要求")
    return True

def install_dependencies():
    """安装必要的依赖项"""
    print("\n[2/5] 安装依赖项...")
    
    # 询问安装方式
    print("请选择安装方式:")
    print("  1. 使用requirements.txt安装依赖")
    print("  2. 使用setup.py安装整个包（推荐）")
    
    install_method = input("请选择 (1/2): ").strip()
    
    if install_method == "1":
        # 使用requirements.txt安装
        print("使用requirements.txt安装依赖项...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ 依赖项安装成功")
        except subprocess.CalledProcessError as e:
            print(f"错误: 安装依赖项失败: {e}")
            return False
    else:
        # 使用setup.py安装整个包
        print("使用setup.py安装ACC_Telemetry包...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "."])
            print("✓ ACC_Telemetry包安装成功")
        except subprocess.CalledProcessError as e:
            print(f"错误: 安装ACC_Telemetry包失败: {e}")
            return False
    
    # 询问是否安装可选包
    optional_packages = [
        "matplotlib",
        "numpy",
        "pandas",
        "pyserial"
    ]
    
    print("\n以下是可选的依赖项，用于示例程序和高级功能:")
    for i, package in enumerate(optional_packages):
        print(f"  {i+1}. {package}")
    
    install_optional = input("\n是否安装这些可选依赖项? (y/n): ").strip().lower()
    
    if install_optional == 'y':
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + optional_packages)
            print("✓ 可选依赖项安装成功")
        except subprocess.CalledProcessError as e:
            print(f"警告: 安装可选依赖项失败: {e}")
            print("您可以稍后手动安装这些包")
    
    return True

def check_acc_installation():
    """检查ACC游戏安装"""
    print("\n[3/5] 检查ACC游戏安装...")
    
    # 检测操作系统
    system = platform.system()
    print(f"检测到操作系统: {system}")
    
    if system == "Windows":
        # 常见的ACC安装路径
        possible_paths = [
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Assetto Corsa Competizione",
            "D:\\Steam\\steamapps\\common\\Assetto Corsa Competizione",
            "E:\\Steam\\steamapps\\common\\Assetto Corsa Competizione"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✓ 在 {path} 找到ACC游戏安装")
                return True
        
        print("警告: 未找到ACC游戏安装")
        print("请确保ACC游戏已安装，并且在运行遥测工具时启动游戏")
    else:
        print("注意: 在非Windows系统上，无法自动检测ACC游戏安装")
        print("请确保ACC游戏已安装，并且在运行遥测工具时启动游戏")
    
    return True  # 即使没有找到游戏，也继续安装

def create_config():
    """创建或更新配置文件"""
    print("\n[4/5] 创建配置文件...")
    
    config_path = "config.py"
    
    # 检查配置文件是否已存在
    if os.path.exists(config_path):
        overwrite = input(f"{config_path} 已存在。是否覆盖? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("保留现有配置文件")
            return True
    
    # 复制默认配置文件
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write('''
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
''')
        print(f"✓ 配置文件已创建: {config_path}")
        return True
    except Exception as e:
        print(f"错误: 创建配置文件失败: {e}")
        return False

def print_instructions():
    """打印使用说明"""
    print("\n[5/5] 安装完成!")
    print("\n====================================")
    print("      ACC_Telemetry 使用说明     ")
    print("====================================")
    print("\n运行方式:")
    print("  1. 启动Assetto Corsa Competizione游戏")
    print("  2. 使用以下命令运行不同功能:")
    
    # 如果使用setup.py安装了包
    print("\n  如果您使用setup.py安装了包:")
    print("     - 终端显示:  acc-telemetry terminal")
    print("     - 图形仪表盘: acc-telemetry dashboard")
    print("     - OSC数据发送: acc-telemetry osc")
    
    # 如果直接运行脚本
    print("\n  或者直接运行脚本:")
    print("     - 终端显示:  python main.py terminal")
    print("     - 图形仪表盘: python main.py dashboard")
    print("     - OSC数据发送: python main.py osc")
    
    print("\n示例程序:")
    print("  examples目录包含多个示例程序，展示了如何使用ACC_Telemetry的不同功能")
    print("  详情请参阅 examples/README.md")
    print("\n配置:")
    print("  编辑config.py文件可以自定义程序的行为")
    print("\n测试:")
    print("  运行 python test_telemetry.py 可以测试基本功能")
    print("====================================")

def main():
    """主函数"""
    print_header()
    
    # 检查Python版本
    if not check_python_version():
        print("\n安装失败: Python版本不符合要求")
        return False
    
    # 安装依赖项
    if not install_dependencies():
        print("\n安装失败: 无法安装必要的依赖项")
        return False
    
    # 检查ACC游戏安装
    check_acc_installation()
    
    # 创建配置文件
    if not create_config():
        print("\n安装失败: 无法创建配置文件")
        return False
    
    # 打印使用说明
    print_instructions()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nACC_Telemetry安装成功!")
        else:
            print("\nACC_Telemetry安装失败，请查看上面的错误信息")
    except KeyboardInterrupt:
        print("\n安装被用户中断")
    except Exception as e:
        print(f"\n安装过程中发生错误: {e}")