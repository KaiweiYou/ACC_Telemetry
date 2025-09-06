#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置模块

该模块提供统一的日志配置功能，支持控制台和文件输出，
并根据环境变量配置日志级别。
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .config import config


def setup_logging(
    app_name: str = "acc_telemetry",
    log_level: Optional[str] = None,
    log_file: Optional[Union[str, Path]] = None,
    log_to_console: bool = True,
) -> logging.Logger:
    """设置日志配置

    Args:
        app_name: 应用程序名称，用于日志记录器名称
        log_level: 日志级别，如果为None则从环境变量获取
        log_file: 日志文件路径，如果为None则根据环境变量配置
        log_to_console: 是否输出到控制台

    Returns:
        配置好的日志记录器
    """
    # 获取日志级别
    if log_level is None:
        log_level = config.get_str("APP_LOG_LEVEL", "INFO")

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # 创建日志记录器
    logger = logging.getLogger(app_name)
    logger.setLevel(numeric_level)

    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 添加控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 添加文件处理器
    if log_file is None:
        # 检查是否启用日志记录
        if config.get_bool("ENABLE_DATA_LOGGING", False):
            log_dir = config.get_str("DATA_LOG_PATH", "./logs")
            log_dir_path = Path(log_dir)
            log_dir_path.mkdir(parents=True, exist_ok=True)

            # 使用当前日期时间创建日志文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir_path / f"{app_name}_{timestamp}.log"

    if log_file:
        if isinstance(log_file, str):
            log_file = Path(log_file)

        # 确保日志目录存在
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 设置为根日志记录器
    logging.root = logger

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志记录器

    Args:
        name: 日志记录器名称，如果为None则返回根日志记录器

    Returns:
        日志记录器实例
    """
    if name is None:
        return logging.getLogger()
    return logging.getLogger(name)
