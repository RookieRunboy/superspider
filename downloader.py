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
import logging


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
        # 用于收集失败的下载链接
        self.failed_downloads = []
    
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
                    # 记录失败的下载
                    self.failed_downloads.append({
                        'url': attachment['url'],
                        'filename': attachment['filename'],
                        'page_title': attachment.get('page_title', '未知标题'),
                        'error': str(e),
                        'error_type': type(e).__name__
                    })
                    print(f"下载失败 {attachment['url']}: {e}")
        
        return downloaded_files
    
    def get_failed_downloads(self) -> List[Dict[str, Any]]:
        """
        获取失败的下载记录
        
        Returns:
            失败下载记录列表
        """
        return self.failed_downloads.copy()
    
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
            
            # 生成优化的文件名格式，限制总长度
            new_filename = self._generate_safe_filename(page_title, attachment_counter, original_filename)
            
            # 确保目录存在
            self.config.attachments_dir.mkdir(parents=True, exist_ok=True)
            
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
                
            except requests.exceptions.HTTPError as e:
                # 对于特定的HTTP错误，不进行重试
                if e.response.status_code in [400, 401, 403, 404, 410, 451]:
                    # 客户端错误，通常是永久性的，不需要重试
                    raise NetworkError(f"HTTP {e.response.status_code} 错误（永久性失败）: {url}")
                elif e.response.status_code in [429, 500, 502, 503, 504]:
                    # 服务器错误或限流，可以重试
                    if attempt < self.config.retry_times - 1:
                        time.sleep(self.config.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise NetworkError(f"HTTP {e.response.status_code} 错误（重试失败）: {url}")
                else:
                    # 其他HTTP错误，尝试重试
                    if attempt < self.config.retry_times - 1:
                        time.sleep(self.config.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise NetworkError(f"HTTP {e.response.status_code} 错误: {url}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # 网络连接错误，可以重试
                if attempt < self.config.retry_times - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                else:
                    raise NetworkError(f"网络连接错误: {url} - {str(e)}")
            except Exception as e:
                # 其他未知错误
                if attempt < self.config.retry_times - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                else:
                    raise NetworkError(f"下载失败: {url} - {str(e)}")
    
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
        
        # 限制长度（为组合文件名预留空间）
        if len(filename) > 100:
            filename = filename[:100]
        
        # 移除首尾空格和点
        filename = filename.strip(' .')
        
        return filename
    
    def _generate_safe_filename(self, page_title: str, attachment_counter: int, original_filename: str) -> str:
        """生成安全的文件名，确保总长度不超过系统限制"""
        # 清理页面标题
        clean_title = self._sanitize_filename(page_title)
        
        # 限制标题长度
        max_title_length = 80
        if len(clean_title) > max_title_length:
            clean_title = clean_title[:max_title_length]
        
        # 获取文件扩展名
        if '.' in original_filename:
            name_part, ext_part = original_filename.rsplit('.', 1)
            ext_part = f".{ext_part}"
        else:
            name_part = original_filename
            ext_part = ""
        
        # 限制原始文件名长度
        max_original_length = 50
        if len(name_part) > max_original_length:
            name_part = name_part[:max_original_length]
        
        # 组合文件名：{title}_附件{n}_{original_name}{ext}
        base_filename = f"{clean_title}_附件{attachment_counter}_{name_part}{ext_part}"
        
        # 确保总长度不超过200字符（大多数文件系统的安全限制）
        max_total_length = 200
        if len(base_filename) > max_total_length:
            # 如果还是太长，进一步缩短标题
            excess = len(base_filename) - max_total_length
            new_title_length = max(10, len(clean_title) - excess)
            clean_title = clean_title[:new_title_length]
            base_filename = f"{clean_title}_附件{attachment_counter}_{name_part}{ext_part}"
        
        return base_filename
    
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