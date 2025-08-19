#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页解析模块

该模块负责解析网页内容，提取附件链接。

作者: SuperSpider Team
版本: 1.0.0
"""

import requests
import chardet
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional
from error_handler import NetworkError, ParseError
import random


class WebParser:
    """网页解析器"""
    
    def __init__(self, config):
        """
        初始化网页解析器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update(self.config.headers)
    
    def parse_page(self, url: str, title: str) -> List[Dict[str, Any]]:
        """
        解析网页，提取附件链接
        
        Args:
            url: 网页URL
            title: 网页标题
            
        Returns:
            附件信息列表
        """
        try:
            # 获取网页内容
            response = self._fetch_page(url)
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取附件链接
            attachments = self._extract_attachments(soup, url, title)
            
            return attachments
            
        except Exception as e:
            raise ParseError(f"解析网页失败 {url}: {e}")
    
    def _fetch_page(self, url: str) -> requests.Response:
        """获取网页内容"""
        try:
            # 随机选择User-Agent
            user_agent = random.choice(self.config.user_agents)
            headers = {'User-Agent': user_agent}
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.config.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"网络请求失败: {e}")
    
    def _extract_attachments(self, soup: BeautifulSoup, base_url: str, page_title: str) -> List[Dict[str, Any]]:
        """提取附件链接"""
        attachments = []
        
        # 查找所有链接
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href'].strip()
            if not href:
                continue
            
            # 转换为绝对URL
            absolute_url = urljoin(base_url, href)
            
            # 检查是否是附件
            if self._is_attachment(absolute_url, link):
                # 获取链接文本作为文件名
                link_text = link.get_text(strip=True)
                if not link_text:
                    link_text = self._extract_filename_from_url(absolute_url)
                
                attachment_info = {
                    'url': absolute_url,
                    'filename': link_text,
                    'page_title': page_title,
                    'page_url': base_url,
                    'link_text': link_text
                }
                
                attachments.append(attachment_info)
        
        return attachments
    
    def _is_attachment(self, url: str, link_element) -> bool:
        """判断链接是否是附件"""
        # 检查URL扩展名
        parsed_url = urlparse(url.lower())
        path = parsed_url.path
        
        # 检查文件扩展名
        for ext in self.config.attachment_extensions:
            if path.endswith(ext):
                return True
        
        # 检查链接文本中的关键词
        link_text = link_element.get_text(strip=True).lower()
        attachment_keywords = [
            '下载', 'download', '附件', 'attachment', '文件', 'file',
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'
        ]
        
        for keyword in attachment_keywords:
            if keyword in link_text:
                return True
        
        # 检查链接属性
        if link_element.get('download') is not None:
            return True
        
        return False
    
    def _extract_filename_from_url(self, url: str) -> str:
        """从URL中提取文件名"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        if path:
            filename = path.split('/')[-1]
            if filename and '.' in filename:
                return filename
        
        return "未知文件"