# SuperSpider - 智能网页爬虫工具

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

SuperSpider 是一个功能强大的智能网页爬虫工具，专门设计用于批量处理URL、下载附件和生成PDF文档。该工具具备完善的中文编码支持，能够准确处理中文网页内容。

## ✨ 主要特性

- 🚀 **批量URL处理**: 从Excel文件读取URL列表，支持并发处理
- 📄 **智能PDF转换**: 将网页内容转换为高质量PDF文档
- 📎 **附件自动下载**: 自动识别并下载网页中的附件文件
- 🌏 **完美中文支持**: 优化的中文编码处理，确保中文内容正确显示
- ⚡ **高性能并发**: 支持多线程并发处理，提高处理效率
- 🔄 **断点续传**: 支持下载中断后的断点续传功能
- 📊 **详细日志**: 完整的执行日志和进度报告
- 🛡️ **错误处理**: 完善的错误处理和重试机制

## 🔧 技术特点

### 中文编码优化
- **智能编码检测**: 自动检测网页编码，支持多种中文编码格式
- **多级字体回退**: 实现完善的中文字体回退策略
- **UTF-8标准化**: 确保所有文本内容使用UTF-8编码处理

### PDF生成引擎
- **ReportLab优化**: 基于ReportLab的PDF生成，专门优化中文字符支持
- **字体管理系统**: 自动注册和管理中文字体，支持多平台
- **样式定制**: 支持自定义PDF样式和布局

### 网络处理
- **智能重试**: 网络请求失败时的智能重试机制
- **超时控制**: 可配置的请求超时时间
- **User-Agent轮换**: 支持多种User-Agent以避免反爬虫

## 📦 安装

### 环境要求
- Python 3.7+
- 操作系统: Windows, macOS, Linux

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/RookieRunboy/superspider.git
cd superspider

# 安装依赖
pip install -r requirements.txt
```

### 核心依赖包
- `requests`: HTTP请求处理
- `beautifulsoup4`: HTML解析
- `reportlab`: PDF生成
- `openpyxl`: Excel文件处理
- `pandas`: 数据处理
- `chardet`: 编码检测

## 🚀 快速开始

### 1. 准备Excel文件

在 `input/` 目录下放置包含URL的Excel文件，格式如下：

| URL | 标题 |
|-----|------|
| https://example.com/page1 | 页面1 |
| https://example.com/page2 | 页面2 |

### 2. 运行爬虫

```bash
# 处理input目录下的所有Excel文件
python superspider.py

# 处理指定的Excel文件
python superspider.py input/urls.xlsx

# 生成PDF格式输出（默认已启用）
python superspider.py input/urls.xlsx --pdf

# 设置并发数为10
python superspider.py input/urls.xlsx --concurrent 10

# 设置超时时间为60秒
python superspider.py input/urls.xlsx --timeout 60

# 设置日志级别为DEBUG
python superspider.py input/urls.xlsx --log-level DEBUG
```

### 3. 查看结果

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

## 📖 详细使用说明

### 命令行参数

```bash
python superspider.py [excel_file] [options]
```

**参数说明:**
- `excel_file`: Excel文件路径（可选，默认处理input目录下所有Excel文件）
- `--output-dir, -o`: 输出目录（默认: downloads）
- `--concurrent, -c`: 并发数（默认: 5）
- `--timeout, -t`: 请求超时时间（秒，默认: 30）
- `--log-level`: 日志级别（DEBUG, INFO, WARNING, ERROR，默认: INFO）
- `--pdf`: 生成PDF格式输出（默认启用）

### Excel文件格式

Excel文件应包含以下列：
- **URL**: 要处理的网页链接（必需）
- **标题**: 网页标题，用作文件名（可选）

### 配置选项

<<<<<<< HEAD
可以通过修改config.py中的配置来自定义行为：

```python
config = Config(
    concurrent_limit=5,         # 并发数
    timeout=30,                 # 超时时间（秒）
    log_level='INFO'           # 日志级别
)

# 其他可配置项
config.retry_times = 3              # 重试次数
config.retry_delay = 1              # 重试延迟
config.attachment_extensions = {    # 支持的附件格式
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
    '.ppt', '.pptx', '.zip', '.rar', '.7z',
    '.txt', '.csv', '.png', '.jpg', '.jpeg'
}
}
```

## 🔍 功能详解

### 1. 网页内容提取
- 自动提取网页标题和正文内容
- 智能识别主要内容区域
- 过滤广告和无关内容
- 保持文本格式和结构

### 2. 附件下载
- 自动识别PDF、DOC、XLS等附件链接
- 支持多种文件格式
- 断点续传功能
- 文件完整性验证

### 3. PDF生成
- 高质量PDF输出
- 中文字符完美支持
- 自定义页面布局
- 书签和目录生成

### 4. 错误处理
- 网络错误自动重试
- 编码错误智能修复
- 详细错误日志记录
- 优雅的错误恢复

## 🛠️ 高级配置

### 自定义字体

如果需要使用特定的中文字体，可以修改 `pdf_generator.py` 中的字体配置：

```python
# 添加自定义字体路径
custom_fonts = {
    'MyFont': '/path/to/your/font.ttf'
}
```

### 代理设置

如果需要使用代理，可以在 `superspider.py` 中配置：

```python
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}
```

### 请求头自定义

```python
custom_headers = {
    'User-Agent': 'Your Custom User Agent',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}
```

## 📊 性能优化

### 并发处理
- 默认并发数为5，可通过--concurrent参数调整
- 建议并发数不超过10，避免对目标服务器造成压力
- 使用ThreadPoolExecutor实现多线程并发下载

### 内存管理
- 大文件分块处理，避免内存溢出
- 及时释放不需要的资源
- 支持流式处理大型网页

### 网络优化
- 连接池复用，减少连接开销
- 智能重试机制，提高成功率
- 请求间隔控制，避免被封禁

## 🐛 故障排除

### 常见问题

**1. 中文显示乱码**
- 确保系统已安装中文字体
- 检查网页编码是否正确检测
- 尝试手动指定编码格式

**2. PDF生成失败**
- 检查ReportLab是否正确安装
- 确认字体文件路径正确
- 查看详细错误日志

**3. 网络连接超时**
- 增加超时时间设置
- 检查网络连接状态
- 尝试使用代理服务器

**4. Excel文件读取失败**
- 确认文件格式为.xlsx或.xls
- 检查文件是否被其他程序占用
- 验证文件内容格式正确

### 调试模式

启用详细日志输出：

```bash
python superspider.py --log-level DEBUG
```

## 📝 更新日志

<<<<<<< HEAD
### v2.0.0 (当前版本)
- ✨ 完全重写PDF生成引擎，优化中文支持
- 🔧 实现智能编码检测和处理
- 🚀 添加多级字体回退策略
- 📊 改进错误处理和日志系统
- 🌏 完善中文字符显示效果
- 📦 新增ZIP打包功能
- 🏗️ 模块化架构重构
- 📝 完善的执行报告生成

### v1.0.0 (初始版本)
- 🎉 初始版本发布
- 📄 基础PDF生成功能
- 📎 附件下载功能
- 🔄 并发处理支持

## 🤝 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目！

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/RookieRunboy/superspider.git
cd superspider

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov  # 测试工具
```

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试
- 提交前运行测试套件

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [ReportLab](https://www.reportlab.com/) - PDF生成库
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析库
- [Requests](https://requests.readthedocs.io/) - HTTP库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [提交Issue](https://github.com/RookieRunboy/superspider/issues)
- 项目主页: [SuperSpider](https://github.com/RookieRunboy/superspider)

---

**SuperSpider** - 让网页爬取变得简单高效！ 🕷️✨
