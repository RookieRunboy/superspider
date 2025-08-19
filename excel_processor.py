#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel处理模块

该模块负责读取和处理Excel文件中的URL数据。

作者: SuperSpider Team
版本: 1.0.0
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from error_handler import FileError


class ExcelProcessor:
    """Excel文件处理器"""
    
    def __init__(self, config):
        """
        初始化Excel处理器
        
        Args:
            config: 配置对象
        """
        self.config = config
    
    def read_excel(self, excel_file: str) -> List[Dict[str, Any]]:
        """
        读取Excel文件中的URL数据
        
        Args:
            excel_file: Excel文件路径
            
        Returns:
            包含URL和标题的字典列表
        """
        try:
            excel_path = Path(excel_file)
            if not excel_path.exists():
                raise FileError(f"Excel文件不存在: {excel_file}")
            
            # 读取Excel文件
            df = pd.read_excel(excel_file)
            
            # 查找URL列
            url_column = self._find_url_column(df)
            if url_column is None:
                raise FileError("Excel文件中未找到URL列")
            
            # 查找标题列
            title_column = self._find_title_column(df)
            
            # 提取数据
            urls_data = []
            for index, row in df.iterrows():
                url = str(row[url_column]).strip()
                
                # 跳过空URL
                if pd.isna(row[url_column]) or not url or url.lower() in ['nan', 'none']:
                    continue
                
                # 确保URL格式正确
                if url.startswith('https:/') and not url.startswith('https://'):
                    # 修复缺少斜杠的URL: https:/xxx -> https://xxx
                    url = 'https://' + url[7:]  # 移除 'https:/' 并添加 'https://'
                elif url.startswith('http:/') and not url.startswith('http://'):
                    # 修复缺少斜杠的URL: http:/xxx -> http://xxx
                    url = 'http://' + url[6:]   # 移除 'http:/' 并添加 'http://'
                elif not url.startswith(('http://', 'https://')):
                    if url.startswith('www.'):
                        url = 'https://' + url
                    elif '.' in url:
                        url = 'https://' + url
                    else:
                        continue  # 跳过无效URL
                
                # 获取标题
                if title_column is not None and not pd.isna(row[title_column]):
                    title = str(row[title_column]).strip()
                else:
                    title = f"页面_{index + 1}"
                
                urls_data.append({
                    'url': url,
                    'title': title,
                    'index': index + 1
                })
            
            if not urls_data:
                raise FileError("Excel文件中没有找到有效的URL数据")
            
            return urls_data
            
        except Exception as e:
            if isinstance(e, FileError):
                raise
            raise FileError(f"读取Excel文件失败: {e}")
    
    def _find_url_column(self, df: pd.DataFrame) -> Optional[str]:
        """查找URL列"""
        # 常见的URL列名
        url_column_names = [
            'url', 'URL', 'Url', 'link', 'Link', 'LINK',
            '链接', '网址', '标题链接', 'address', 'Address', 'href'
        ]
        
        # 首先检查列名
        for col_name in url_column_names:
            if col_name in df.columns:
                return col_name
        
        # 检查列内容是否包含URL
        for col in df.columns:
            if df[col].dtype == 'object':  # 只检查文本列
                sample_values = df[col].dropna().head(5)
                url_count = 0
                for value in sample_values:
                    if isinstance(value, str) and ('http' in value.lower() or 'www.' in value.lower()):
                        url_count += 1
                
                if url_count >= len(sample_values) * 0.6:  # 60%以上是URL
                    return col
        
        return None
    
    def _find_title_column(self, df: pd.DataFrame) -> Optional[str]:
        """查找标题列"""
        # 常见的标题列名
        title_column_names = [
            'title', 'Title', 'TITLE', 'name', 'Name', 'NAME',
            '标题', '名称', '题目', 'subject', 'Subject'
        ]
        
        for col_name in title_column_names:
            if col_name in df.columns:
                return col_name
        
        return None