#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperSpider - 智能网页爬虫工具

功能特性：
- 从Excel读取URL列表
- 解析网页提取附件链接
- 并发下载附件文件
- 支持断点续传
- 详细日志记录
- 错误处理和重试机制
- 支持HTML和PDF输出格式
- 完善的中文编码支持

作者: SuperSpider Team
版本: 2.0.0
"""

import os
import sys
import time
import argparse
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import requests
import chardet
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 导入项目模块
from config import Config
from logger import Logger
from excel_processor import ExcelProcessor
from web_parser import WebParser
from downloader import Downloader
from file_manager import FileManager
from error_handler import ErrorHandler
import pdf_generator


class SuperSpider:
    """SuperSpider主类 - 网页爬虫核心引擎"""
    
    def __init__(self, config: Config):
        """初始化SuperSpider
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = Logger(config.log_level, config.log_dir)
        self.excel_processor = ExcelProcessor(config)
        self.web_parser = WebParser(config)
        self.downloader = Downloader(config)
        self.file_manager = FileManager(config)
        self.error_handler = ErrorHandler(config)
        
        # 设置HTTP会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.logger.info(f"SuperSpider初始化完成 - 版本2.0.0")
    
    def smart_decode_response(self, response: requests.Response) -> str:
        """智能解码HTTP响应内容，确保中文字符正确显示
        
        Args:
            response: HTTP响应对象
            
        Returns:
            str: 正确解码的文本内容
        """
        try:
            # 首先尝试从HTTP头获取编码
            content_type = response.headers.get('content-type', '')
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[1].split(';')[0].strip()
                try:
                    return response.content.decode(charset)
                except (UnicodeDecodeError, LookupError):
                    pass
            
            # 使用chardet检测编码
            detected = chardet.detect(response.content)
            if detected['encoding'] and detected['confidence'] > 0.7:
                try:
                    return response.content.decode(detected['encoding'])
                except UnicodeDecodeError:
                    pass
            
            # 尝试常见的中文编码
            for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']:
                try:
                    return response.content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # 最后回退到errors='ignore'
            return response.content.decode('utf-8', errors='ignore')
            
        except Exception as e:
            self.logger.warning(f"编码检测失败: {e}，使用UTF-8忽略错误")
            return response.content.decode('utf-8', errors='ignore')
    
    def run(self, excel_file: str) -> Dict[str, Any]:
        """执行爬虫任务的优化流水线处理
        
        Args:
            excel_file: Excel文件路径
            
        Returns:
            Dict[str, Any]: 执行结果统计
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"开始处理Excel文件: {excel_file}")
            
            # 1. 读取Excel文件
            urls_data = self.excel_processor.read_excel(excel_file)
            if not urls_data:
                raise ValueError("Excel文件中没有找到有效的URL数据")
            
            self.logger.info(f"成功读取 {len(urls_data)} 个URL")
            
            # 2. 执行处理流水线
            results, url_results = self._run_pipeline(urls_data)
            
            # 3. 生成执行报告
            execution_time = time.time() - start_time
            report = self._generate_report(results, execution_time)
            
            # 4. 将结果写回Excel文件
            try:
                self.logger.info("开始将结果写回Excel文件...")
                self.excel_processor.write_results_to_excel(excel_file, url_results)
                self.logger.info("结果写回Excel文件成功")
            except Exception as e:
                self.logger.error(f"写回Excel文件失败: {e}")
            
            # 5. 重命名已处理的Excel文件
            try:
                self.logger.info("开始重命名Excel文件...")
                new_excel_path = self.file_manager.rename_processed_file(excel_file)
                self.logger.info(f"Excel文件重命名成功: {new_excel_path}")
                report['renamed_excel_file'] = new_excel_path
            except Exception as e:
                self.logger.error(f"重命名Excel文件失败: {e}")
            
            self.logger.info(f"任务完成，总耗时: {execution_time:.2f}秒")
            return report
            
        except Exception as e:
            self.logger.error(f"执行失败: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def _run_pipeline(self, urls_data: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """执行处理流水线
        
        Args:
            urls_data: URL数据列表
            
        Returns:
            Tuple[Dict[str, Any], List[Dict[str, Any]]]: (处理结果, URL详细结果列表)
        """
        results = {
            'parsed_urls': 0,
            'downloaded_files': 0,
            'generated_pdfs': 0,
            'errors': [],
            'attachments': [],
            'pdf_files': []
        }
        
        # 用于收集每个URL的详细执行结果
        url_results = []
        
        try:
            # 阶段1: 并发解析网页提取附件
            self.logger.info("开始解析网页提取附件...")
            all_attachments = []
            
            for url_data in urls_data:
                url_result = {
                    'index': url_data.get('index', 0),
                    'url': url_data.get('url', ''),
                    'title': url_data.get('title', ''),
                    'success': False,
                    'attachments_count': 0,
                    'pdf_generated': False,
                    'pdf_error': None,
                    'error': None,
                    'completion_time': None
                }
                
                try:
                    url = url_data.get('url', '')
                    title = url_data.get('title', '')
                    
                    if not url:
                        url_result['error'] = '无效的URL'
                        url_results.append(url_result)
                        continue
                    
                    # 解析网页提取附件
                    attachments = self.web_parser.parse_page(url, title)
                    all_attachments.extend(attachments)
                    results['parsed_urls'] += 1
                    
                    url_result['success'] = True
                    url_result['attachments_count'] = len(attachments)
                    
                    self.logger.info(f"解析完成: {title} - 找到 {len(attachments)} 个附件")
                    
                except Exception as e:
                    error_msg = f"解析失败 {url_data.get('url', '')}: {e}"
                    self.logger.error(error_msg)
                    results['errors'].append(error_msg)
                    url_result['error'] = str(e)
                
                url_results.append(url_result)
            
            # 阶段2: 并发下载附件
            if all_attachments:
                self.logger.info(f"开始下载 {len(all_attachments)} 个附件...")
                downloaded_files = self.downloader.download_files(all_attachments)
                results['downloaded_files'] = len(downloaded_files)
                results['attachments'] = downloaded_files
                self.logger.info(f"附件下载完成: {len(downloaded_files)} 个文件")
            
            # 阶段3: 生成PDF文件（如果需要）
            if self.config.output_format == 'pdf':
                self.logger.info("开始生成PDF文件...")
                
                for i, url_data in enumerate(urls_data):
                    url = url_data.get('url', '')
                    title = url_data.get('title', '')
                    
                    if not url or i >= len(url_results):
                        continue
                    
                    try:
                        self.logger.debug(f"开始处理PDF: {title}, URL: {url}")
                        
                        # 获取网页内容
                        response = self.session.get(url, timeout=self.config.timeout)
                        response.raise_for_status()
                        
                        self.logger.debug(f"网页获取成功: {title}, 状态码: {response.status_code}")
                        
                        # 使用智能解码确保中文正确显示
                        html_content = self.smart_decode_response(response)
                        
                        self.logger.debug(f"内容解码成功: {title}, 内容长度: {len(html_content)}")
                        
                        # 生成PDF
                        pdf_path = pdf_generator.html_to_pdf_with_title(
                            html_content, title, self.config.pdfs_dir
                        )
                        
                        if pdf_path:
                            results['pdf_files'].append(pdf_path)
                            results['generated_pdfs'] += 1
                            url_results[i]['pdf_generated'] = True
                            self.logger.info(f"PDF生成成功: {title}")
                        else:
                            url_results[i]['pdf_error'] = 'PDF生成返回空路径'
                            self.logger.warning(f"PDF生成返回空路径: {title}")
                        
                    except Exception as e:
                        error_msg = f"PDF生成失败 {title}: {e}"
                        self.logger.error(error_msg)
                        results['errors'].append(error_msg)
                        url_results[i]['pdf_error'] = str(e)
                
                self.logger.info(f"PDF生成完成: {results['generated_pdfs']} 个文件")
            
            # 为所有URL结果添加完成时间
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for url_result in url_results:
                url_result['completion_time'] = completion_time
            
            return results, url_results
            
        except Exception as e:
            self.logger.error(f"流水线执行失败: {e}")
            raise
    
    def _generate_report(self, results: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
        """生成执行报告
        
        Args:
            results: 执行结果
            execution_time: 执行时间
            
        Returns:
            Dict[str, Any]: 执行报告
        """
        report = {
            'execution_time': execution_time,
            'parsed_urls': results['parsed_urls'],
            'downloaded_files': results['downloaded_files'],
            'generated_pdfs': results['generated_pdfs'],
            'total_errors': len(results['errors']),
            'errors': results['errors'],
            'output_dir': str(self.config.output_dir),
            'attachments': results['attachments'],
            'pdf_files': results['pdf_files']
        }
        
        # 保存报告到文件
        report_file = self.config.output_dir / 'execution_report.json'
        try:
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.info(f"执行报告已保存: {report_file}")
        except Exception as e:
            self.logger.warning(f"保存执行报告失败: {e}")
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='SuperSpider - 智能网页爬虫工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python superspider.py                          # 处理input目录下所有Excel文件
  python superspider.py data.xlsx                # 处理指定Excel文件
  python superspider.py data.xlsx --pdf          # 生成PDF格式输出
  python superspider.py data.xlsx --concurrent 10 # 设置并发数为10
        """
    )
    
    parser.add_argument(
        'excel_file', 
        nargs='?',  # 使参数可选
        help='包含URL的Excel文件路径（可选，默认处理input目录下所有Excel文件）'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='downloads',
        help='输出目录（默认: downloads）'
    )
    parser.add_argument(
        '--concurrent', '-c',
        type=int,
        default=5,
        help='并发数（默认: 5）'
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=30,
        help='请求超时时间（秒，默认: 30）'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别（默认: INFO）'
    )
    parser.add_argument(
        '--pdf',
        action='store_true',
        help='生成PDF格式输出'
    )
    
    args = parser.parse_args()
    
    try:
        # 处理Excel文件参数
        excel_files = []
        
        if args.excel_file:
            # 用户指定了Excel文件
            if not os.path.exists(args.excel_file):
                print(f"错误: Excel文件不存在: {args.excel_file}")
                sys.exit(1)
            excel_files = [args.excel_file]
        else:
            # 自动扫描input目录下的Excel文件
            input_dir = Path('input')
            if not input_dir.exists():
                print("错误: input目录不存在，请创建input目录并放入Excel文件")
                sys.exit(1)
            
            # 查找所有Excel文件
            excel_files = list(input_dir.glob('*.xlsx')) + list(input_dir.glob('*.xls'))
            
            if not excel_files:
                print("错误: input目录下没有找到Excel文件")
                sys.exit(1)
            
            print(f"找到 {len(excel_files)} 个Excel文件:")
            for file in excel_files:
                print(f"  - {file}")
            print()
        
        # 过滤已执行的Excel文件
        original_count = len(excel_files)
        filtered_files = []
        ignored_files = []
        
        for excel_file in excel_files:
            file_name = Path(excel_file).name
            if '【已执行】' in file_name:
                ignored_files.append(excel_file)
            else:
                filtered_files.append(excel_file)
        
        excel_files = filtered_files
        
        # 输出过滤结果
        if ignored_files:
            print(f"\n自动忽略 {len(ignored_files)} 个已执行的Excel文件:")
            for file in ignored_files:
                print(f"  - {Path(file).name}")
            print()
        
        if not excel_files:
            if ignored_files:
                print("所有Excel文件都已执行完成，无需重复处理。")
            else:
                print("没有找到需要处理的Excel文件。")
            sys.exit(0)
        
        if len(excel_files) != original_count:
            print(f"实际需要处理 {len(excel_files)} 个Excel文件:")
            for file in excel_files:
                print(f"  - {Path(file).name}")
            print()
        
        # 处理每个Excel文件
        for excel_file in excel_files:
            print(f"\n{'='*60}")
            print(f"开始处理: {excel_file}")
            print(f"{'='*60}")
            
            # 为每个Excel文件创建独立的输出目录
            if len(excel_files) > 1:
                base_output_dir = Path(args.output_dir)
                file_name = Path(excel_file).stem
                output_dir = base_output_dir / file_name
            else:
                output_dir = None  # 让Config类自动创建时间命名的目录
            
            # 创建配置
            config = Config(
                excel_file=str(excel_file),
                output_dir=output_dir,
                concurrent_limit=args.concurrent,
                timeout=args.timeout,
                log_level=args.log_level,
                output_format='pdf'  # 默认生成PDF和附件
            )
            
            # 设置Excel文件信息，生成对应的zip文件名
            config.set_excel_info(str(excel_file))
            
            # 设置日志
            logger = Logger(config.log_level, config.log_dir)
            logger.info(f"SuperSpider启动 - 处理文件: {excel_file}")
            
            # 运行爬虫
            spider = SuperSpider(config)
            results = spider.run(str(excel_file))
            
            # 创建zip文件
            try:
                logger.info(f"开始创建zip文件: {config.zip_filename}")
                file_manager = FileManager(config)
                success = file_manager.create_zip_file(
                    config.temp_work_dir, 
                    config.zip_file_path
                )
                
                if success:
                    logger.info(f"zip文件创建成功: {config.zip_file_path}")
                    # 清理临时目录
                    file_manager.cleanup_temp_directory(config.temp_work_dir)
                    logger.info("临时目录清理完成")
                else:
                    logger.warning("zip文件创建失败")
                    
            except Exception as e:
                logger.error(f"创建zip文件时出错: {e}")
            
            # 输出结果
            print(f"\n处理完成: {excel_file}")
            print(f"解析URL数: {results['parsed_urls']}")
            print(f"下载文件数: {results['downloaded_files']}")
            if results['generated_pdfs'] > 0:
                print(f"生成PDF数: {results['generated_pdfs']}")
            print(f"错误数: {results['total_errors']}")
            print(f"执行时间: {results['execution_time']:.2f}秒")
            print(f"输出目录: {results['output_dir']}")
            print(f"zip文件: {config.zip_file_path}")
            
            if results['total_errors'] > 0:
                print("\n错误详情:")
                for error in results['errors'][:5]:  # 只显示前5个错误
                    print(f"  - {error}")
                if len(results['errors']) > 5:
                    print(f"  ... 还有 {len(results['errors']) - 5} 个错误")
        
        print(f"\n{'='*60}")
        print("所有文件处理完成！")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()