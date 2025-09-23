import requests
from bs4 import BeautifulSoup

# 测试正确的分页URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 测试多页URL
test_urls = [
    "https://read.douban.com/category/105?sort=hot&page=1",
    "https://read.douban.com/category/105?sort=hot&page=2", 
    "https://read.douban.com/category/105?sort=hot&page=3",
]

for url in test_urls:
    try:
        print(f"\n测试URL: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        works_list = soup.find('ul', class_='works-list')
        if works_list:
            books = works_list.find_all('li')
            print(f"找到书籍数量: {len(books)}")
            if books:
                # 显示前3本书的标题
                for i, book in enumerate(books[:3]):
                    title_elem = book.find('div', class_='title')
                    if title_elem:
                        print(f"  {i+1}. {title_elem.text.strip()}")
        else:
            print("未找到书籍列表")
    except Exception as e:
        print(f"请求失败: {e}")