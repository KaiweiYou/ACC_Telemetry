#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC遥测音乐系统启动脚本

这个脚本是一个便捷的启动器，实际功能在 acc_telemetry.audio.start_music_system 模块中实现。
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == '__main__':
    from acc_telemetry.audio.start_music_system import main
    main()