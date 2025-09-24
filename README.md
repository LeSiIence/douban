# 豆瓣读书爬虫

一个用于爬取豆瓣读书计算机与互联网分类热门书籍信息的Python工具。

## 功能特性

- 支持多页数据爬取
- 自动下载书籍封面图片
- 导出CSV格式数据文件
- 支持Selenium（不要使用request模式，因为豆瓣动态加载）


## 环境要求

```
Python 3.x
selenium
beautifulsoup4
requests
pandas
```

## 安装依赖

### 方式一：使用requirements.txt（推荐）

```bash
pip install -r requirements.txt
```

### 方式二：手动安装

```bash
pip install selenium beautifulsoup4 requests pandas
```

注意：使用Selenium模式需要安装Chrome浏览器和对应的ChromeDriver。

## 使用方法

### 基本用法

```bash
# 爬取2页数据
python douban.py --pages 2

# 开启调试模式
python douban.py --debug --pages 1

# 保存调试HTML文件
python douban.py --save-html --pages 1
```

### 参数说明

- `--pages`: 爬取页数（无此参数则要求输入页数）
- `--debug`: 开启调试模式，显示详细日志
- `--save-html`: 保存响应HTML到文件

## 输出文件

### CSV文件 (books.csv)

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

### 图片文件 (images/)

书籍封面图片，命名格式：`{排名}_{书名}.jpg`

## 配置选项

可在代码中修改以下配置：

```python
USE_SELENIUM = True        # 是否使用Selenium模式
DEBUG_MODE = False         # 调试模式
SAVE_HTML = False         # 是否保存HTML文件
```

## 注意事项


- 建议适当设置请求间隔避免频繁访问影响网站正常业务以及ip遭到风控
- 网络问题可能导致部分图片下载失败
- 数据仅供学习研究使用

## 许可证

本项目仅供学习和研究使用。