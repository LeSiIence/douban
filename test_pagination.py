import requests
from bs4 import BeautifulSoup

# 测试不同的URL参数
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 测试可能的分页URL
test_urls = [
    "https://read.douban.com/category/105?page=2",
    "https://read.douban.com/category/105?start=10",  
    "https://read.douban.com/category/105?offset=10",
    "https://read.douban.com/category/105?p=2",
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
                first_title = books[0].find('div', class_='title')
                if first_title:
                    print(f"第一本书: {first_title.text.strip()}")
        else:
            print("未找到书籍列表")
    except Exception as e:
        print(f"请求失败: {e}")