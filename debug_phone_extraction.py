#!/usr/bin/env python3
"""
Debug script to test phone number extraction from Google Maps
"""

import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def create_debug_driver():
    """Create Chrome driver for debugging"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def debug_phone_extraction():
    """Debug phone number extraction on a specific business"""
    driver = create_debug_driver()
    
    try:
        # Test with a known business that should have a phone number
        test_url = "https://www.google.com/maps/place/Starbucks/@37.7749,-122.4194,15z"
        print(f"🔍 Testing phone extraction on: {test_url}")
        
        driver.get(test_url)
        time.sleep(5)
        
        # Get page source for analysis
        page_source = driver.page_source
        print(f"📄 Page loaded, source length: {len(page_source)} characters")
        
        # Test all phone selectors
        phone_selectors = [
            # XPath selectors
            "//button[contains(@aria-label,'Phone')]",
            "//button[contains(@data-item-id,'phone')]", 
            "//div[contains(@data-item-id,'phone')]//span",
            "//a[contains(@href,'tel:')]",
            "//span[contains(text(),'(') and contains(text(),')')]",
            "//div[contains(@class,'fontBodyMedium') and contains(text(),'(')]",
            "//button[contains(@data-item-id, 'phone')]//div[contains(@class, 'Io6YTe')]",
            '//span[@class="UsdlK"]',
            "//button[contains(@aria-label,'Call')]",
            "//div[contains(@class,'Io6YTe') and contains(text(),'(')]",
            # CSS selectors
            'button[data-item-id*="phone"]',
            '.rogA2c button[aria-label*="phone"]', 
            'button[aria-label*="Call"]',
            '.Io6YTe.fontBodyMedium.kR99db.fdkmkc[aria-label*="phone"]',
            'button[data-item-id="phone:tel:"]',
            '[data-item-id*="phone"]'
        ]
        
        print("\n📞 Testing phone selectors:")
        found_elements = []
        
        for i, selector in enumerate(phone_selectors, 1):
            try:
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"✅ Selector {i:2d}: Found {len(elements)} elements - {selector}")
                    for j, element in enumerate(elements[:3]):  # Show first 3 matches
                        try:
                            text = element.text.strip()
                            aria_label = element.get_attribute('aria-label') or ''
                            href = element.get_attribute('href') or ''
                            data_item_id = element.get_attribute('data-item-id') or ''
                            
                            print(f"    Element {j+1}:")
                            print(f"      Text: '{text}'")
                            print(f"      Aria-label: '{aria_label}'")
                            print(f"      Href: '{href}'")
                            print(f"      Data-item-id: '{data_item_id}'")
                            
                            found_elements.append({
                                'selector': selector,
                                'text': text,
                                'aria_label': aria_label,
                                'href': href,
                                'data_item_id': data_item_id
                            })
                        except Exception as e:
                            print(f"      Error getting element info: {e}")
                else:
                    print(f"❌ Selector {i:2d}: No elements found - {selector}")
                    
            except Exception as e:
                print(f"❌ Selector {i:2d}: Error - {selector} - {e}")
        
        # Test phone number patterns
        print(f"\n🔍 Testing phone patterns on found text:")
        phone_patterns = [
            re.compile(r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'),
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            re.compile(r'\(\d{3}\)\s?\d{3}[-.]?\d{4}'),
            re.compile(r'tel[:\s]*(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})', re.IGNORECASE),
            re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),  # More flexible
            re.compile(r'\d{10}'),  # Just 10 digits
        ]
        
        all_text = ' '.join([elem['text'] + ' ' + elem['aria_label'] + ' ' + elem['href'] for elem in found_elements])
        print(f"Combined text to search: '{all_text}'")
        
        for i, pattern in enumerate(phone_patterns, 1):
            matches = pattern.findall(all_text)
            if matches:
                print(f"✅ Pattern {i}: Found matches - {matches}")
            else:
                print(f"❌ Pattern {i}: No matches")
        
        # Look for any phone-like text in the entire page
        print(f"\n🔍 Searching entire page source for phone patterns:")
        for i, pattern in enumerate(phone_patterns, 1):
            matches = pattern.findall(page_source)
            if matches:
                print(f"✅ Pattern {i} in page source: Found {len(matches)} matches - {matches[:5]}")  # Show first 5
        
        # Save page source for manual inspection
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"\n💾 Page source saved to debug_page_source.html for manual inspection")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_phone_extraction()
