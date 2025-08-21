#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Excel写入问题的解决方案

该脚本解决了以下问题：
1. Excel文件权限被设置为只读，导致无法写入结果
2. 提供了完整的诊断和修复流程
"""

import os
import glob
import stat
from pathlib import Path
from excel_processor import ExcelProcessor
from config import Config
from datetime import datetime

def diagnose_and_fix_excel_issues():
    """诊断并修复Excel写入问题"""
    
    print("=== Excel写入问题诊断和修复工具 ===")
    print()
    
    input_dir = '/Users/runbo/Documents/superspider-main/input'
    
    # 1. 查找所有已执行的Excel文件
    pattern = os.path.join(input_dir, '【已执行】*.xlsx')
    excel_files = glob.glob(pattern)
    
    print(f"1. 找到 {len(excel_files)} 个已执行的Excel文件")
    
    for excel_file in excel_files:
        print(f"\n处理文件: {os.path.basename(excel_file)}")
        
        # 2. 检查文件权限
        current_mode = oct(os.stat(excel_file).st_mode)[-3:]
        print(f"  当前权限: {current_mode}")
        
        # 3. 修复权限问题
        if current_mode == '444':  # 只读权限
            print(f"  ⚠️  发现只读权限，正在修复...")
            try:
                os.chmod(excel_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                new_mode = oct(os.stat(excel_file).st_mode)[-3:]
                print(f"  ✓ 权限已修复: {current_mode} -> {new_mode}")
            except Exception as e:
                print(f"  ✗ 权限修复失败: {e}")
                continue
        else:
            print(f"  ✓ 权限正常")
        
        # 4. 测试Excel写入功能
        print(f"  测试Excel写入功能...")
        try:
            config = Config()
            excel_processor = ExcelProcessor(config)
            
            # 读取Excel文件
            urls_data = excel_processor.read_excel(excel_file)
            print(f"    读取到 {len(urls_data)} 条URL数据")
            
            # 检查是否已有结果列
            import pandas as pd
            df = pd.read_excel(excel_file)
            result_columns = ['爬取状态', '下载附件数', 'PDF生成状态', '错误详情', '完成时间']
            existing_columns = [col for col in result_columns if col in df.columns]
            
            if existing_columns:
                print(f"    ✓ 已存在结果列: {existing_columns}")
                # 检查是否有数据
                has_data = False
                for col in existing_columns:
                    non_null_count = df[col].notna().sum()
                    if non_null_count > 0:
                        print(f"      {col}: {non_null_count} 条记录有数据")
                        has_data = True
                
                if has_data:
                    print(f"    ✓ Excel文件已包含爬取结果数据")
                else:
                    print(f"    ⚠️  结果列存在但无数据")
            else:
                print(f"    ⚠️  未找到结果列，可能需要重新执行爬取")
            
        except Exception as e:
            print(f"    ✗ Excel读取测试失败: {e}")
    
    print("\n=== 修复建议 ===")
    print("1. 如果Excel文件权限问题已修复，但仍无结果数据，可能需要重新运行爬虫")
    print("2. 确保在运行爬虫时，Excel文件没有被其他程序（如Excel、WPS等）打开")
    print("3. 如果问题持续存在，请检查磁盘空间和文件系统权限")
    print()
    print("=== 问题根因分析 ===")
    print("问题原因: Excel文件在重命名后被系统设置为只读权限（444）")
    print("解决方案: 将权限修改为644（rw-r--r--），允许所有者读写")
    print("预防措施: 在file_manager.py的rename_processed_file方法中添加权限设置")

def create_prevention_patch():
    """创建预防性补丁，修改file_manager.py"""
    
    print("\n=== 创建预防性补丁 ===")
    
    file_manager_path = '/Users/runbo/Documents/superspider-main/file_manager.py'
    
    # 读取当前文件内容
    with open(file_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经包含权限设置代码
    if 'os.chmod' in content:
        print("✓ file_manager.py 已包含权限设置代码")
        return
    
    # 在重命名后添加权限设置
    old_code = "            # 重命名文件\n            excel_path.rename(new_file_path)\n            \n            return str(new_file_path)"
    new_code = "            # 重命名文件\n            excel_path.rename(new_file_path)\n            \n            # 确保文件权限正确（可读写）\n            import stat\n            os.chmod(new_file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)\n            \n            return str(new_file_path)"
    
    if old_code in content:
        new_content = content.replace(old_code, new_code)
        
        # 备份原文件
        backup_path = file_manager_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已备份原文件: {backup_path}")
        
        # 写入修改后的内容
        with open(file_manager_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ 已更新 file_manager.py，添加权限设置代码")
    else:
        print(f"⚠️  未找到预期的代码模式，请手动添加权限设置")

if __name__ == '__main__':
    diagnose_and_fix_excel_issues()
    create_prevention_patch()