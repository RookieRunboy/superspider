#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理模块

该模块负责文件和目录的管理操作。

作者: SuperSpider Team
版本: 1.0.0
"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from error_handler import FileError


class FileManager:
    """文件管理器"""
    
    def __init__(self, config):
        """
        初始化文件管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
    
    def create_directories(self):
        """创建必要的目录"""
        try:
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            self.config.attachments_dir.mkdir(parents=True, exist_ok=True)
            self.config.pdfs_dir.mkdir(parents=True, exist_ok=True)
            self.config.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileError(f"创建目录失败: {e}")
    
    def clean_directory(self, directory: Path):
        """清理目录"""
        try:
            if directory.exists():
                shutil.rmtree(directory)
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileError(f"清理目录失败: {e}")
    
    def get_file_size(self, file_path: Path) -> int:
        """获取文件大小"""
        try:
            return file_path.stat().st_size
        except Exception as e:
            raise FileError(f"获取文件大小失败: {e}")
    
    def move_file(self, source: Path, destination: Path):
        """移动文件"""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
        except Exception as e:
            raise FileError(f"移动文件失败: {e}")
    
    def copy_file(self, source: Path, destination: Path):
        """复制文件"""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(destination))
        except Exception as e:
            raise FileError(f"复制文件失败: {e}")
    
    def delete_file(self, file_path: Path):
        """删除文件"""
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            raise FileError(f"删除文件失败: {e}")
    
    def list_files(self, directory: Path, pattern: str = "*") -> List[Path]:
        """列出目录中的文件"""
        try:
            if not directory.exists():
                return []
            return list(directory.glob(pattern))
        except Exception as e:
            raise FileError(f"列出文件失败: {e}")
    
    def get_directory_size(self, directory: Path) -> int:
        """获取目录大小"""
        try:
            total_size = 0
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception as e:
            raise FileError(f"获取目录大小失败: {e}")
    
    def create_zip_file(self, source_dir: Path, zip_file_path: Path, 
                       attachments_folder_name: str = "附件", 
                       pdfs_folder_name: str = "源网页PDF") -> bool:
        """创建zip文件，包含附件和PDF两个文件夹
        
        Args:
            source_dir: 源目录（包含attachments和pdfs子目录）
            zip_file_path: 目标zip文件路径
            attachments_folder_name: zip内附件文件夹名称
            pdfs_folder_name: zip内PDF文件夹名称
            
        Returns:
            bool: 是否成功创建
        """
        try:
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加附件文件夹
                attachments_dir = source_dir / 'attachments'
                if attachments_dir.exists():
                    for file_path in attachments_dir.rglob('*'):
                        if file_path.is_file():
                            # 在zip中的路径：附件文件夹/文件名
                            arcname = f"{attachments_folder_name}/{file_path.name}"
                            zipf.write(file_path, arcname)
                
                # 添加PDF文件夹
                pdfs_dir = source_dir / 'pdfs'
                if pdfs_dir.exists():
                    for file_path in pdfs_dir.rglob('*'):
                        if file_path.is_file():
                            # 在zip中的路径：PDF文件夹/文件名
                            arcname = f"{pdfs_folder_name}/{file_path.name}"
                            zipf.write(file_path, arcname)
            
            return True
        except Exception as e:
            raise FileError(f"创建zip文件失败: {e}")
    
    def cleanup_temp_directory(self, temp_dir: Path):
        """清理临时目录
        
        Args:
            temp_dir: 要清理的临时目录
        """
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            raise FileError(f"清理临时目录失败: {e}")