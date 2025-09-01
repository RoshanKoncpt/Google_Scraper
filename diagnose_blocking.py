#!/usr/bin/env python3
"""
Diagnostic test to identify if Google Maps is blocking or limiting results
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

def diagnose_google_maps_blocking():
    """Diagnose if Google Maps is blocking or limiting our scraper"""
    
    options = Options()
    # Try with non-headless mode to see what's actually happening
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("🔍 DIAGNOSTIC TEST - Checking Google Maps behavior")
        
        # Test 1: Simple broad search that should return many results
        query = "restaurants"  # Very broad
        search_url = f"https://www.google.com/maps/search/{query}"
        
        print(f"🌐 Testing URL: {search_url}")
        driver.get(search_url)
        time.sleep(10)
        
        print(f"📄 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Check for blocking indicators
        blocking_indicators = [
            "sorry", "blocked", "unusual traffic", "captcha", 
            "verify", "robot", "automated", "consent"
        ]
        
        page_text = driver.page_source.lower()
        current_url = driver.current_url.lower()
        
        print("\n🚫 CHECKING FOR BLOCKING INDICATORS:")
        blocking_detected = False
        for indicator in blocking_indicators:
            if indicator in page_text or indicator in current_url:
                print(f"❌ BLOCKING DETECTED: '{indicator}' found")
                blocking_detected = True
        
        if not blocking_detected:
            print("✅ No obvious blocking detected")
        
        # Test 2: Count actual visible business elements
        print(f"\n📊 COUNTING VISIBLE BUSINESS ELEMENTS:")
        
        # All possible business selectors
        business_selectors = [
            "//div[contains(@class, 'Nv2PK')]",
            "//div[@role='article']", 
            "//a[contains(@href, '/maps/place/')]",
            "//div[contains(@class, 'bfdHYd')]",
            "//div[contains(@class, 'lI9IFe')]",
            "//div[contains(@jsaction, 'mouseover')]"
        ]
        
        total_elements = 0
        for i, selector in enumerate(business_selectors, 1):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                print(f"Selector {i}: {len(elements)} elements - {selector}")
                total_elements += len(elements)
            except Exception as e:
                print(f"Selector {i}: ERROR - {e}")
        
        print(f"📊 Total business-like elements found: {total_elements}")
        
        # Test 3: Check if scrolling loads more content
        print(f"\n🔄 TESTING SCROLL BEHAVIOR:")
        
        # Count links before scrolling
        initial_links = set()
        link_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/maps/place/')]")
        for elem in link_elements:
            href = elem.get_attribute('href')
            if href:
                initial_links.add(href)
        
        print(f"Links before scroll: {len(initial_links)}")
        
        # Perform aggressive scrolling
        for scroll_attempt in range(5):
            try:
                # Try multiple scroll methods
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Try scrolling the results panel
                try:
                    results_panel = driver.find_element(By.CSS_SELECTOR, "[role='main']")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
                except:
                    pass
                
                time.sleep(3)
                
                # Count links after scroll
                current_links = set()
                link_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/maps/place/')]")
                for elem in link_elements:
                    href = elem.get_attribute('href')
                    if href:
                        current_links.add(href)
                
                new_links = len(current_links) - len(initial_links)
                print(f"Scroll {scroll_attempt + 1}: {len(current_links)} total links (+{new_links} new)")
                
                if new_links == 0:
                    print("⚠️ No new links loaded - may have reached limit")
                
                initial_links = current_links
                
            except Exception as e:
                print(f"Scroll error: {e}")
        
        final_unique_links = len(initial_links)
        print(f"\n📊 FINAL DIAGNOSIS:")
        print(f"Total unique business links found: {final_unique_links}")
        
        if final_unique_links <= 5:
            print("❌ CRITICAL ISSUE: Very few results found")
            print("Possible causes:")
            print("1. Google Maps is actively blocking automated access")
            print("2. IP address is rate limited or flagged")
            print("3. Geographic region has limited businesses")
            print("4. Google has changed their HTML structure significantly")
        elif final_unique_links <= 15:
            print("⚠️ MODERATE ISSUE: Limited results")
            print("May need different approach or query optimization")
        else:
            print("✅ GOOD: Reasonable number of results found")
        
        # Save page source for manual inspection
        with open('diagnostic_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\n💾 Page source saved to diagnostic_page_source.html")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("Press Enter to close browser and continue...")  # Keep browser open for manual inspection
        driver.quit()

if __name__ == "__main__":
    diagnose_google_maps_blocking()
