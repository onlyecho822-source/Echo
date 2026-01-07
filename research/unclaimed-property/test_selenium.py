#!/usr/bin/env python3
"""Test Selenium setup"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

print("Testing Selenium setup...")

chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service('/usr/bin/chromedriver')

print("Creating driver...")
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Navigating to test page...")
driver.get('https://www.google.com')

print(f"Page title: {driver.title}")

driver.quit()
print("Test successful!")
