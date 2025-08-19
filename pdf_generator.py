#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF生成器模块 - 完全重写版本

该模块提供HTML到PDF的转换功能，专门优化了中文字符支持。

作者: SuperSpider
版本: 2.0.0
"""

import os
import sys
import logging
import platform
import unicodedata
import html
from pathlib import Path
from typing import Optional, Union, List, Dict, Tuple
from error_handler import PDFGenerationError

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.colors import black, blue, red
    from bs4 import BeautifulSoup
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    print(f"ReportLab导入失败: {e}")


class FontManager:
    """
    字体管理器 - 负责字体注册、验证和回退策略
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.registered_fonts = {}
        self.font_fallback_chain = []
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        return {
            'platform': platform.system(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'encoding': sys.getdefaultencoding()
        }
    
    def register_chinese_fonts(self) -> str:
        """
        注册中文字体，实现多级回退策略
        
        Returns:
            最佳可用字体名称
        """
        self.logger.info(f"开始注册中文字体，系统: {self.system_info['platform']}")
        
        # 第一级：尝试注册CID字体（最可靠）
        cid_font = self._register_cid_fonts()
        if cid_font:
            self.font_fallback_chain.append(cid_font)
            self.logger.info(f"成功注册CID字体: {cid_font}")
            return cid_font
        
        # 第二级：尝试注册系统TrueType字体
        system_font = self._register_system_fonts()
        if system_font:
            self.font_fallback_chain.append(system_font)
            self.logger.info(f"成功注册系统字体: {system_font}")
            return system_font
        
        # 第三级：尝试注册内置Unicode字体
        unicode_font = self._register_unicode_fonts()
        if unicode_font:
            self.font_fallback_chain.append(unicode_font)
            self.logger.info(f"成功注册Unicode字体: {unicode_font}")
            return unicode_font
        
        # 第四级：使用默认字体
        default_font = 'Helvetica'
        self.font_fallback_chain.append(default_font)
        self.logger.warning(f"使用默认字体: {default_font}，中文可能显示为方框")
        return default_font
    
    def _register_cid_fonts(self) -> Optional[str]:
        """注册CID字体"""
        cid_fonts = [
            'STSong-Light',
            'STSongStd-Light',
            'STKaiti',
            'STFangsong',
            'MSung-Light',
            'MSungStd-Light',
            'HeiseiKakuGo-W5',
            'HeiseiMin-W3'
        ]
        
        for font_name in cid_fonts:
            try:
                # 检查是否已注册
                if font_name in pdfmetrics.getRegisteredFontNames():
                    if self._validate_font(font_name):
                        self.registered_fonts[font_name] = 'cid'
                        return font_name
                
                # 尝试注册CID字体
                pdfmetrics.registerFont(UnicodeCIDFont(font_name))
                if self._validate_font(font_name):
                    self.registered_fonts[font_name] = 'cid'
                    self.logger.debug(f"CID字体注册成功: {font_name}")
                    return font_name
                    
            except Exception as e:
                self.logger.debug(f"CID字体注册失败 {font_name}: {e}")
                continue
        
        return None
    
    def _register_system_fonts(self) -> Optional[str]:
        """注册系统字体"""
        font_configs = self._get_system_font_paths()
        
        for font_name, font_path in font_configs.items():
            if os.path.exists(font_path):
                try:
                    # 检查是否已注册
                    if font_name in pdfmetrics.getRegisteredFontNames():
                        if self._validate_font(font_name):
                            self.registered_fonts[font_name] = font_path
                            return font_name
                    
                    # 注册TTF字体
                    if font_path.endswith('.ttc'):
                        # TTC文件需要指定子字体索引
                        for subfont_index in range(4):  # 尝试前4个子字体
                            try:
                                pdfmetrics.registerFont(TTFont(f"{font_name}_{subfont_index}", font_path, subfontIndex=subfont_index))
                                test_font_name = f"{font_name}_{subfont_index}"
                                if self._validate_font(test_font_name):
                                    self.registered_fonts[test_font_name] = font_path
                                    self.logger.debug(f"系统字体注册成功: {test_font_name} (索引: {subfont_index})")
                                    return test_font_name
                            except Exception:
                                continue
                    else:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        if self._validate_font(font_name):
                            self.registered_fonts[font_name] = font_path
                            self.logger.debug(f"系统字体注册成功: {font_name}")
                            return font_name
                            
                except Exception as e:
                    self.logger.debug(f"系统字体注册失败 {font_name} ({font_path}): {e}")
                    continue
        
        return None
    
    def _get_system_font_paths(self) -> Dict[str, str]:
        """获取系统字体路径"""
        system = self.system_info['platform']
        
        if system == "Darwin":  # macOS
            return {
                'PingFang': '/System/Library/Fonts/PingFang.ttc',
                'Hiragino': '/System/Library/Fonts/Hiragino Sans GB.ttc',
                'STHeiti': '/System/Library/Fonts/STHeiti Medium.ttc',
                'AppleGothic': '/System/Library/Fonts/AppleSDGothicNeo.ttc',
                'STSong': '/System/Library/Fonts/Songti.ttc'
            }
        elif system == "Windows":
            return {
                'SimSun': 'C:/Windows/Fonts/simsun.ttc',
                'SimHei': 'C:/Windows/Fonts/simhei.ttf',
                'YaHei': 'C:/Windows/Fonts/msyh.ttc',
                'KaiTi': 'C:/Windows/Fonts/simkai.ttf',
                'FangSong': 'C:/Windows/Fonts/simfang.ttf'
            }
        else:  # Linux
            return {
                'NotoSansCJK': '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                'WenQuanYi': '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                'DejaVu': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                'Liberation': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
            }
    
    def _register_unicode_fonts(self) -> Optional[str]:
        """注册Unicode字体"""
        unicode_fonts = [
            'STSong-Light',
            'STKaiti',
            'MSung-Light'
        ]
        
        for font_name in unicode_fonts:
            try:
                if font_name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(UnicodeCIDFont(font_name))
                
                if self._validate_font(font_name):
                    self.registered_fonts[font_name] = 'unicode'
                    self.logger.debug(f"Unicode字体注册成功: {font_name}")
                    return font_name
                    
            except Exception as e:
                self.logger.debug(f"Unicode字体注册失败 {font_name}: {e}")
                continue
        
        return None
    
    def _validate_font(self, font_name: str) -> bool:
        """验证字体是否可用"""
        try:
            # 检查字体是否在已注册字体列表中
            if font_name not in pdfmetrics.getRegisteredFontNames():
                return False
            
            # 尝试创建一个简单的测试段落
            from reportlab.platypus import Paragraph
            test_style = ParagraphStyle(
                'TestStyle',
                fontName=font_name,
                fontSize=10
            )
            
            # 测试中文字符
            test_text = "测试中文字符显示"
            test_para = Paragraph(test_text, test_style)
            
            # 如果能创建段落，说明字体可用
            return True
            
        except Exception as e:
            self.logger.debug(f"字体验证失败 {font_name}: {e}")
            return False
    
    def get_best_font(self) -> str:
        """获取最佳可用字体"""
        if self.font_fallback_chain:
            return self.font_fallback_chain[0]
        return 'Helvetica'
    
    def get_font_info(self) -> Dict:
        """获取字体信息"""
        return {
            'registered_fonts': self.registered_fonts,
            'fallback_chain': self.font_fallback_chain,
            'system_info': self.system_info,
            'available_fonts': pdfmetrics.getRegisteredFontNames()
        }


class TextProcessor:
    """
    文本处理器 - 负责HTML解析和文本清理
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def process_html_content(self, html_content: str) -> Dict[str, any]:
        """
        处理HTML内容，提取标题和正文
        
        Args:
            html_content: HTML内容字符串
            
        Returns:
            包含标题和内容段落的字典
        """
        try:
            # 预处理HTML内容
            processed_html = self._preprocess_html(html_content)
            
            # 解析HTML
            soup = BeautifulSoup(processed_html, 'html.parser')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 提取内容段落
            paragraphs = self._extract_paragraphs(soup)
            
            return {
                'title': title,
                'paragraphs': paragraphs,
                'raw_text_length': len(html_content),
                'processed_paragraphs': len(paragraphs)
            }
            
        except Exception as e:
            self.logger.error(f"HTML内容处理失败: {e}")
            return {
                'title': "文档标题",
                'paragraphs': ["内容处理失败"],
                'raw_text_length': 0,
                'processed_paragraphs': 0
            }
    
    def _preprocess_html(self, html_content: str) -> str:
        """预处理HTML内容"""
        try:
            # 确保是字符串类型
            if isinstance(html_content, bytes):
                html_content = html_content.decode('utf-8', errors='ignore')
            
            # HTML解码
            html_content = html.unescape(html_content)
            
            # Unicode规范化
            html_content = unicodedata.normalize('NFC', html_content)
            
            # 替换常见的问题字符
            replacements = {
                '\u00a0': ' ',  # 非断行空格
                '\u2028': '\n',  # 行分隔符
                '\u2029': '\n\n',  # 段落分隔符
                '\r\n': '\n',  # Windows换行符
                '\r': '\n',  # Mac换行符
                '\u200b': '',  # 零宽空格
                '\u200c': '',  # 零宽非连字符
                '\u200d': '',  # 零宽连字符
                '\ufeff': '',  # 字节顺序标记
            }
            
            for old, new in replacements.items():
                html_content = html_content.replace(old, new)
            
            return html_content
            
        except Exception as e:
            self.logger.warning(f"HTML预处理失败: {e}")
            return str(html_content)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        try:
            # 尝试多种方式提取标题
            title_candidates = [
                soup.find('title'),
                soup.find('h1'),
                soup.find('h2'),
                soup.find('meta', attrs={'property': 'og:title'}),
                soup.find('meta', attrs={'name': 'title'})
            ]
            
            for candidate in title_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        title_text = candidate.get('content', '')
                    else:
                        title_text = candidate.get_text(strip=True)
                    
                    if title_text and len(title_text.strip()) > 0:
                        return self._clean_text(title_text)
            
            return "文档标题"
            
        except Exception as e:
            self.logger.warning(f"标题提取失败: {e}")
            return "文档标题"
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """提取内容段落"""
        try:
            # 移除不需要的标签
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()
            
            paragraphs = []
            
            # 查找主要内容区域
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_=['content', 'main-content', 'post-content']) or
                soup.find('div', id=['content', 'main', 'post']) or
                soup.body or 
                soup
            )
            
            if main_content:
                # 提取段落和标题
                for element in main_content.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:  # 过滤太短的文本
                        cleaned_text = self._clean_text(text)
                        if cleaned_text:
                            paragraphs.append(cleaned_text)
                
                # 如果没有找到段落，提取所有文本
                if not paragraphs:
                    all_text = main_content.get_text(separator='\n', strip=True)
                    if all_text:
                        # 按行分割并清理
                        lines = all_text.split('\n')
                        current_paragraph = []
                        
                        for line in lines:
                            cleaned_line = self._clean_text(line)
                            if cleaned_line:
                                current_paragraph.append(cleaned_line)
                            elif current_paragraph:
                                # 空行表示段落结束
                                paragraph_text = ' '.join(current_paragraph)
                                if len(paragraph_text) > 10:
                                    paragraphs.append(paragraph_text)
                                current_paragraph = []
                        
                        # 添加最后一个段落
                        if current_paragraph:
                            paragraph_text = ' '.join(current_paragraph)
                            if len(paragraph_text) > 10:
                                paragraphs.append(paragraph_text)
            
            # 如果仍然没有内容，返回默认信息
            if not paragraphs:
                paragraphs = ["未能提取到有效内容"]
            
            return paragraphs[:50]  # 限制段落数量
            
        except Exception as e:
            self.logger.error(f"段落提取失败: {e}")
            return ["内容提取失败"]
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        try:
            # 确保是字符串
            text = str(text).strip()
            
            # 移除多余的空白字符
            text = ' '.join(text.split())
            
            # 过滤控制字符，但保留中文字符
            cleaned_chars = []
            for char in text:
                if (char.isprintable() or 
                    '\u4e00' <= char <= '\u9fff' or  # 中文字符
                    '\u3400' <= char <= '\u4dbf' or  # 中文扩展A
                    '\u20000' <= char <= '\u2a6df' or  # 中文扩展B
                    '\u3000' <= char <= '\u303f' or  # 中文标点
                    '\uff00' <= char <= '\uffef' or  # 全角字符
                    char in ' \n\t'):
                    cleaned_chars.append(char)
            
            text = ''.join(cleaned_chars)
            
            # 限制长度
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return text.strip()
            
        except Exception as e:
            self.logger.warning(f"文本清理失败: {e}")
            return str(text).strip() if text else ""


class PDFGenerator:
    """
    PDF生成器 - 重写版本，专门优化中文支持
    """
    
    def __init__(self, engine: str = 'reportlab'):
        """
        初始化PDF生成器
        
        Args:
            engine: PDF生成引擎，目前只支持'reportlab'
        """
        self.logger = self._setup_logger()
        self.engine = self._validate_engine(engine)
        
        # 初始化组件
        self.font_manager = FontManager(self.logger)
        self.text_processor = TextProcessor(self.logger)
        
        # 注册字体
        self.primary_font = self.font_manager.register_chinese_fonts()
        
        # 记录初始化信息
        self._log_initialization_info()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _validate_engine(self, engine: str) -> str:
        """验证PDF引擎"""
        if not REPORTLAB_AVAILABLE:
            raise PDFGenerationError("ReportLab未安装，请运行: pip install reportlab beautifulsoup4")
        
        if engine not in ['reportlab', 'auto']:
            raise PDFGenerationError(f"不支持的PDF引擎: {engine}，当前只支持reportlab")
        
        return 'reportlab'
    
    def _log_initialization_info(self):
        """记录初始化信息"""
        font_info = self.font_manager.get_font_info()
        self.logger.info(f"PDF生成器初始化完成")
        self.logger.info(f"使用引擎: {self.engine}")
        self.logger.info(f"主要字体: {self.primary_font}")
        self.logger.info(f"已注册字体数量: {len(font_info['registered_fonts'])}")
        self.logger.debug(f"字体回退链: {font_info['fallback_chain']}")
    
    def html_to_pdf(self, html_content: str, output_path: Union[str, Path], 
                   base_url: Optional[str] = None) -> bool:
        """
        将HTML内容转换为PDF文件
        
        Args:
            html_content: HTML内容字符串
            output_path: 输出PDF文件路径
            base_url: HTML中相对链接的基础URL（暂未使用）
            
        Returns:
            转换是否成功
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"开始生成PDF: {output_path}")
            
            # 处理HTML内容
            processed_content = self.text_processor.process_html_content(html_content)
            
            # 生成PDF
            success = self._generate_pdf(
                processed_content['title'],
                processed_content['paragraphs'],
                output_path
            )
            
            if success:
                self.logger.info(f"PDF生成成功: {output_path}")
                self.logger.info(f"处理了 {processed_content['processed_paragraphs']} 个段落")
            else:
                self.logger.error(f"PDF生成失败: {output_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"PDF生成过程出错: {e}")
            raise PDFGenerationError(f"PDF生成失败: {e}")
    
    def _generate_pdf(self, title: str, paragraphs: List[str], output_path: Path) -> bool:
        """
        生成PDF文件
        
        Args:
            title: 文档标题
            paragraphs: 段落列表
            output_path: 输出路径
            
        Returns:
            是否成功
        """
        try:
            # 创建PDF文档
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # 创建样式
            styles = self._create_styles()
            
            # 构建内容
            story = []
            
            # 添加标题
            if title:
                title_para = Paragraph(title, styles['title'])
                story.append(title_para)
                story.append(Spacer(1, 20))
            
            # 添加段落
            for paragraph_text in paragraphs:
                if paragraph_text.strip():
                    try:
                        para = Paragraph(paragraph_text, styles['normal'])
                        story.append(para)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        self.logger.warning(f"段落添加失败，使用回退方案: {e}")
                        # 使用回退样式
                        fallback_para = Paragraph(paragraph_text, styles['fallback'])
                        story.append(fallback_para)
                        story.append(Spacer(1, 12))
            
            # 如果没有内容，添加默认信息
            if len(story) <= 2:  # 只有标题和间距
                story.append(Paragraph("未能提取到有效内容", styles['normal']))
            
            # 构建PDF
            doc.build(story)
            
            return True
            
        except Exception as e:
            self.logger.error(f"PDF文档构建失败: {e}")
            return False
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """
        创建段落样式
        
        Returns:
            样式字典
        """
        base_styles = getSampleStyleSheet()
        
        # 主要字体样式
        title_style = ParagraphStyle(
            'ChineseTitle',
            parent=base_styles['Title'],
            fontName=self.primary_font,
            fontSize=18,
            leading=24,
            spaceAfter=16,
            alignment=TA_CENTER,
            textColor=black
        )
        
        normal_style = ParagraphStyle(
            'ChineseNormal',
            parent=base_styles['Normal'],
            fontName=self.primary_font,
            fontSize=11,
            leading=16,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=black
        )
        
        # 回退样式（使用默认字体）
        fallback_style = ParagraphStyle(
            'Fallback',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=16,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=black
        )
        
        return {
            'title': title_style,
            'normal': normal_style,
            'fallback': fallback_style
        }
    
    def html_to_pdf_with_title(self, html_content: str, title: str, output_dir: Union[str, Path], 
                              base_url: Optional[str] = None) -> Optional[str]:
        """
        将HTML内容转换为PDF文件，使用指定标题作为文件名
        
        Args:
            html_content: HTML内容字符串
            title: 用作文件名的标题
            output_dir: 输出目录
            base_url: HTML中相对链接的基础URL
            
        Returns:
            生成的PDF文件路径，失败时返回None
        """
        try:
            # 清理标题作为文件名
            safe_title = self._sanitize_filename(title)
            if not safe_title:
                safe_title = "untitled"
            
            # 生成PDF文件路径
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = output_dir / f"{safe_title}.pdf"
            
            # 如果文件已存在，添加序号
            counter = 1
            original_path = pdf_path
            while pdf_path.exists():
                pdf_path = original_path.parent / f"{safe_title}_{counter}.pdf"
                counter += 1
            
            # 转换为PDF
            if self.html_to_pdf(html_content, pdf_path, base_url):
                return str(pdf_path)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"PDF生成失败 ({title}): {e}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
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
    
    def html_file_to_pdf(self, html_file_path: Union[str, Path], 
                        output_path: Union[str, Path]) -> bool:
        """
        将HTML文件转换为PDF文件
        
        Args:
            html_file_path: HTML文件路径
            output_path: 输出PDF文件路径
            
        Returns:
            转换是否成功
        """
        html_file_path = Path(html_file_path)
        
        if not html_file_path.exists():
            raise PDFGenerationError(f"HTML文件不存在: {html_file_path}")
        
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 使用HTML文件的绝对路径目录作为基础URL
            base_url = f"file://{html_file_path.parent.absolute()}"
            
            return self.html_to_pdf(html_content, output_path, base_url)
            
        except Exception as e:
            self.logger.error(f"读取HTML文件失败: {e}")
            raise PDFGenerationError(f"读取HTML文件失败: {e}")
    
    def batch_convert(self, html_files: list, output_dir: Union[str, Path]) -> dict:
        """
        批量转换HTML文件为PDF
        
        Args:
            html_files: HTML文件路径列表
            output_dir: 输出目录
            
        Returns:
            转换结果字典，包含成功和失败的文件列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'success': [],
            'failed': []
        }
        
        for html_file in html_files:
            try:
                html_path = Path(html_file)
                pdf_name = html_path.stem + '.pdf'
                pdf_path = output_dir / pdf_name
                
                if self.html_file_to_pdf(html_path, pdf_path):
                    results['success'].append(str(html_path))
                    self.logger.info(f"转换成功: {html_path} -> {pdf_path}")
                else:
                    results['failed'].append(str(html_path))
                    
            except Exception as e:
                self.logger.error(f"转换失败 {html_file}: {e}")
                results['failed'].append(str(html_file))
        
        self.logger.info(f"批量转换完成: 成功 {len(results['success'])} 个，失败 {len(results['failed'])} 个")
        return results
    
    def get_debug_info(self) -> Dict:
        """
        获取调试信息
        
        Returns:
            包含字体、系统等信息的字典
        """
        return {
            'engine': self.engine,
            'primary_font': self.primary_font,
            'font_info': self.font_manager.get_font_info(),
            'reportlab_available': REPORTLAB_AVAILABLE
        }


def create_pdf_generator(engine: str = 'reportlab') -> PDFGenerator:
    """
    创建PDF生成器实例
    
    Args:
        engine: PDF生成引擎
        
    Returns:
        PDFGenerator实例
    """
    return PDFGenerator(engine=engine)


# 全局函数，保持向后兼容
def html_to_pdf_with_title(html_content: str, title: str, output_dir: Union[str, Path]) -> Optional[str]:
    """
    全局函数：将HTML内容转换为PDF文件
    
    Args:
        html_content: HTML内容字符串
        title: 用作文件名的标题
        output_dir: 输出目录
        
    Returns:
        生成的PDF文件路径，失败时返回None
    """
    try:
        generator = create_pdf_generator()
        return generator.html_to_pdf_with_title(html_content, title, output_dir)
    except Exception as e:
        print(f"PDF生成失败: {e}")
        return None