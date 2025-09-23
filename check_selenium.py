# 检查是否安装了selenium和webdriver
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    print("✅ Selenium已安装")
    selenium_available = True
except ImportError as e:
    print(f"❌ Selenium未安装: {e}")
    print("请运行: pip install selenium")
    selenium_available = False

# 检查ChromeDriver
if selenium_available:
    try:
        options = Options()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # 尝试自动查找ChromeDriver
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ ChromeDriver可用（自动模式）")
            driver.quit()
            webdriver_available = True
        except Exception:
            # 尝试指定常见路径
            common_paths = [
                r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
                r"C:\chromedriver.exe",
                "chromedriver.exe"
            ]
            
            webdriver_available = False
            for path in common_paths:
                try:
                    service = Service(path)
                    driver = webdriver.Chrome(service=service, options=options)
                    print(f"✅ ChromeDriver可用: {path}")
                    driver.quit()
                    webdriver_available = True
                    break
                except Exception:
                    continue
            
            if not webdriver_available:
                print("❌ ChromeDriver不可用")
                print("请下载ChromeDriver: https://chromedriver.chromium.org/")
    except Exception as e:
        print(f"❌ WebDriver测试失败: {e}")
        webdriver_available = False
else:
    webdriver_available = False

if selenium_available and webdriver_available:
    print("\n🎉 Selenium环境准备就绪，可以使用浏览器自动化")
else:
    print("\n⚠️  Selenium环境未准备好，将使用备用方案")