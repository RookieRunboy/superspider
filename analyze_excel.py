#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os

def analyze_excel_file(file_path):
    """分析Excel文件内容，检查是否有爬取结果数据"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        print(f"分析文件: {file_path}")
        print(f"总行数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        print("\n列名:")
        for i, col in enumerate(df.columns):
            print(f"{i+1}. {col}")
        
        # 检查是否有爬取结果相关的列
        result_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['状态', 'status', '附件', 'attachment', 'pdf', '错误', 'error', '完成', 'complete']):
                result_columns.append(col)
        
        if result_columns:
            print("\n发现可能的结果列:")
            for col in result_columns:
                print(f"- {col}")
                # 显示该列的前几个非空值
                non_null_values = df[col].dropna().head(5)
                if not non_null_values.empty:
                    print(f"  示例值: {list(non_null_values)}")
                else:
                    print("  该列为空")
        else:
            print("\n未发现明显的结果列")
        
        # 显示前5行数据
        print("\n前5行数据:")
        print(df.head().to_string())
        
        # 检查是否有URL列
        url_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['url', '链接', 'link', '网址']):
                url_columns.append(col)
        
        if url_columns:
            print(f"\n发现URL列: {url_columns}")
            for col in url_columns:
                non_null_count = df[col].notna().sum()
                print(f"- {col}: {non_null_count} 个非空URL")
        
        return True
        
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python analyze_excel.py <excel_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    analyze_excel_file(file_path)

if __name__ == "__main__":
    main()