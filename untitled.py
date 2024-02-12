from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Setup Selenium with ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# URL of the webpage you want to scrape
url = 'https://theddari.com/kimp'

# Navigate to the webpage
driver.get(url)

# Wait for the dynamic content to load
time.sleep(5)  # Adjust the sleep time as needed

# Find the element with the specific class
try:
    target_element = driver.find_element(By.CLASS_NAME, 'chakra-text.css-hghil1')
    print(target_element.text)
except Exception as e:
    print('Element not found or error occurred:', e)

# Clean up by closing the browser
driver.quit()