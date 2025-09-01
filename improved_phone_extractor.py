#!/usr/bin/env python3
"""
Improved phone number extraction for Google Maps scraper
"""

import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def extract_phone_from_business_page(driver, business_url):
    """
    Enhanced phone extraction method with comprehensive selectors
    """
    try:
        print(f"📞 Extracting phone from: {business_url[:60]}...")
        driver.get(business_url)
        time.sleep(3)
        
        # Comprehensive list of phone selectors (updated for 2024 Google Maps)
        phone_selectors = [
            # Primary phone button selectors
            "//button[@data-item-id='phone:tel:']",
            "//button[contains(@data-item-id,'phone')]",
            "//div[@data-item-id='phone:tel:']",
            
            # Phone number in contact info section
            "//div[contains(@class,'rogA2c')]//button[contains(@aria-label,'Phone')]",
            "//div[contains(@class,'rogA2c')]//button[contains(@aria-label,'Call')]",
            "//div[contains(@class,'rogA2c')]//div[contains(@class,'Io6YTe')]",
            
            # Direct phone text elements
            "//span[contains(text(),'(') and contains(text(),')') and string-length(text()) > 10]",
            "//div[contains(text(),'(') and contains(text(),')') and string-length(text()) > 10]",
            
            # Phone links
            "//a[starts-with(@href,'tel:')]",
            
            # Business info sections
            "//div[contains(@class,'fontBodyMedium') and contains(text(),'(')]",
            "//div[contains(@class,'fontBodyMedium') and contains(text(),'-')]",
            
            # Generic contact buttons
            "//button[contains(@aria-label,'Phone')]",
            "//button[contains(@aria-label,'Call')]",
            "//div[@role='button'][contains(@aria-label,'Phone')]",
            "//div[@role='button'][contains(@aria-label,'Call')]",
            
            # Fallback selectors
            "//*[contains(text(),'(') and contains(text(),')')]",
            "//*[contains(@aria-label,'phone')]",
            "//*[contains(@aria-label,'call')]"
        ]
        
        # Enhanced phone patterns
        phone_patterns = [
            re.compile(r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'),  # (123) 456-7890
            re.compile(r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'),     # 123-456-7890
            re.compile(r'\+1\s*\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'),  # +1 (123) 456-7890
            re.compile(r'\+1\s*\d{3}[-.\s]\d{3}[-.\s]\d{4}'),    # +1 123-456-7890
            re.compile(r'\d{10}'),                          # 1234567890
            re.compile(r'\+\d{1,3}\s*\d{3,4}[-.\s]?\d{3}[-.\s]?\d{4}'),  # International
        ]
        
        found_phone = None
        
        # Try each selector
        for selector in phone_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                
                for element in elements:
                    # Get text from multiple sources
                    text_sources = [
                        element.get_attribute('aria-label') or '',
                        element.get_attribute('href') or '',
                        element.get_attribute('data-item-id') or '',
                        element.text or ''
                    ]
                    
                    for text in text_sources:
                        if not text:
                            continue
                            
                        # Clean the text
                        text = text.replace('tel:', '').replace('Phone: ', '').replace('Call ', '')
                        
                        # Try each pattern
                        for pattern in phone_patterns:
                            match = pattern.search(text)
                            if match:
                                phone = match.group(0)
                                # Validate - must have at least 10 digits
                                digits = re.sub(r'\D', '', phone)
                                if len(digits) >= 10:
                                    found_phone = phone
                                    print(f"✅ Found phone: {found_phone}")
                                    return found_phone
                                    
            except Exception as e:
                continue
        
        # If no phone found with selectors, try searching page source
        if not found_phone:
            print("🔍 Searching page source for phone patterns...")
            page_source = driver.page_source
            
            for pattern in phone_patterns:
                matches = pattern.findall(page_source)
                for match in matches:
                    digits = re.sub(r'\D', '', match)
                    if len(digits) >= 10:
                        found_phone = match
                        print(f"✅ Found phone in page source: {found_phone}")
                        return found_phone
        
        print("❌ No phone number found")
        return None
        
    except Exception as e:
        print(f"❌ Phone extraction error: {e}")
        return None

def test_phone_extraction():
    """Test the improved phone extraction"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Test URLs - replace with actual Google Maps business URLs
        test_urls = [
            "https://www.google.com/maps/search/restaurants+near+me",  # This will redirect to actual results
        ]
        
        for url in test_urls:
            phone = extract_phone_from_business_page(driver, url)
            print(f"Result for {url}: {phone}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    test_phone_extraction()
