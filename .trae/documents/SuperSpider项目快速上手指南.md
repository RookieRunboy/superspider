# SuperSpider 项目快速上手指南

## 📋 项目概述

SuperSpider 是一个功能强大的智能网页爬虫工具，专门设计用于批量处理URL、下载附件和生成PDF文档。该工具具备完善的中文编码支持，能够准确处理中文网页内容。

### 🎯 主要功能
- **批量URL处理**: 从Excel文件读取URL列表，支持并发处理
- **智能PDF转换**: 将网页内容转换为高质量PDF文档
- **附件自动下载**: 自动识别并下载网页中的附件文件
- **完美中文支持**: 优化的中文编码处理，确保中文内容正确显示
- **高性能并发**: 支持多线程并发处理，提高处理效率
- **断点续传**: 支持下载中断后的断点续传功能
- **详细日志**: 完整的执行日志和进度报告
- **错误处理**: 完善的错误处理和重试机制

### 🏗️ 技术特点
- **智能编码检测**: 自动检测网页编码，支持多种中文编码格式
- **ReportLab PDF引擎**: 基于ReportLab的PDF生成，专门优化中文字符支持
- **智能重试机制**: 网络请求失败时的智能重试机制
- **模块化设计**: 清晰的模块分离，便于维护和扩展

## 🚀 快速开始

### 1. 环境要求
- Python 3.7+
- 操作系统: Windows, macOS, Linux

### 2. 安装步骤

```bash
# 1. 克隆项目（如果从Git获取）
git clone <repository-url>
cd superspider-main

# 2. 安装依赖
pip install -r requirements.txt
```

### 3. 准备数据

在 `input/` 目录下放置包含URL的Excel文件，格式要求：

| URL | 标题 |
|-----|------|
| https://example.com/page1 | 页面1 |
| https://example.com/page2 | 页面2 |

**注意事项：**
- URL列可以命名为：`url`, `URL`, `link`, `链接`, `网址` 等
- 标题列可以命名为：`title`, `标题`, `名称` 等
- 如果没有标题列，系统会自动生成

### 4. 运行程序

```bash
# 处理input目录下的所有Excel文件
python superspider.py

# 处理指定的Excel文件
python superspider.py input/urls.xlsx

# 设置并发数为10
python superspider.py input/urls.xlsx --concurrent 10

# 设置超时时间为60秒
python superspider.py input/urls.xlsx --timeout 60

# 设置日志级别为DEBUG
python superspider.py input/urls.xlsx --log-level DEBUG
```

### 5. 查看结果

处理完成后，结果将保存在 `downloads/` 目录下：

```
downloads/
├── 20250819_1430/          # 时间戳目录
│   ├── temp_work/          # 临时工作目录
│   │   ├── attachments/    # 下载的附件
│   │   └── pdfs/          # 生成的PDF文件
│   ├── data.zip           # 打包的结果文件
│   ├── execution_report.json # 执行报告
│   └── superspider.log    # 执行日志
```

## 📁 项目结构

```
superspider-main/
├── superspider.py          # 主程序入口
├── config.py              # 配置管理
├── logger.py              # 日志模块
├── excel_processor.py     # Excel文件处理
├── web_parser.py          # 网页解析
├── downloader.py          # 文件下载
├── file_manager.py        # 文件管理
├── pdf_generator.py       # PDF生成
├── error_handler.py       # 错误处理
├── requirements.txt       # 依赖包列表
├── README.md             # 项目说明
├── DEPLOYMENT_GUIDE.md   # 部署指南
├── input/                # 输入文件目录
├── downloads/            # 输出文件目录
└── .trae/               # 项目文档目录
    └── documents/
```

### 核心模块说明

| 模块 | 功能 | 主要类/函数 |
|------|------|-------------|
| `superspider.py` | 主程序，协调各模块工作 | `SuperSpider` 类 |
| `config.py` | 配置管理，包含所有可配置参数 | `Config` 类 |
| `excel_processor.py` | Excel文件读写处理 | `ExcelProcessor` 类 |
| `web_parser.py` | 网页内容解析和附件提取 | `WebParser` 类 |
| `downloader.py` | 文件下载和并发控制 | `Downloader` 类 |
| `pdf_generator.py` | PDF文档生成 | PDF生成相关函数 |
| `file_manager.py` | 文件管理和打包 | `FileManager` 类 |
| `error_handler.py` | 错误处理和重试机制 | `ErrorHandler` 类 |
| `logger.py` | 日志记录和管理 | `Logger` 类 |

## ⚙️ 配置说明

### 主要配置参数

在 `config.py` 中可以调整以下参数：

```python
class Config:
    def __init__(self, 
                 concurrent_limit=5,    # 并发数限制
                 timeout=15,           # 请求超时时间（秒）
                 log_level='INFO',     # 日志级别
                 output_format='pdf'): # 输出格式
```

### 可配置项详解

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `concurrent_limit` | 5 | 并发处理的URL数量 |
| `timeout` | 15 | HTTP请求超时时间（秒） |
| `log_level` | 'INFO' | 日志级别：DEBUG, INFO, WARNING, ERROR |
| `retry_times` | 1 | 失败重试次数 |
| `retry_delay` | 1 | 重试间隔时间（秒） |

### 支持的附件格式

```python
attachment_extensions = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
    '.ppt', '.pptx', '.zip', '.rar', '.7z',
    '.tar', '.gz', '.txt', '.csv'
}
```

## 🔧 开发指南

### 代码规范

1. **编码规范**
   - 使用UTF-8编码
   - 遵循PEP 8代码风格
   - 类名使用驼峰命名法
   - 函数和变量使用下划线命名法

2. **注释规范**
   - 每个模块开头包含模块说明
   - 每个类和函数包含docstring
   - 复杂逻辑添加行内注释

3. **错误处理**
   - 使用try-except捕获异常
   - 记录详细的错误日志
   - 提供有意义的错误信息

### 添加新功能

1. **添加新的解析器**
   ```python
   # 在web_parser.py中添加新的解析方法
   def parse_custom_site(self, soup, url):
       # 自定义解析逻辑
       pass
   ```

2. **添加新的文件格式支持**
   ```python
   # 在config.py中添加新的文件扩展名
   self.attachment_extensions.add('.new_format')
   ```

3. **自定义PDF样式**
   ```python
   # 在pdf_generator.py中修改样式配置
   def customize_pdf_style():
       # 自定义样式逻辑
       pass
   ```

### 调试技巧

1. **启用DEBUG日志**
   ```bash
   python superspider.py --log-level DEBUG
   ```

2. **单独测试模块**
   ```python
   # 测试Excel处理
   from excel_processor import ExcelProcessor
   processor = ExcelProcessor(config)
   data = processor.read_excel('test.xlsx')
   ```

3. **检查网络请求**
   ```python
   # 在web_parser.py中添加调试信息
   print(f"请求URL: {url}")
   print(f"响应状态: {response.status_code}")
   ```

## 🐛 常见问题解答

### Q1: Excel文件读取失败
**A:** 检查以下几点：
- Excel文件是否存在
- 文件是否被其他程序占用
- URL列是否正确命名
- 文件格式是否为.xlsx或.xls

### Q2: 中文字符显示乱码
**A:** 项目已优化中文支持，如仍有问题：
- 确保系统安装了中文字体
- 检查网页原始编码
- 查看日志中的编码检测信息

### Q3: 下载速度慢
**A:** 可以调整以下参数：
- 增加并发数：`--concurrent 10`
- 调整超时时间：`--timeout 30`
- 检查网络连接状况

### Q4: PDF生成失败
**A:** 检查以下几点：
- 确保安装了reportlab包
- 检查系统字体配置
- 查看错误日志详细信息

### Q5: 内存占用过高
**A:** 优化建议：
- 减少并发数
- 分批处理大量URL
- 定期清理临时文件

## 📞 技术支持

### 日志分析
- 执行日志位于：`downloads/时间戳/superspider.log`
- 执行报告位于：`downloads/时间戳/execution_report.json`

### 性能监控
- 监控并发数和内存使用
- 关注网络请求成功率
- 检查文件下载完整性

### 故障排除
1. 查看最新的日志文件
2. 检查网络连接状态
3. 验证输入文件格式
4. 确认系统资源充足

---

**祝您使用愉快！如有问题，请查看日志文件或联系开发团队。**