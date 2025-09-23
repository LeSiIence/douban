import requests
import json

# 尝试寻找API接口
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest'
}

# 可能的API端点
api_urls = [
    "https://read.douban.com/j/category/105/works",
    "https://read.douban.com/j/category/105/works?page=1",
    "https://read.douban.com/j/category/works?category_id=105",
    "https://read.douban.com/api/category/105/works",
    "https://read.douban.com/j/works?category=105",
]

for url in api_urls:
    try:
        print(f"\n测试API: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON响应: {str(data)[:200]}...")
                if 'works' in data:
                    print(f"找到works字段，包含 {len(data['works'])} 项")
            except:
                print("非JSON响应")
                print(f"内容长度: {len(response.text)}")
        
    except Exception as e:
        print(f"请求失败: {e}")