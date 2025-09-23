import requests
import json
from bs4 import BeautifulSoup
import time

# 分析豆瓣的网络请求，寻找真正的API接口
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://read.douban.com/category/105',
    'X-Requested-With': 'XMLHttpRequest'
}

# 尝试不同的API路径和参数组合
test_apis = [
    # 基于常见的豆瓣API模式
    "https://read.douban.com/j/category/105/more",
    "https://read.douban.com/j/category/105/works",
    "https://read.douban.com/j/more_works",
    "https://read.douban.com/j/category_works",
    # 尝试带参数的
    "https://read.douban.com/j/category/105/more?start=0&count=10",
    "https://read.douban.com/j/category/105/more?start=10&count=10",
    "https://read.douban.com/j/category/105/works?start=0&count=10&sort=hot",
    "https://read.douban.com/j/category/105/works?start=10&count=10&sort=hot",
    # 不同的路径格式
    "https://read.douban.com/api/v1/category/105/works",
    "https://read.douban.com/category/105/j/more",
]

print("正在测试可能的API接口...")
for api_url in test_apis:
    try:
        print(f"\n测试: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"内容类型: {content_type}")
            
            if 'json' in content_type:
                try:
                    data = response.json()
                    print(f"JSON响应结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"  {key}: 数组，长度 {len(value)}")
                            else:
                                print(f"  {key}: {type(value)} - {str(value)[:100]}")
                except json.JSONDecodeError:
                    print("响应不是有效的JSON")
                    print(f"响应内容前200字符: {response.text[:200]}")
            else:
                print(f"非JSON响应，长度: {len(response.text)}")
        
        time.sleep(0.5)  # 避免请求过快
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

print("\nAPI接口测试完成")