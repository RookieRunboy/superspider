#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块

该模块提供SuperSpider的配置管理。

作者: SuperSpider Team
版本: 1.0.0
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class Config:
    """配置类"""
    
    def __init__(self, 
                 excel_file: str = None,
                 output_dir: Path = None,
                 concurrent_limit: int = 5,
                 timeout: int = 30,
                 log_level: str = 'INFO',
                 output_format: str = 'pdf'):
        """
        初始化配置
        
        Args:
            excel_file: Excel文件路径
            output_dir: 输出目录
            concurrent_limit: 并发限制
            timeout: 超时时间
            log_level: 日志级别
            output_format: 输出格式
        """
        self.excel_file = excel_file
        self.concurrent_limit = concurrent_limit
        self.timeout = timeout
        self.log_level = log_level
        self.output_format = output_format
        
        # 设置输出目录
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            self.output_dir = Path('downloads') / timestamp
        else:
            self.output_dir = Path(output_dir)
        
        # 创建子目录
        self.attachments_dir = self.output_dir / 'attachments'
        self.pdfs_dir = self.output_dir / 'pdfs'
        self.log_dir = self.output_dir
        
        # 创建目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        self.pdfs_dir.mkdir(parents=True, exist_ok=True)
        
        # 请求配置
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 重试配置
        self.retry_times = 3
        self.retry_delay = 1
        
        # 文件类型配置
        self.attachment_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.txt', '.csv'
        }