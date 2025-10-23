import os
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Grainger Scraper API is running",
        "usage": "/scrape?product_id=YOUR_PRODUCT_ID",
        "example": "/scrape?product_id=34RY84"
    })

@app.route("/scrape", methods=["GET"])
def scrape_endpoint():
    product_id = request.args.get("product_id")
    if not product_id:
        return jsonify({"error": "Missing ?product_id parameter"}), 400

    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        wait = WebDriverWait(driver, 20)

        driver.get("https://www.grainger.com/")

        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.gcom__typeahead-query-field"))
        )
        search_input.clear()
        search_input.send_keys(product_id)

        search_button = driver.find_element(By.CSS_SELECTOR, "button.gcom__typeahead-submit-button")
        search_button.click()

        price_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid^='pricing-component']"))
        )
        price = price_elem.text.strip()

        return jsonify({
            "success": True,
            "product_id": product_id,
            "price": price
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "product_id": product_id
        }), 500

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)