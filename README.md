# 豆瓣读书爬虫与数据分析

一个用于爬取豆瓣读书计算机与互联网分类热门书籍信息的Python工具，包含完整的数据分析和可视化功能。

## 功能特性

### 数据爬取功能
- 支持多页数据爬取
- 自动下载书籍封面图片
- 导出CSV格式数据文件
- 支持Selenium（不要使用request模式，因为豆瓣动态加载）

### 数据分析功能
- 图书分类统计与可视化
- 价格分布分析
- 字数统计分析
- 热度排名分析
- 折扣率分析
- 价格与字数关系分析
- 自动生成分析报告

## 环境要求

```
Python 3.x
selenium
beautifulsoup4
requests
pandas
numpy
matplotlib
seaborn
```

## 安装依赖

### 方式一：使用requirements.txt（推荐）

```bash
pip install -r requirements.txt
```

### 方式二：手动安装

```bash
# 爬虫依赖
pip install selenium beautifulsoup4 requests pandas

# 分析和可视化依赖
pip install numpy matplotlib seaborn
```

注意：使用Selenium模式需要安装Chrome浏览器和对应的ChromeDriver。

## 使用方法

### 数据爬取

```bash
# 爬取2页数据
python douban.py --pages 2

# 开启调试模式
python douban.py --debug --pages 1

# 保存调试HTML文件
python douban.py --save-html --pages 1
```

### 数据分析

```bash
# 运行完整数据分析
python book_analysis.py
```

### 参数说明

#### 爬虫参数 (douban.py)
- `--pages`: 爬取页数（无此参数则要求输入页数）
- `--debug`: 开启调试模式，显示详细日志
- `--save-html`: 保存响应HTML到文件

## 输出文件

### 爬虫输出

#### CSV文件 (books.csv)
包含以下字段：
- 热度排名
- 书名
- 作者
- 简介
- 分类
- 字数
- 原价
- 现价
- 封面图片

#### 图片文件 (images/)
书籍封面图片，命名格式：`{排名}_{书名}.jpg`

### 分析输出

#### 可视化图表
- `图书分类统计.png`: 包含条形图、饼图、水平条形图和分布直方图
- `图书指标分析.png`: 包含价格分布、字数分布、热度排名、价格字数关系、折扣率分布和最贵图书排行

#### 分析报告
- `豆瓣图书分析报告.txt`: 详细的统计分析报告

## 分析功能详解

### 图书分类分析
- 统计各分类图书数量
- 支持多分类图书处理（+号分隔）
- 生成Top N分类排行
- 分类占比分析

### 价格指标分析
- 原价和现价统计
- 价格分布分析
- 折扣率计算
- 优惠金额统计

### 内容指标分析
- 图书字数统计
- 字数分布可视化
- 价格与字数相关性分析

### 热度分析
- 热度排名分布
- Top图书识别
- 排名区间统计

## 配置选项

### 爬虫配置 (douban.py)
```python
USE_SELENIUM = True        # 是否使用Selenium模式
DEBUG_MODE = False         # 调试模式
SAVE_HTML = False         # 是否保存HTML文件
```

### 分析配置 (book_analysis.py)
```python
# 可在BookDataAnalyzer类中自定义
top_n = 15                 # 分类排行显示数量
csv_file = 'books.csv'     # 数据源文件
```

## 使用示例

### 完整工作流程

1. **爬取数据**
```bash
python douban.py --pages 5
```

2. **分析数据**
```bash
python book_analysis.py
```

3. **查看结果**
   - 检查生成的PNG图表文件
   - 阅读TXT分析报告
   - 查看CSV原始数据

### 自定义分析

```python
from book_analysis import BookDataAnalyzer

# 创建分析器
analyzer = BookDataAnalyzer('books.csv')

# 运行特定分析
analyzer.clean_data()
analyzer.analyze_categories()
analyzer.visualize_categories(top_n=20)
```

## 注意事项

- 建议适当设置请求间隔避免频繁访问影响网站正常业务以及ip遭到风控
- 网络问题可能导致部分图片下载失败
- 数据仅供学习研究使用
- 分析功能需要先运行爬虫生成books.csv文件
- 可视化图表支持中文显示，如遇字体问题请安装相应中文字体

## 许可证

本项目仅供学习和研究使用。