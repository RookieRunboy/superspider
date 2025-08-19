#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理模块

该模块提供统一的错误处理和异常定义。

作者: SuperSpider
版本: 1.0.0
"""

import logging
import traceback
from typing import Optional, Dict, Any


class SuperSpiderError(Exception):
    """SuperSpider基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class NetworkError(SuperSpiderError):
    """网络相关错误"""
    pass


class ParseError(SuperSpiderError):
    """解析相关错误"""
    pass


class FileError(SuperSpiderError):
    """文件操作相关错误"""
    pass


class PDFGenerationError(SuperSpiderError):
    """PDF生成相关错误"""
    pass


class ConfigurationError(SuperSpiderError):
    """配置相关错误"""
    pass


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: Optional[str] = None) -> None:
        """处理错误"""
        error_msg = f"错误发生在 {context}: {str(error)}" if context else str(error)
        
        if isinstance(error, SuperSpiderError):
            self.logger.error(error_msg)
            if error.details:
                self.logger.debug(f"错误详情: {error.details}")
        else:
            self.logger.error(f"未预期的错误: {error_msg}")
            self.logger.debug(f"错误堆栈: {traceback.format_exc()}")
    
    def log_warning(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """记录警告"""
        self.logger.warning(message)
        if details:
            self.logger.debug(f"警告详情: {details}")
    
    def log_info(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """记录信息"""
        self.logger.info(message)
        if details:
            self.logger.debug(f"信息详情: {details}")
