from urllib.parse import urlparse
import re
import io
import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define price-fetching functions
def fetch_nykaa_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(10)  # Allow page to load fully

        # Try to extract the price using class name
        try:
            price_element = driver.find_element(By.CLASS_NAME, "css-1jczs19")
            price = price_element.text.strip().replace('₹', '').replace(',', '')
        except Exception:
            # Fallback to regex if direct extraction fails
            page_source = driver.page_source
            match = re.search(r'₹\s?(\d{1,5}(?:,\d{3})*)', page_source)
            price = match.group(1).replace(',', '') if match else "NA"

    except Exception as e:
        print(f"Error fetching Nykaa price: {e}")
        price = "NA"
    
    finally:
        driver.quit()  # Ensure the browser is closed properly

    return price

def fetch_amazon_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        # Wait for the price element to be visible
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "a-price-whole"))
        )

        # Extract and clean the price
        price = price_element.text.strip().replace(',', '')

        return price if price else "NA"

    except Exception as e:
        print(f"Error fetching Amazon price: {e}")
        return "NA"

    finally:
        driver.quit()  # Close browser session
                
def fetch_flipkart_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        
        # Wait for the price element to load
        try:
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Nx9bqj.CxhGGd"))
            )
        except:
            try:
                price_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "_30jeq3._16Jk6d"))
                )
            except:
                try:
                    price_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "._25b18c ._30jeq3"))
                    )
                except:
                    return "NA"
        
        price = price_element.text.strip().replace('₹', '').replace(',', '')

        return price

    except Exception as e:
        print(f"Error: {e}")
        return "NA"

    finally:
        driver.quit()  # Close browser instance

def fetch_myntra_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        
        # Wait for the price element to load
        try:
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pdp-discount-container"))
            )
            price_text = price_element.text.strip().replace('₹', '').replace(',', '')

            # Extract only the numeric discounted price
            price = price_text.split()[0]  # Extracts only the first numeric value

            return price

        except Exception as e:
            print(f"Error fetching Myntra price: {e}")
            return "NA"

    finally:
        driver.quit()  # Close browser instance
        
def fetch_zepto_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        # Wait for price element to be visible
        try:
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[itemprop='price']"))
            )
            price = price_element.get_attribute("content")  # Extracts price

            return price if price else "NA"

        except Exception as e:
            print(f"Error fetching Zepto price: {e}")
            return "NA"

    finally:
        driver.quit()  # Close browser session

def fetch_faceshop_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        # Wait for the price element to be visible
        try:
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "price-item--sale"))
            )
            price = price_element.text.strip().replace('₹', '').replace(',', '')  # Extracts price

            return price if price else "NA"

        except Exception as e:
            print(f"Error fetching Faceshop price: {e}")
            return "NA"

    finally:
        driver.quit()  # Close browser session
        
def fetch_blinkit_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(10)  # Give time for JavaScript content to load

        # Get the full page source
        page_source = driver.page_source

        # Extract the price using regex (₹ followed by numbers)
        match = re.search(r'₹\s?(\d{1,5}(?:,\d{3})*)', page_source)

        if match:
            price = match.group(1).replace(',', '')  # Remove commas
        else:
            price = "NA"

    except NoSuchWindowException:
        print("Error: Browser window closed unexpectedly.")
        price = "NA"
    
    except Exception as e:
        print(f"Error fetching price: {e}")
        price = "NA"
    
    finally:
        driver.quit()  # Close the driver properly
    
    return price

def identify_sales_channel(url):
    if not isinstance(url, str):
        return 'Unknown'

    channels = {
        'nykaa': 'Nykaa',
        'amazon': 'Amazon',
        'myntra': 'Myntra',
        'flipkart': 'Flipkart',
        'zepto': 'Zepto',
        'faceshop': 'Faceshop',
        'blinkit': 'Blinkit'
    }

    parsed_url = urlparse(url).netloc.lower()  # Extract domain

    for keyword, channel in channels.items():
        if keyword in parsed_url:
            return channel
    return 'NA'

def fetch_price(channel, url, retries=3, delay=2):
    log = []
    
    for attempt in range(1, retries + 1):
        try:
            if channel == 'Amazon':
                return fetch_amazon_price(url)
            elif channel == 'Nykaa':
                return fetch_nykaa_price(url)
            elif channel == 'Flipkart':
                return fetch_flipkart_price(url)
            elif channel == 'Myntra':
                return fetch_myntra_price(url)
            elif channel == 'Zepto':
                return fetch_zepto_price(url)
            elif channel == 'Faceshop':
                return fetch_faceshop_price(url)
            elif channel == 'Blinkit':
                return fetch_blinkit_price(url)
            else:
                return "NA"
        
        except Exception as e:
            log.append(f"Attempt {attempt}: Failed to fetch price for {channel}. Error: {e}")
            if attempt < retries:
                time.sleep(delay * (2 ** (attempt - 1)))  # Exponential backoff
            else:
                return "NA"

    return "NA"
