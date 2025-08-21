#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import stat

def fix_excel_permissions():
    """修复所有已执行Excel文件的权限问题"""
    
    input_dir = '/Users/runbo/Documents/superspider-main/input'
    
    # 查找所有【已执行】开头的Excel文件
    pattern = os.path.join(input_dir, '【已执行】*.xlsx')
    excel_files = glob.glob(pattern)
    
    print(f"找到 {len(excel_files)} 个已执行的Excel文件:")
    
    for excel_file in excel_files:
        print(f"\n处理文件: {os.path.basename(excel_file)}")
        
        # 检查当前权限
        current_mode = oct(os.stat(excel_file).st_mode)[-3:]
        print(f"  当前权限: {current_mode}")
        
        # 修改权限为644 (rw-r--r--)
        try:
            os.chmod(excel_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            new_mode = oct(os.stat(excel_file).st_mode)[-3:]
            print(f"  新权限: {new_mode}")
            print(f"  ✓ 权限修复成功")
        except Exception as e:
            print(f"  ✗ 权限修复失败: {e}")
    
    print(f"\n权限修复完成！")

if __name__ == '__main__':
    fix_excel_permissions()