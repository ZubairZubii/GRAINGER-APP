from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape_endpoint():
    product_id = request.args.get("product_id")

    if not product_id:
        return jsonify({"error": "Missing ?product_id"}), 400

    try:
        # ✅ Setup Chrome
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/116.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)

        # ✅ Step 1: Go to homepage
        driver.get("https://www.grainger.com/")

        # ✅ Step 2: Enter product ID into search bar
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.gcom__typeahead-query-field"))
        )
        search_input.clear()
        search_input.send_keys(product_id)

        # ✅ Step 3: Click search button
        search_button = driver.find_element(By.CSS_SELECTOR, "button.gcom__typeahead-submit-button")
        search_button.click()

        # ✅ Step 4: Wait until price appears on product page
        price_elem = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span[data-testid^='pricing-component']")
            )
        )
        price = price_elem.text.strip()

        return jsonify({
            "product_id": product_id,
            "price": price
        })

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
