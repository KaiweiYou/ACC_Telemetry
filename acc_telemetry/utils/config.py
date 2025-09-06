#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境变量配置加载模块

该模块提供从.env文件和环境变量加载配置的功能，
支持类型转换和默认值设置。
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union, cast

# 尝试导入dotenv，如果不可用则提供警告
try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv未安装，将只从系统环境变量加载配置")


class Config:
    """配置管理类

    从.env文件和环境变量加载配置，支持类型转换和默认值。
    """

    def __init__(self, env_file: Optional[Union[str, Path]] = None):
        """初始化配置管理器

        Args:
            env_file: .env文件路径，如果为None则尝试在项目根目录查找
        """
        self._values: Dict[str, Any] = {}

        # 如果dotenv可用，尝试加载.env文件
        if DOTENV_AVAILABLE:
            if env_file is None:
                # 尝试在项目根目录查找.env文件
                project_root = Path(__file__).parent.parent.parent
                env_file = project_root / ".env"

            if isinstance(env_file, str):
                env_file = Path(env_file)

            if env_file.exists():
                load_dotenv(dotenv_path=str(env_file))
                logging.info(f"已从{env_file}加载环境变量")
            else:
                logging.warning(f"未找到.env文件: {env_file}")

    def get(self, key: str, default: Any = None, var_type: type = str) -> Any:
        """获取配置值

        Args:
            key: 配置键名
            default: 默认值，如果环境变量不存在则返回此值
            var_type: 配置值类型，支持str, int, float, bool

        Returns:
            转换为指定类型的配置值

        Raises:
            ValueError: 如果类型转换失败
        """
        # 如果已缓存，直接返回
        if key in self._values:
            return self._values[key]

        # 从环境变量获取
        value = os.environ.get(key)

        # 如果环境变量不存在，返回默认值
        if value is None:
            self._values[key] = default
            return default

        # 根据指定类型进行转换
        try:
            if var_type == bool:
                # 特殊处理布尔类型
                value = value.lower()
                if value in ("true", "yes", "1", "y", "t"):
                    result = True
                elif value in ("false", "no", "0", "n", "f"):
                    result = False
                else:
                    raise ValueError(f"无法将'{value}'转换为布尔值")
            else:
                # 其他类型直接转换
                result = var_type(value)

            self._values[key] = result
            return result
        except ValueError as e:
            logging.error(f"配置'{key}'类型转换失败: {e}")
            self._values[key] = default
            return default

    def get_str(self, key: str, default: str = "") -> str:
        """获取字符串类型配置"""
        return cast(str, self.get(key, default, str))

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数类型配置"""
        return cast(int, self.get(key, default, int))

    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数类型配置"""
        return cast(float, self.get(key, default, float))

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔类型配置"""
        return cast(bool, self.get(key, default, bool))


# 创建全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例

    Returns:
        全局配置实例
    """
    return config
