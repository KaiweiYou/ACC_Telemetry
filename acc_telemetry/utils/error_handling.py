#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
错误处理模块

该模块提供统一的异常处理机制，包括自定义异常类、
异常装饰器和全局异常处理器。
"""

import functools
import sys
import traceback
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast

from .logging_config import get_logger

# 类型变量定义
F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")

# 获取日志记录器
logger = get_logger(__name__)


class AppError(Exception):
    """应用程序基础异常类

    所有自定义异常应继承此类
    """

    def __init__(self, message: str, error_code: int = 500):
        """初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConfigError(AppError):
    """配置错误异常"""

    def __init__(self, message: str):
        super().__init__(message, 400)


class ConnectionError(AppError):
    """连接错误异常"""

    def __init__(self, message: str):
        super().__init__(message, 503)


class DataError(AppError):
    """数据错误异常"""

    def __init__(self, message: str):
        super().__init__(message, 422)


def handle_exception(
    exc_type: Type[Exception], exc_value: Exception, exc_traceback: Any
) -> None:
    """全局未捕获异常处理器

    Args:
        exc_type: 异常类型
        exc_value: 异常值
        exc_traceback: 异常堆栈
    """
    # 忽略KeyboardInterrupt异常
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # 记录异常信息
    logger.error("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))


def exception_handler(func: F) -> F:
    """异常处理装饰器

    用于捕获和记录函数执行过程中的异常

    Args:
        func: 被装饰的函数

    Returns:
        装饰后的函数
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except AppError as e:
            # 记录自定义异常
            logger.error(
                f"{func.__name__} 发生应用程序异常: {e.message} (代码: {e.error_code})"
            )
            raise
        except Exception as e:
            # 记录未预期的异常
            logger.error(f"{func.__name__} 发生未预期异常: {str(e)}", exc_info=True)
            raise

    return cast(F, wrapper)


def retry(
    max_attempts: int = 3,
    retry_exceptions: tuple = (Exception,),
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0,
    logger_name: Optional[str] = None,
) -> Callable[[F], F]:
    """重试装饰器

    在指定异常发生时自动重试函数

    Args:
        max_attempts: 最大尝试次数
        retry_exceptions: 触发重试的异常类型
        delay_seconds: 初始延迟秒数
        backoff_factor: 退避因子
        logger_name: 日志记录器名称

    Returns:
        装饰器函数
    """
    import time

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            local_logger = get_logger(logger_name or func.__module__)

            attempt = 1
            current_delay = delay_seconds

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    if attempt == max_attempts:
                        local_logger.error(
                            f"{func.__name__} 在 {max_attempts} 次尝试后失败: {str(e)}"
                        )
                        raise

                    local_logger.warning(
                        f"{func.__name__} 尝试 {attempt}/{max_attempts} 失败: {str(e)}. "
                        f"将在 {current_delay:.2f} 秒后重试."
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff_factor
                    attempt += 1

        return cast(F, wrapper)

    return decorator


# 设置全局异常处理器
def setup_exception_handling() -> None:
    """设置全局异常处理"""
    sys.excepthook = handle_exception
