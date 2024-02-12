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

# Find and print the text for the first specified element
try:
    target_element_1 = driver.find_element(By.CLASS_NAME, 'css-1i59yj2')
    print(target_element_1.text)
except Exception as e:
    print('Element with class css-1i59yj2 not found or error occurred:', e)

# Find and print the text for the second specified element
try:
    target_element_2 = driver.find_element(By.CLASS_NAME, 'css-19a56l9')
    print(target_element_2.text)
except Exception as e:
    print('Element with class css-19a56l9 not found or error occurred:', e)

# Find and print the text for the third specified element
try:
    target_element_3 = driver.find_element(By.CLASS_NAME, 'css-13cxduj')
    print(target_element_3.text)
except Exception as e:
    print('Element with class css-13cxduj not found or error occurred:', e)

# Clean up by closing the browser
driver.quit()