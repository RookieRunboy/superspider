#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志模块

该模块提供统一的日志记录功能。

作者: SuperSpider Team
版本: 1.0.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class Logger:
    """日志记录器"""
    
    def __init__(self, log_level: str = 'INFO', log_dir: Path = None):
        """
        初始化日志记录器
        
        Args:
            log_level: 日志级别
            log_dir: 日志目录
        """
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = log_dir or Path('logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f'superspider_{timestamp}.log'
        
        # 设置日志格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建根日志记录器
        self.logger = logging.getLogger('SuperSpider')
        self.logger.setLevel(self.log_level)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 添加文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误"""
        self.logger.critical(message)