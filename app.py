from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape_endpoint():
    product_id = request.args.get("product_id")

    if not product_id:
        return jsonify({"error": "Missing ?product_id"}), 400

    try:
        # ✅ Setup undetected Chrome (works in Railway)
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/116.0.0.0 Safari/537.36"
        )

        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)

        # ✅ Step 1: Go to homepage
        driver.get("https://www.grainger.com/")

        # ✅ Step 2: Enter product ID
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.gcom__typeahead-query-field"))
        )
        search_input.clear()
        search_input.send_keys(product_id)

        # ✅ Step 3: Click search button
        search_button = driver.find_element(By.CSS_SELECTOR, "button.gcom__typeahead-submit-button")
        search_button.click()

        # ✅ Step 4: Extract price
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
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
