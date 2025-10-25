from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chrome_driver():
    """Create and return a configured Chrome WebDriver"""
    options = Options()
    
    # Essential options for headless mode on server
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    
    # Anti-detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # User agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    
    # Additional stability options
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--single-process")
    
    # Set binary location if needed
    options.binary_location = "/usr/bin/google-chrome"
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "endpoints": {
            "/scrape": "GET with ?product_id=<id>"
        }
    })

@app.route("/scrape", methods=["GET"])
def scrape_endpoint():
    product_id = request.args.get("product_id")

    if not product_id:
        return jsonify({"error": "Missing ?product_id"}), 400

    driver = None
    try:
        logger.info(f"Starting scrape for product_id: {product_id}")
        
        # Initialize driver
        driver = get_chrome_driver()
        wait = WebDriverWait(driver, 20)

        logger.info("Navigating to Grainger homepage")
        driver.get("https://www.grainger.com/")

        logger.info("Finding search input")
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.gcom__typeahead-query-field"))
        )
        search_input.clear()
        search_input.send_keys(product_id)

        logger.info("Clicking search button")
        search_button = driver.find_element(By.CSS_SELECTOR, "button.gcom__typeahead-submit-button")
        search_button.click()

        logger.info("Waiting for price element")
        price_elem = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span[data-testid^='pricing-component']")
            )
        )
        price = price_elem.text.strip()

        logger.info(f"Successfully scraped price: {price}")
        return jsonify({
            "success": True,
            "product_id": product_id,
            "price": price
        })

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)