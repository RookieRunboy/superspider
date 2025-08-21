# SuperSpider 开发规范文档

## 📋 目录
1. [代码规范](#代码规范)
2. [开发流程](#开发流程)
3. [测试规范](#测试规范)
4. [文档规范](#文档规范)
5. [版本管理](#版本管理)
6. [部署规范](#部署规范)

## 🎯 代码规范

### 1.1 Python代码风格

#### 基本原则
- 严格遵循 **PEP 8** 代码风格指南
- 使用 **UTF-8** 编码，文件头部添加编码声明
- 每行代码不超过 **120** 个字符
- 使用 **4个空格** 进行缩进，不使用Tab

#### 命名规范
```python
# 类名：使用驼峰命名法
class SuperSpider:
    pass

class WebParser:
    pass

# 函数和变量：使用下划线命名法
def process_excel_file():
    pass

def download_attachment():
    pass

# 常量：使用大写字母和下划线
MAX_RETRY_TIMES = 3
DEFAULT_TIMEOUT = 30

# 私有方法：使用单下划线前缀
def _internal_method(self):
    pass

# 特殊方法：使用双下划线前缀
def __private_method(self):
    pass
```

#### 导入规范
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块说明文档
"""

# 标准库导入
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# 第三方库导入
import requests
import pandas as pd
from bs4 import BeautifulSoup

# 本地模块导入
from config import Config
from logger import Logger
from error_handler import ErrorHandler
```

### 1.2 注释和文档字符串

#### 模块文档
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块名称

该模块的详细描述，包括主要功能和用途。

作者: SuperSpider Team
版本: 1.0.0
创建时间: 2024-01-15
最后修改: 2024-01-15
"""
```

#### 类文档
```python
class ExcelProcessor:
    """Excel文件处理器
    
    该类负责读取和处理Excel文件中的URL数据，
    支持多种Excel格式和编码。
    
    Attributes:
        config (Config): 配置对象
        logger (Logger): 日志对象
    
    Example:
        >>> processor = ExcelProcessor(config)
        >>> data = processor.read_excel('urls.xlsx')
    """
```

#### 函数文档
```python
def read_excel(self, excel_file: str) -> List[Dict[str, Any]]:
    """读取Excel文件中的URL数据
    
    Args:
        excel_file (str): Excel文件路径
        
    Returns:
        List[Dict[str, Any]]: 包含URL和标题的字典列表
        
    Raises:
        FileError: 当文件不存在或格式错误时
        
    Example:
        >>> data = processor.read_excel('input/urls.xlsx')
        >>> print(len(data))  # 输出URL数量
    """
```

#### 行内注释
```python
# 检测网页编码，优先使用HTTP头信息
detected = chardet.detect(response.content)
if detected['confidence'] > 0.7:  # 置信度阈值
    try:
        return response.content.decode(detected['encoding'])
    except UnicodeDecodeError:
        pass  # 继续尝试其他编码方式
```

### 1.3 错误处理规范

#### 异常处理
```python
# 好的做法：具体的异常处理
try:
    response = requests.get(url, timeout=self.config.timeout)
    response.raise_for_status()
except requests.exceptions.Timeout:
    self.logger.error(f"请求超时: {url}")
    raise NetworkError(f"请求超时: {url}")
except requests.exceptions.ConnectionError:
    self.logger.error(f"连接错误: {url}")
    raise NetworkError(f"连接错误: {url}")
except requests.exceptions.HTTPError as e:
    self.logger.error(f"HTTP错误: {e}")
    raise NetworkError(f"HTTP错误: {e}")

# 避免的做法：过于宽泛的异常处理
try:
    # 一些操作
    pass
except Exception as e:  # 避免捕获所有异常
    pass
```

#### 自定义异常
```python
class SuperSpiderError(Exception):
    """SuperSpider基础异常类"""
    pass

class NetworkError(SuperSpiderError):
    """网络相关错误"""
    pass

class FileError(SuperSpiderError):
    """文件操作错误"""
    pass

class ParseError(SuperSpiderError):
    """解析错误"""
    pass
```

### 1.4 日志规范

```python
# 日志级别使用指南
self.logger.debug("详细的调试信息，仅在开发时使用")
self.logger.info("一般信息，记录程序正常运行状态")
self.logger.warning("警告信息，程序可以继续运行但需要注意")
self.logger.error("错误信息，程序遇到错误但可以恢复")
self.logger.critical("严重错误，程序无法继续运行")

# 日志消息格式
self.logger.info(f"开始处理Excel文件: {excel_file}")
self.logger.info(f"成功读取 {len(urls_data)} 个URL")
self.logger.warning(f"下载重试 {retry_count}/{max_retries}: {url}")
self.logger.error(f"文件下载失败: {url}, 错误: {str(e)}")
```

## 🔄 开发流程

### 2.1 分支管理策略

```
main (主分支)
├── develop (开发分支)
│   ├── feature/new-parser (功能分支)
│   ├── feature/pdf-optimization (功能分支)
│   └── bugfix/encoding-issue (修复分支)
└── release/v2.1.0 (发布分支)
```

#### 分支命名规范
- **功能分支**: `feature/功能描述`
- **修复分支**: `bugfix/问题描述`
- **发布分支**: `release/版本号`
- **热修复分支**: `hotfix/紧急修复描述`

### 2.2 提交规范

#### 提交消息格式
```
<类型>(<范围>): <描述>

<详细说明>

<相关问题>
```

#### 提交类型
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

#### 提交示例
```bash
# 新功能
git commit -m "feat(parser): 添加新的网站解析器支持

- 支持解析example.com网站
- 优化附件链接提取算法
- 添加相应的测试用例

Closes #123"

# 修复bug
git commit -m "fix(encoding): 修复中文编码检测问题

修复了在某些网站上中文字符显示乱码的问题

Fixes #456"

# 文档更新
git commit -m "docs: 更新API文档和使用示例"
```

### 2.3 代码审查流程

#### Pull Request 规范
1. **标题**: 简洁明了地描述变更内容
2. **描述**: 详细说明变更原因和实现方式
3. **测试**: 说明测试情况和结果
4. **截图**: 如有UI变更，提供截图

#### 审查检查清单
- [ ] 代码符合项目规范
- [ ] 功能实现正确
- [ ] 测试覆盖充分
- [ ] 文档更新完整
- [ ] 性能影响可接受
- [ ] 安全性考虑充分

## 🧪 测试规范

### 3.1 测试结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_excel_processor.py
│   ├── test_web_parser.py
│   └── test_downloader.py
├── integration/             # 集成测试
│   ├── test_full_pipeline.py
│   └── test_file_operations.py
├── fixtures/                # 测试数据
│   ├── sample.xlsx
│   └── test_html.html
└── conftest.py             # pytest配置
```

### 3.2 单元测试示例

```python
import pytest
from unittest.mock import Mock, patch
from excel_processor import ExcelProcessor
from config import Config

class TestExcelProcessor:
    """Excel处理器测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.config = Config()
        self.processor = ExcelProcessor(self.config)
    
    def test_read_excel_success(self):
        """测试成功读取Excel文件"""
        # 准备测试数据
        excel_file = 'tests/fixtures/sample.xlsx'
        
        # 执行测试
        result = self.processor.read_excel(excel_file)
        
        # 验证结果
        assert len(result) > 0
        assert 'url' in result[0]
        assert 'title' in result[0]
    
    def test_read_excel_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileError):
            self.processor.read_excel('nonexistent.xlsx')
    
    @patch('pandas.read_excel')
    def test_read_excel_with_mock(self, mock_read_excel):
        """使用Mock测试Excel读取"""
        # 设置Mock返回值
        mock_df = Mock()
        mock_df.iterrows.return_value = [
            (0, {'URL': 'https://example.com', '标题': '测试页面'})
        ]
        mock_read_excel.return_value = mock_df
        
        # 执行测试
        result = self.processor.read_excel('test.xlsx')
        
        # 验证结果
        assert len(result) == 1
        assert result[0]['url'] == 'https://example.com'
```

### 3.3 集成测试示例

```python
import pytest
from pathlib import Path
from superspider import SuperSpider
from config import Config

class TestFullPipeline:
    """完整流程集成测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.config = Config(
            output_dir=Path('tests/output'),
            concurrent_limit=2,
            timeout=10
        )
        self.spider = SuperSpider(self.config)
    
    def test_full_pipeline(self):
        """测试完整的处理流程"""
        # 准备测试数据
        excel_file = 'tests/fixtures/test_urls.xlsx'
        
        # 执行完整流程
        result = self.spider.run(excel_file)
        
        # 验证结果
        assert result['parsed_urls'] > 0
        assert 'errors' in result
        assert Path(self.config.output_dir).exists()
    
    def teardown_method(self):
        """测试后清理"""
        # 清理测试生成的文件
        import shutil
        if Path('tests/output').exists():
            shutil.rmtree('tests/output')
```

### 3.4 测试运行

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_excel_processor.py

# 运行特定测试方法
pytest tests/unit/test_excel_processor.py::TestExcelProcessor::test_read_excel_success

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行测试并显示详细输出
pytest -v -s
```

## 📚 文档规范

### 4.1 文档结构

```
docs/
├── README.md                # 项目概述
├── INSTALLATION.md          # 安装指南
├── USER_GUIDE.md           # 用户指南
├── API_REFERENCE.md        # API参考
├── DEVELOPMENT.md          # 开发指南
├── CHANGELOG.md            # 变更日志
└── CONTRIBUTING.md         # 贡献指南
```

### 4.2 README.md 规范

```markdown
# 项目名称

[![状态徽章](badge-url)](link)

简短的项目描述（1-2句话）

## 特性

- 特性1
- 特性2
- 特性3

## 快速开始

### 安装

```bash
安装命令
```

### 使用

```bash
使用示例
```

## 文档

- [用户指南](docs/USER_GUIDE.md)
- [API参考](docs/API_REFERENCE.md)
- [开发指南](docs/DEVELOPMENT.md)

## 贡献

请阅读 [贡献指南](CONTRIBUTING.md)

## 许可证

[MIT License](LICENSE)
```

### 4.3 API文档规范

```python
def process_url(url: str, options: Dict[str, Any] = None) -> ProcessResult:
    """处理单个URL
    
    该函数接收一个URL并根据指定选项进行处理，
    返回包含处理结果的对象。
    
    Args:
        url (str): 要处理的URL地址
        options (Dict[str, Any], optional): 处理选项
            - timeout (int): 超时时间，默认30秒
            - retry_times (int): 重试次数，默认3次
            - output_format (str): 输出格式，'pdf'或'html'
    
    Returns:
        ProcessResult: 处理结果对象
            - success (bool): 是否成功
            - content (str): 页面内容
            - attachments (List[str]): 附件链接列表
            - error (str): 错误信息（如果失败）
    
    Raises:
        ValueError: 当URL格式无效时
        NetworkError: 当网络请求失败时
        TimeoutError: 当请求超时时
    
    Example:
        >>> result = process_url('https://example.com')
        >>> if result.success:
        ...     print(f"找到 {len(result.attachments)} 个附件")
        ... else:
        ...     print(f"处理失败: {result.error}")
    
    Note:
        - URL必须包含协议（http://或https://）
        - 处理大文件时建议增加超时时间
        - 某些网站可能需要特殊的请求头
    
    See Also:
        - process_urls(): 批量处理URL
        - download_attachment(): 下载附件
    """
```

## 📦 版本管理

### 5.1 版本号规范

采用 **语义化版本控制** (Semantic Versioning):

```
主版本号.次版本号.修订号 (MAJOR.MINOR.PATCH)

例如: 2.1.3
```

- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 5.2 变更日志规范

```markdown
# 变更日志

## [2.1.0] - 2024-01-15

### 新增
- 添加新的网站解析器支持
- 支持自定义PDF样式
- 增加批量处理进度显示

### 修改
- 优化中文编码检测算法
- 改进错误处理机制
- 更新依赖包版本

### 修复
- 修复某些网站附件下载失败的问题
- 解决PDF生成时的字体问题
- 修复Excel文件读取的编码问题

### 移除
- 移除已废弃的旧版API

## [2.0.1] - 2024-01-10

### 修复
- 修复安装依赖问题
```

### 5.3 发布流程

```bash
# 1. 更新版本号
# 在 setup.py 或 __init__.py 中更新版本号

# 2. 更新变更日志
# 在 CHANGELOG.md 中添加新版本的变更内容

# 3. 提交变更
git add .
git commit -m "chore: 准备发布 v2.1.0"

# 4. 创建标签
git tag -a v2.1.0 -m "发布版本 2.1.0"

# 5. 推送到远程仓库
git push origin main
git push origin v2.1.0

# 6. 创建GitHub Release
# 在GitHub上创建新的Release，包含变更说明
```

## 🚀 部署规范

### 6.1 环境配置

#### 开发环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install
```

#### 生产环境
```bash
# 安装生产依赖
pip install -r requirements.txt

# 设置环境变量
export SUPERSPIDER_LOG_LEVEL=INFO
export SUPERSPIDER_OUTPUT_DIR=/var/superspider/output
```

### 6.2 配置管理

```python
# config/development.py
class DevelopmentConfig:
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CONCURRENT_LIMIT = 3
    TIMEOUT = 10

# config/production.py
class ProductionConfig:
    DEBUG = False
    LOG_LEVEL = 'INFO'
    CONCURRENT_LIMIT = 10
    TIMEOUT = 30
```

### 6.3 部署检查清单

- [ ] 代码通过所有测试
- [ ] 文档已更新
- [ ] 版本号已更新
- [ ] 变更日志已更新
- [ ] 依赖包版本已锁定
- [ ] 配置文件已检查
- [ ] 性能测试通过
- [ ] 安全扫描通过

---

**遵循这些开发规范将有助于保持代码质量，提高团队协作效率，确保项目的可维护性和可扩展性。**