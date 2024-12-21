from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import os
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service



app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 自動安裝 ChromeDriver
chromedriver_autoinstaller.install()
# 設置 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--headless")  # 無頭模式
chrome_options.add_argument("--no-sandbox")  # 解除沙盒限制
chrome_options.add_argument("--disable-dev-shm-usage")  # 避免共享內存問題

# 啟動 Chrome
driver = webdriver.Chrome(service=Service(), options=chrome_options)

def setup_driver():
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(service=Service(), options=options)

def is_good_name(name):
    """
    判斷商品名稱是否具有足夠的資訊
    
    規則：
    1. 長度在 5-100 字之間
    2. 不是太通用的詞彙
    3. 包含具體描述
    """
    if not name or len(name) < 5 or len(name) > 100:
        return False
    
    # 排除一些通用或無意義的名稱
    bad_keywords = [
        'product', 'item', 'sale', 'wts', 'wtb', 'for sale', 
        'bunjang', 'global', 'sign', 'album', 'photocard'
    ]
    
    name_lower = name.lower()
    if any(keyword in name_lower for keyword in bad_keywords):
        return False
    
    return True

@app.route('/')
def index():
    return render_template('product_scraper.html')

@app.route('/scrape', methods=['POST'])
def scrape_product():
    url = request.json.get('url')
    
    if not url:
        return jsonify({"error": "未提供網址"}), 400

    driver = None
    try:
        driver = setup_driver()
        driver.get(url)

        # 等待頁面加載
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # 獲取網頁內容
        html_content = driver.page_source

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # 先從 alt 屬性提取韓文原文
        korean_title = None
        
        # 尋找具有特定特徵的圖片
        img_tags = soup.find_all('img', {
            'fetchpriority': 'high', 
            'data-nimg': 'fill', 
            'class': 'osrq1v4',
            'alt': True
        })
        
        if img_tags:
            korean_title = img_tags[0].get('alt')

        # 查找 JSON-LD 資料
        script_tags = soup.find_all("script", type="application/ld+json")
        for script_tag in script_tags:
            try:
                product_data = json.loads(script_tag.string)

                # 確保資料包含所需字段
                if product_data.get("@type") == "Product":
                    image_url = product_data.get("image")
                    name = product_data.get("name")
                    description = product_data.get("description")
                    offers = product_data.get("offers")

                    # 如果 offers 是列表，提取第一個元素
                    if isinstance(offers, list):
                        offers = offers[0]

                    price = offers.get("price") if offers else None
                    price_currency = offers.get("priceCurrency") if offers else None

                    # 評估商品名稱的品質
                    name_quality = is_good_name(name)

                    return jsonify({
                        "image": image_url,
                        "name": name,
                        "korean_name": korean_title or name,  # 如果沒找到特定圖片的 alt，則使用原始 name
                        "description": description,
                        "price": price,
                        "currency": price_currency,
                        "name_quality": name_quality
                    })
            except json.JSONDecodeError:
                continue
        
        return jsonify({"error": "未找到商品資訊"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
