#!/usr/bin/env python3
"""
Debug script to identify why we're only getting 4-5 results
"""

import re
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def debug_google_maps_results():
    """Debug the Google Maps scraping process step by step"""
    
    # Setup Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Test search
        search_query = "restaurants in Chicago"
        max_results = 20
        
        print(f"🔍 DEBUG: Searching for '{search_query}' with max_results={max_results}")
        
        # Navigate to Google Maps
        search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        print(f"🌐 Navigating to: {search_url}")
        
        driver.get(search_url)
        time.sleep(10)  # Wait longer initially
        
        print(f"📄 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Check for consent/blocking
        if "consent" in driver.current_url.lower() or "sorry" in driver.title.lower():
            print("🚫 Detected consent page or blocking")
            return
        
        # Debug: Check what elements are actually on the page
        print("\n🔍 DEBUGGING AVAILABLE ELEMENTS:")
        
        # Test all possible link selectors
        link_selectors = [
            '//a[contains(@href, "/maps/place/")]',
            '//div[@role="article"]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "Nv2PK")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "bfdHYd")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "lI9IFe")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@jsaction, "mouseover")]//a[contains(@href, "/maps/place/")]'
        ]
        
        all_links = set()
        
        for i, selector in enumerate(link_selectors, 1):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                print(f"Selector {i}: Found {len(elements)} elements - {selector}")
                
                for element in elements:
                    href = element.get_attribute('href')
                    if href and '/maps/place/' in href:
                        all_links.add(href)
                        
            except Exception as e:
                print(f"Selector {i}: ERROR - {e}")
        
        print(f"\n📊 Initial links found: {len(all_links)}")
        
        if len(all_links) < 5:
            print("⚠️ Very few links found initially. Checking page structure...")
            
            # Save page source for analysis
            with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("💾 Page source saved to debug_page_source.html")
            
            # Check for common Google Maps elements
            common_elements = [
                "div[role='main']",
                ".m6QErb",
                "#pane",
                ".siAUzd",
                "[data-value='Search']",
                ".section-result"
            ]
            
            for element_selector in common_elements:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, element_selector)
                    print(f"Found {len(elements)} elements with selector: {element_selector}")
                except:
                    print(f"No elements found with selector: {element_selector}")
        
        # Now test scrolling behavior
        print(f"\n🔄 TESTING SCROLLING BEHAVIOR:")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls and len(all_links) < max_results:
            print(f"\nScroll attempt {scroll_attempts + 1}/{max_scrolls}")
            
            # Count links before scroll
            links_before = len(all_links)
            
            # Try scrolling
            scrollable_selectors = [
                '[role="main"]',
                '.m6QErb',
                '#pane',
                '.siAUzd'
            ]
            
            scrolled = False
            for selector in scrollable_selectors:
                try:
                    results_panel = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
                    print(f"✅ Scrolled using: {selector}")
                    scrolled = True
                    break
                except:
                    continue
            
            if not scrolled:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print("✅ Used fallback page scroll")
            
            time.sleep(5)  # Wait for content to load
            
            # Recount links after scroll
            for selector in link_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/maps/place/' in href:
                            all_links.add(href)
                except:
                    continue
            
            links_after = len(all_links)
            new_links = links_after - links_before
            
            print(f"Links before scroll: {links_before}")
            print(f"Links after scroll: {links_after}")
            print(f"New links found: {new_links}")
            
            if new_links == 0:
                print("⚠️ No new links found - may have reached end of results")
                break
            
            scroll_attempts += 1
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"Total unique links found: {len(all_links)}")
        print(f"Target was: {max_results}")
        
        # Show sample links
        if all_links:
            print(f"\n🔗 Sample links found:")
            for i, link in enumerate(list(all_links)[:5], 1):
                print(f"  {i}. {link[:80]}...")
        else:
            print("❌ No links found at all!")
            
        # Analyze why we might be getting limited results
        print(f"\n🔍 ANALYSIS:")
        if len(all_links) < max_results * 0.3:  # Less than 30% of target
            print("❌ CRITICAL: Very few results found. Possible causes:")
            print("  1. Google Maps is blocking/limiting the scraper")
            print("  2. Search query returns limited results")
            print("  3. Page structure has changed significantly")
            print("  4. Geographic location has limited businesses")
            print("  5. Rate limiting or IP blocking")
        elif len(all_links) < max_results * 0.7:  # Less than 70% of target
            print("⚠️ WARNING: Moderate results found. Possible causes:")
            print("  1. Scrolling not reaching all results")
            print("  2. Some results not loading properly")
            print("  3. Selectors missing some business types")
        else:
            print("✅ Good result count achieved!")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_google_maps_results()
