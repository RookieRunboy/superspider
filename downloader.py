#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载器模块

该模块负责下载附件文件。

作者: SuperSpider Team
版本: 1.0.0
"""

import os
import requests
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from error_handler import NetworkError, FileError
import time
import random


class Downloader:
    """文件下载器"""
    
    def __init__(self, config):
        """
        初始化下载器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
        # 用于跟踪每个title下的附件计数
        self.title_attachment_counters = {}
    
    def download_files(self, attachments: List[Dict[str, Any]]) -> List[str]:
        """
        并发下载文件
        
        Args:
            attachments: 附件信息列表
            
        Returns:
            成功下载的文件路径列表
        """
        if not attachments:
            return []
        
        downloaded_files = []
        
        with ThreadPoolExecutor(max_workers=self.config.concurrent_limit) as executor:
            # 提交下载任务
            future_to_attachment = {
                executor.submit(self._download_single_file, attachment): attachment
                for attachment in attachments
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_attachment):
                attachment = future_to_attachment[future]
                try:
                    file_path = future.result()
                    if file_path:
                        downloaded_files.append(file_path)
                except Exception as e:
                    print(f"下载失败 {attachment['url']}: {e}")
        
        return downloaded_files
    
    def _download_single_file(self, attachment: Dict[str, Any]) -> str:
        """
        下载单个文件
        
        Args:
            attachment: 附件信息
            
        Returns:
            下载的文件路径，失败时返回None
        """
        url = attachment['url']
        filename = attachment['filename']
        page_title = attachment.get('page_title', '未知标题')
        
        try:
            # 获取原始文件名
            original_filename = self._sanitize_filename(filename)
            if not original_filename:
                original_filename = self._extract_filename_from_url(url)
            
            # 计算同一title下的附件序号
            attachment_counter = self._get_attachment_counter(page_title)
            
            # 生成新的文件名格式：{title}_附件{n}_{original_attachment_name}
            new_filename = f"{page_title}_附件{attachment_counter}_{original_filename}"
            
            # 生成文件路径
            file_path = self.config.attachments_dir / new_filename
            
            # 如果文件已存在，添加序号
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_part = original_path.stem
                ext_part = original_path.suffix
                file_path = original_path.parent / f"{name_part}_{counter}{ext_part}"
                counter += 1
            
            # 下载文件
            self._download_with_retry(url, file_path)
            
            return str(file_path)
            
        except Exception as e:
            raise NetworkError(f"下载文件失败 {url}: {e}")
    
    def _download_with_retry(self, url: str, file_path: Path):
        """带重试的下载"""
        for attempt in range(self.config.retry_times):
            try:
                # 随机选择User-Agent
                user_agent = random.choice(self.config.user_agents)
                headers = {'User-Agent': user_agent}
                
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.config.timeout,
                    stream=True
                )
                response.raise_for_status()
                
                # 写入文件
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                return  # 下载成功
                
            except Exception as e:
                if attempt < self.config.retry_times - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        if not filename:
            return ""
        
        # 移除或替换非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        
        # 移除控制字符
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]
        
        # 移除首尾空格和点
        filename = filename.strip(' .')
        
        return filename
    
    def _extract_filename_from_url(self, url: str) -> str:
        """从URL中提取文件名"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        if path:
            filename = path.split('/')[-1]
            if filename and '.' in filename:
                return filename
        
        return f"file_{int(time.time())}.bin"
    
    def _get_attachment_counter(self, page_title: str) -> int:
        """
        获取指定title下的附件序号
        
        Args:
            page_title: 页面标题
            
        Returns:
            附件序号
        """
        if page_title not in self.title_attachment_counters:
            self.title_attachment_counters[page_title] = 0
        
        self.title_attachment_counters[page_title] += 1
        return self.title_attachment_counters[page_title]