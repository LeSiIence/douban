import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import os
import argparse

# 尝试导入Selenium，如果不可用则使用备用方案
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# --- 配置 ---
# 目标网址（使用热度排序）
BASE_URL = "https://read.douban.com/category/105?sort=hot"
# 自定义请求头，模拟浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
# 图片存储目录
IMAGE_DIR = 'images'
# CSV文件路径
CSV_FILE = 'books.csv'
# 爬取页数
MAX_PAGES = 3  # 默认爬取3页

# --- 调试配置 ---
DEBUG_MODE = True  # 设置为False可关闭所有调试输出
SAVE_HTML = True   # 是否保存原始HTML文件用于调试
USE_SELENIUM = SELENIUM_AVAILABLE  # 如果Selenium可用则默认使用

# --- 调试工具函数 ---
def debug_print(message, level="INFO"):
    """
    调试输出函数
    level: INFO, ERROR, SUCCESS
    """
    if DEBUG_MODE:
        prefix_map = {
            "INFO": "[调试]",
            "ERROR": "[错误]", 
            "SUCCESS": "[成功]",
            "CONFIG": "[配置]",
            "MAIN": "[主程序]"
        }
        prefix = prefix_map.get(level, "[调试]")
        print(f"{prefix} {message}")

def create_selenium_driver():
    """
    创建Selenium WebDriver
    """
    if not SELENIUM_AVAILABLE:
        return None
    
    try:
        options = Options()
        options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 尝试创建WebDriver
        driver = webdriver.Chrome(options=options)
        debug_print("成功创建Selenium WebDriver", "SUCCESS")
        return driver
    except Exception as e:
        debug_print(f"创建Selenium WebDriver失败: {e}", "ERROR")
        debug_print("将回退到普通requests方案", "INFO")
        return None

def fetch_page_with_selenium(driver, url):
    """
    使用Selenium获取页面内容
    """
    try:
        debug_print(f"使用Selenium加载页面: {url}")
        driver.get(url)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "works-list")))
        
        # 等待一下确保动态内容加载完成
        time.sleep(2)
        
        # 尝试滚动页面，触发懒加载
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # 获取页面源码
        html_content = driver.page_source
        debug_print(f"通过Selenium获取到页面内容，长度: {len(html_content)}", "SUCCESS")
        return html_content
        
    except TimeoutException:
        debug_print("页面加载超时", "ERROR")
        return None
    except Exception as e:
        debug_print(f"Selenium获取页面失败: {e}", "ERROR")
        return None

# --- 初始化 ---
# 创建图片存储目录
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 打开CSV文件并写入表头（使用UTF-8 BOM编码，确保Office正确显示中文）
with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['热度排名', '书名', '作者', '简介', '分类', '字数', '价格'])

# --- 爬虫核心逻辑 ---

def init_webdriver():
    """初始化Chrome WebDriver"""
    if not SELENIUM_AVAILABLE:
        debug_print("❌ Selenium不可用，无法初始化WebDriver", "ERROR")
        return None
    
    try:
        debug_print("正在初始化Chrome WebDriver...")
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无界面模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 自动下载和配置ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # 创建WebDriver实例
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        debug_print("✅ Chrome WebDriver初始化成功")
        return driver
        
    except Exception as e:
        debug_print(f"❌ 初始化WebDriver失败: {e}", "ERROR")
        return None

def fetch_book_data_selenium(url, driver, page_num=1):
    """
    使用Selenium获取书籍数据（处理JavaScript动态加载）
    """
    debug_print(f"开始请求第{page_num}页URL: {url}")
    debug_print("使用Selenium模式获取页面")
    
    try:
        # 使用Selenium获取页面
        driver.get(url)
        
        # 等待页面加载完成 - 先等待works-list容器
        wait = WebDriverWait(driver, 10)
        works_list = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.works-list"))
        )
        
        # 等待实际的书籍数据加载（而非loading skeleton）
        debug_print("等待实际书籍数据加载...")
        try:
            # 等待至少有一个带有data-works-id属性的书籍项目出现
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-works-id]"))
            )
            # 额外等待确保所有数据都加载完成
            time.sleep(3)
            debug_print("检测到实际书籍数据已加载")
        except TimeoutException:
            debug_print("未检测到实际书籍数据，可能页面仍在加载中...")
            # 给予更多时间
            time.sleep(5)
        
        debug_print("页面加载完成，开始解析...")
        
        # 获取页面源码
        html_content = driver.page_source
        
        # 保存HTML文件用于调试
        if SAVE_HTML:
            filename = f"debug_response_selenium_page{page_num}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            debug_print(f"已保存原始HTML到 {filename}")
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        page_title = soup.title.string if soup.title else "无标题"
        debug_print(f"页面标题: {page_title}")
        
        # 查找书籍列表 - 优先查找React根节点下的动态加载内容
        debug_print("尝试查找豆瓣页面中的书籍列表...")
        
        # 先尝试找React渲染的动态内容
        react_root = soup.find('div', id='react-root')
        if react_root:
            works_list = react_root.find('ul', class_='works-list')
            if works_list:
                debug_print("✅ 找到React动态加载的works-list容器")
            else:
                debug_print("⚠️  React根节点存在但未找到works-list")
                works_list = None
        else:
            debug_print("⚠️  未找到React根节点")
            works_list = None
        
        # 如果动态内容没找到，尝试静态内容
        if not works_list:
            works_list = soup.find('ul', class_='works-list')
            if works_list:
                debug_print("✅ 找到静态works-list容器")
            else:
                debug_print("❌ 未找到任何works-list容器")
                return []
        
        # 获取所有实际的书籍项目（有data-works-id的，排除loading skeleton）
        book_items = works_list.find_all('li', {'data-works-id': True})
        debug_print(f"在works-list中找到 {len(book_items)} 个实际书籍li元素")
        
        # 如果没有找到实际书籍，检查loading状态
        if not book_items:
            loading_items = works_list.find_all('li', class_='works-item is-loading')
            debug_print(f"发现 {len(loading_items)} 个loading项目，数据可能还在加载中")
            all_li_items = works_list.find_all('li')
            debug_print(f"总共有 {len(all_li_items)} 个li元素")
            return []
        
        books_data = []
        
        for i, book in enumerate(book_items):
            debug_print(f"处理第 {i+1} 本书...")
            try:
                # 基于豆瓣实际HTML结构提取信息
                # 提取标题
                title_elem = book.find('h4', class_='title')
                if title_elem:
                    title_link = title_elem.find('a')
                    if title_link:
                        title_span = title_link.find('span', class_='title-text')
                        if title_span:
                            title = title_span.get_text(strip=True)
                        else:
                            title = title_link.get_text(strip=True)
                    else:
                        title = title_elem.get_text(strip=True)
                    debug_print(f"书名: {title}")
                else:
                    debug_print(f"第 {i+1} 本书缺少标题信息")
                    continue
                
                # 提取作者信息
                author_elem = book.find('div', class_='author')
                if author_elem:
                    author_links = author_elem.find_all('a', class_='author-link')
                    if author_links:
                        authors = [link.get_text(strip=True) for link in author_links]
                        author = ' / '.join(authors)
                    else:
                        author = author_elem.get_text(strip=True)
                    debug_print(f"作者: {author}")
                else:
                    author = "未知作者"
                    debug_print(f"第 {i+1} 本书缺少作者信息")
                
                # 提取简介信息
                intro_elem = book.find('a', class_='intro')
                if intro_elem:
                    intro = intro_elem.get_text(strip=True)
                    if len(intro) > 200:
                        intro = intro[:200] + "..."
                    debug_print(f"简介长度: {len(intro)} 字符")
                else:
                    intro = "无简介信息"
                    debug_print(f"第 {i+1} 本书缺少简介信息")
                
                # 提取字数信息
                word_count = "未知"
                extra_info = book.find('div', class_='extra-info')
                if extra_info:
                    spans = extra_info.find_all('span')
                    for span in spans:
                        text = span.get_text(strip=True)
                        if '万字' in text:
                            word_count = text
                            break
                
                # 提取价格信息
                price = "未知"
                price_elem = book.find('span', class_='price-tag')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = price_text if price_text else "未知"
                
                # 计算热度排名
                ranking = (page_num - 1) * 10 + (i + 1)
                
                # 组装数据
                data_row = {
                    '热度排名': ranking,
                    '书名': title,
                    '作者': author,
                    '简介': intro,
                    '字数': word_count,
                    '价格': price
                }
                books_data.append(data_row)
                debug_print(f"成功提取第 {i+1} 本书的信息", "SUCCESS")
                
            except Exception as e:
                debug_print(f"处理第 {i+1} 本书时出错: {e}", "ERROR")
        
        debug_print(f"成功提取 {len(books_data)} 本书的数据", "SUCCESS")
        return books_data
        
    except TimeoutException:
        debug_print("❌ 页面加载超时", "ERROR")
        return None
    except WebDriverException as e:
        debug_print(f"❌ WebDriver错误: {e}", "ERROR")
        return None
    except Exception as e:
        debug_print(f"❌ 其他错误: {e}", "ERROR")
        return None

def fetch_book_data(url, page_num=1, start_rank=1, driver=None):
    """
    爬取指定URL的页面并提取书籍信息
    page_num: 页码（用于调试显示）
    start_rank: 起始排名（用于计算热度排名）
    driver: Selenium WebDriver实例（可选）
    """
    try:
        debug_print(f"开始请求第{page_num}页URL: {url}")
        
        # 根据配置选择使用Selenium还是requests
        if USE_SELENIUM and SELENIUM_AVAILABLE and driver:
            debug_print("使用Selenium模式获取页面")
            html_content = fetch_page_with_selenium(driver, url)
            if html_content is None:
                debug_print("Selenium获取失败，回退到requests模式", "ERROR")
                # 回退到requests
                response = requests.get(url, headers=HEADERS)
                html_content = response.text
            else:
                # 保存Selenium获取的HTML
                if SAVE_HTML:
                    filename = f'debug_selenium_page{page_num}.html'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    debug_print(f"已保存Selenium HTML到 {filename}")
        else:
            debug_print("使用requests模式获取页面")
            # 代理IP（可选，但推荐）
            # proxies = { "http": "http://your_proxy_ip:port", "https": "https://your_proxy_ip:port" }
            # response = requests.get(url, headers=HEADERS, proxies=proxies)

            response = requests.get(url, headers=HEADERS)
            debug_print(f"HTTP状态码: {response.status_code}")
            debug_print(f"响应头: {dict(response.headers)}")
            
            response.raise_for_status()  # 如果请求失败则抛出异常
            html_content = response.text

            # 保存原始HTML用于调试
            debug_print(f"响应内容长度: {len(response.text)} 字符")
            if SAVE_HTML:
                filename = f'debug_response_page{page_num}.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                debug_print(f"已保存原始HTML到 {filename}")

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 打印页面标题用于确认
        title_tag = soup.find('title')
        if title_tag:
            debug_print(f"页面标题: {title_tag.text}")
        
        # 根据实际页面结构查找书籍列表
        debug_print("尝试查找豆瓣页面中的书籍列表...")
        
        # 查找works-list容器
        works_list = soup.find('ul', class_='works-list')
        if works_list:
            debug_print("找到works-list容器")
            books = works_list.find_all('li')
            debug_print(f"在works-list中找到 {len(books)} 个li元素")
        else:
            debug_print("未找到works-list容器，尝试直接查找li元素...")
            books = soup.find_all('li')
            debug_print(f"直接找到 {len(books)} 个li元素")
        
        # 如果没找到，尝试其他常见的选择器
        if len(books) == 0:
            debug_print("尝试其他可能的选择器...")
            
            # 尝试查找所有包含"书"字的div
            book_divs = soup.find_all('div', string=lambda text: text and '书' in text)
            debug_print(f"找到包含'书'字的div: {len(book_divs)} 个")
            
            # 查找所有class包含book的元素
            book_elements = soup.find_all(class_=lambda x: x and 'book' in x.lower())
            debug_print(f"找到class包含'book'的元素: {len(book_elements)} 个")
            for elem in book_elements[:5]:  # 只显示前5个
                debug_print(f"元素: {elem.name}, class: {elem.get('class')}")
            
            # 查找所有img标签
            img_tags = soup.find_all('img')
            debug_print(f"找到图片标签: {len(img_tags)} 个")
            
            # 查找所有a标签  
            a_tags = soup.find_all('a')
            debug_print(f"找到链接标签: {len(a_tags)} 个")
        
        book_data = []
        for i, book in enumerate(books):
            current_rank = start_rank + i  # 计算当前书籍的热度排名
            debug_print(f"处理第 {i+1} 本书（排名第{current_rank}）...")
            
            try:
                # 根据实际HTML结构提取信息
                title_elem = book.find('div', class_='title')
                author_elem = book.find('div', class_='author')
                abstract_elem = book.find('div', class_='abstract')
                
                if title_elem:
                    title = title_elem.text.strip()
                    debug_print(f"书名: {title}")
                else:
                    debug_print(f"第 {i+1} 本书缺少标题信息")
                    continue
                
                # 处理作者信息
                if author_elem:
                    # 作者信息可能包含多个a标签
                    authors = []
                    author_links = author_elem.find_all('a')
                    if author_links:
                        for link in author_links:
                            authors.append(link.text.strip())
                        author = ', '.join(authors)
                    else:
                        author = author_elem.text.strip()
                    debug_print(f"作者: {author}")
                else:
                    author = "未知作者"
                    debug_print(f"第 {i+1} 本书缺少作者信息")
                
                # 处理简介信息
                if abstract_elem:
                    abstract = abstract_elem.text.strip()
                    # 限制简介长度用于显示
                    if len(abstract) > 200:
                        abstract = abstract[:200] + "..."
                    debug_print(f"简介长度: {len(abstract)} 字符")
                else:
                    abstract = "无简介信息"
                    debug_print(f"第 {i+1} 本书缺少简介信息")
                
                # 组装数据（增加热度排名字段）
                data_row = {
                    '热度排名': current_rank,
                    '书名': title,
                    '作者': author,
                    '简介': abstract,
                    '分类': '计算机与互联网',
                    '字数': '未知',
                    '价格': '未知'
                }
                book_data.append(data_row)
                debug_print(f"成功提取第 {i+1} 本书的信息（排名第{current_rank}）", "SUCCESS")
                
                # 下载图片逻辑（暂时注释）
                # img_elem = book.find('img')
                # if img_elem and img_elem.get('src'):
                #     img_url = img_elem['src']
                #     download_image(img_url, f"{len(book_data)}.jpg")
                
            except Exception as e:
                debug_print(f"处理第 {i+1} 本书时出错: {e}", "ERROR")
                if DEBUG_MODE:
                    import traceback
                    traceback.print_exc()

        debug_print(f"成功提取 {len(book_data)} 本书的数据", "SUCCESS")
        return book_data

    except requests.exceptions.RequestException as e:
        debug_print(f"请求失败: {e}", "ERROR")
        return []
    except Exception as e:
        debug_print(f"解析页面时出错: {e}", "ERROR")
        return []

def download_image(url, filename):
    """
    下载单张图片
    """
    try:
        img_response = requests.get(url, headers=HEADERS)
        img_response.raise_for_status()
        with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
            f.write(img_response.content)
        debug_print(f"已下载: {filename}", "SUCCESS")
    except requests.exceptions.RequestException as e:
        debug_print(f"图片下载失败: {e}", "ERROR")

def save_to_csv(data):
    """
    将数据追加到CSV文件（使用UTF-8 BOM编码）
    """
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['热度排名', '书名', '作者', '简介', '分类', '字数', '价格'])
        writer.writerows(data)

# --- 主程序 ---
def main():
    """主函数"""
    global DEBUG_MODE, SAVE_HTML, MAX_PAGES, USE_SELENIUM
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='豆瓣读书爬虫')
    parser.add_argument('--debug', action='store_true', help='开启调试模式')
    parser.add_argument('--no-debug', action='store_true', help='关闭调试模式')
    parser.add_argument('--save-html', action='store_true', help='保存原始HTML文件')
    parser.add_argument('--no-save-html', action='store_true', help='不保存原始HTML文件')
    parser.add_argument('--pages', type=int, default=MAX_PAGES, help=f'爬取页数 (默认: {MAX_PAGES})')
    parser.add_argument('--use-selenium', action='store_true', help='强制使用Selenium浏览器模式')
    parser.add_argument('--no-selenium', action='store_true', help='强制使用requests模式')
    
    args = parser.parse_args()
    
    # 根据命令行参数调整配置
    if args.debug:
        DEBUG_MODE = True
    elif args.no_debug:
        DEBUG_MODE = False
    
    if args.save_html:
        SAVE_HTML = True
    elif args.no_save_html:
        SAVE_HTML = False
    
    if args.use_selenium:
        USE_SELENIUM = True
    elif args.no_selenium:
        USE_SELENIUM = False
    
    MAX_PAGES = args.pages
    
    print("=" * 50)
    print("豆瓣读书爬虫启动")
    print("=" * 50)
    
    debug_print(f"程序配置:")
    debug_print(f"- 调试模式: {DEBUG_MODE}")
    debug_print(f"- 保存HTML: {SAVE_HTML}")
    debug_print(f"- 爬取页数: {MAX_PAGES}")
    debug_print(f"- 使用Selenium: {USE_SELENIUM}")
    debug_print(f"- Selenium可用: {SELENIUM_AVAILABLE}")
    
    # 根据配置选择爬取方式
    if USE_SELENIUM:
        if not SELENIUM_AVAILABLE:
            print("❌ 错误：指定使用Selenium但Selenium不可用")
            return
        debug_print("✅ 将使用Selenium浏览器模式进行爬取")
    else:
        debug_print("🔧 将使用requests模式进行爬取")
    
    all_books = []
    current_ranking = 1
    driver = None
    
    # 初始化WebDriver（如果需要）
    if USE_SELENIUM and SELENIUM_AVAILABLE:
        debug_print("初始化Chrome浏览器...")
        driver = init_webdriver()
        if driver is None:
            print("❌ 错误：无法初始化WebDriver")
            return
    
    try:
        debug_print("开始爬取豆瓣读书...")
        
        for page_num in range(1, MAX_PAGES + 1):
            debug_print(f"\n--- 开始爬取第 {page_num} 页 ---")
            
            url = f"https://read.douban.com/category/105?sort=hot&page={page_num}"
            
            # 根据配置选择爬取方式
            if USE_SELENIUM and driver:
                books_data = fetch_book_data_selenium(url, driver, page_num)
            else:
                books_data = fetch_book_data(url, page_num)
            
            if books_data is None:
                debug_print(f"第 {page_num} 页获取失败，跳过")
                continue
            
            if not books_data:
                debug_print(f"第 {page_num} 页没有找到书籍数据")
                continue
            
            # 添加排名信息
            for book in books_data:
                book['热度排名'] = current_ranking
                current_ranking += 1
            
            all_books.extend(books_data)
            
            debug_print(f"第 {page_num} 页成功获取 {len(books_data)} 本书")
            
            # 延迟避免请求太频繁
            if page_num < MAX_PAGES:
                debug_print("等待2秒...")
                time.sleep(2)
    
    finally:
        # 关闭WebDriver
        if driver:
            debug_print("关闭浏览器...")
            driver.quit()
    
    debug_print(f"所有页面爬取完成，共获得 {len(all_books)} 本书的数据")
    
    if all_books:
        debug_print("开始保存数据到CSV...")
        save_to_csv(all_books)
        debug_print(f"成功将 {len(all_books)} 本书的信息存入 {CSV_FILE}")
    else:
        debug_print("⚠️  没有获取到任何数据！")
        debug_print("请检查:")
        debug_print("  1. 网络连接是否正常")
        debug_print("  2. 目标网站是否可以访问")
        debug_print("  3. CSS选择器是否正确")
        debug_print("  4. 是否需要处理反爬虫机制")
        debug_print("  5. 检查 debug_response_page*.html 文件查看实际页面内容")

    debug_print("程序结束", "MAIN")

if __name__ == "__main__":
    main()