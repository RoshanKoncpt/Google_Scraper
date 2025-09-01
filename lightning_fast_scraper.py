#!/usr/bin/env python3
"""
Lightning Fast Google Maps Scraper - 20+ leads in 30-60 seconds
Speed optimizations:
- Minimal delays (0.1-0.3s instead of 1-3s)
- Fast scrolling (50 attempts max)
- Skip detailed extraction during link collection
- Parallel-ready data extraction
- Immediate exit when target reached
"""

import re
import time
import random
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class LightningFastGoogleMapsScraper:
    def __init__(self, search_query, max_results=30):
        self.search_query = search_query
        self.max_results = max_results
        self.extracted_count = 0
        self.contacts_found = 0
        
        self.phone_patterns = [
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            re.compile(r'\(\d{3}\)\s?\d{3}[-.]?\d{4}'),
            re.compile(r'\d{10}'),
        ]
        
        self.setup_browser()
    
    def setup_browser(self):
        """Lightning fast browser setup"""
        print("⚡ Setting up LIGHTNING FAST browser...")

        self.chrome_options = Options()
        
        # Ultra-fast options
        options = [
            "--headless=new",
            "--no-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-images",  # Critical for speed
            "--disable-css",     # Skip CSS loading
            "--disable-javascript",  # Skip JS for faster loading
            "--disable-plugins",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--window-size=1920,1080",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
        
        for option in options:
            self.chrome_options.add_argument(option)

        # Speed-optimized preferences
        self.chrome_options.add_experimental_option('prefs', {
            'profile.managed_default_content_settings.images': 2,
            'profile.default_content_settings.popups': 0,
            'profile.managed_default_content_settings.stylesheets': 2,
            'profile.managed_default_content_settings.cookies': 2,
            'profile.managed_default_content_settings.javascript': 1,
            'profile.managed_default_content_settings.plugins': 2,
            'profile.managed_default_content_settings.geolocation': 2,
            'profile.managed_default_content_settings.media_stream': 2,
        })

        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # Reduced timeout
        print("✅ Lightning fast browser ready")

    def lightning_search_and_extract(self):
        """Lightning fast search with minimal delays"""
        start_time = time.time()
        
        try:
            print(f"⚡ Lightning search: {self.search_query}")
            
            # Direct search URL
            search_url = f"https://www.google.com/maps/search/{self.search_query.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(3)  # Minimal initial wait
            
            # Quick consent handling
            self._quick_consent()
            
            # Lightning fast link extraction
            business_links = self._lightning_extract_links()
            
            elapsed = time.time() - start_time
            print(f"⚡ Found {len(business_links)} links in {elapsed:.1f}s")
            
            return business_links[:self.max_results]
            
        except Exception as e:
            print(f"❌ Lightning search failed: {e}")
            return []

    def _quick_consent(self):
        """Ultra-quick consent handling"""
        try:
            consent_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(@class, 'VfPpkd-LgbsSe')]"
            ]
            
            for selector in consent_selectors:
                try:
                    button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(1)
                    break
                except:
                    continue
        except:
            pass

    def _lightning_extract_links(self):
        """Lightning fast link extraction - optimized for 10+ results"""
        all_links = set()
        scroll_count = 0
        max_scrolls = 80  # Increased to find more results
        patience = 0
        max_patience = 15  # Slightly more patience for 10+ results
        
        # Enhanced selectors for better coverage
        selectors = [
            '//a[contains(@href, "/maps/place/")]',
            '//div[@role="article"]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "Nv2PK")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "bfdHYd")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "lI9IFe")]//a[contains(@href, "/maps/place/")]'
        ]
        
        while scroll_count < max_scrolls and len(all_links) < self.max_results:
            # Quick progress update every 10 scrolls
            if scroll_count % 10 == 0:
                print(f"⚡ Speed scroll {scroll_count}/{max_scrolls} - Found: {len(all_links)}")
            
            # Lightning fast link extraction
            new_count = 0
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            if href and '/maps/place/' in href and href not in all_links:
                                all_links.add(href)
                                new_count += 1
                        except:
                            continue
                except:
                    continue
            
            # Quick exit if target reached
            if len(all_links) >= self.max_results:
                print(f"⚡ Target reached: {len(all_links)} links")
                break
            
            # Speed-optimized patience with recovery strategies
            if new_count == 0:
                patience += 1
                
                # Try recovery strategies when stuck
                if patience == 5:
                    print("⚡ Recovery: Zoom out...")
                    self._quick_zoom_out()
                elif patience == 10:
                    print("⚡ Recovery: Alternative scroll...")
                    self._quick_alternative_scroll()
                
                if patience >= max_patience:
                    print(f"⚡ Speed exit after {patience} attempts")
                    break
            else:
                patience = 0
            
            # Lightning fast scrolling
            self._lightning_scroll()
            
            # Minimal delay - critical for speed
            time.sleep(0.1)  # Ultra-fast delay
            scroll_count += 1
        
        return list(all_links)

    def _lightning_scroll(self):
        """Lightning fast scrolling - enhanced for more results"""
        try:
            # Method 1: Multiple panel scrolls for better coverage
            panel_selectors = ['[role="main"]', '.m6QErb', '#pane']
            scrolled = False
            
            for selector in panel_selectors:
                try:
                    panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                    # Double scroll for more results
                    self.driver.execute_script("arguments[0].scrollTop += 1200", panel)
                    time.sleep(0.05)
                    self.driver.execute_script("arguments[0].scrollTop += 800", panel)
                    scrolled = True
                    break
                except:
                    continue
            
            # Method 2: Fallback page scroll
            if not scrolled:
                self.driver.execute_script("window.scrollBy(0, 1500);")
                time.sleep(0.05)
                self.driver.execute_script("window.scrollBy(0, 800);")
            
        except:
            pass

    def lightning_extract_data(self, business_url):
        """Lightning fast data extraction - minimal fields"""
        try:
            self.driver.get(business_url)
            time.sleep(1.5)  # Minimal wait
            
            # Extract only essential data quickly
            data = {
                'name': self._quick_get_name(),
                'mobile': self._quick_get_phone(),
                'address': self._quick_get_address(),
                'google_maps_url': business_url,
                'search_query': self.search_query
            }

            self.extracted_count += 1
            if data.get('mobile'):
                self.contacts_found += 1

            # Quick status
            status = f"⚡ {data['name']}"
            if data.get('mobile'):
                status += f" 📞"
            print(status)
            
            return data

        except Exception as e:
            return None

    def _quick_get_name(self):
        """Quick name extraction"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, 'h1')
            name = element.text.strip()
            return name if name else 'Unknown'
        except:
            return 'Unknown'
    
    def _quick_zoom_out(self):
        """Quick zoom out recovery"""
        try:
            zoom_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Zoom out']")
            zoom_button.click()
            zoom_button.click()  # Double click
            time.sleep(0.5)
        except:
            # Keyboard fallback
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.CONTROL, "-")
                body.send_keys(Keys.CONTROL, "-")
            except:
                pass
    
    def _quick_alternative_scroll(self):
        """Quick alternative scrolling"""
        try:
            # Try clicking show more buttons
            show_more_selectors = [
                "//button[contains(text(), 'Show more')]",
                "//button[contains(text(), 'More results')]"
            ]
            
            for selector in show_more_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        button.click()
                        time.sleep(0.5)
                except:
                    continue
            
            # Aggressive keyboard scroll
            body = self.driver.find_element(By.TAG_NAME, "body")
            for _ in range(5):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.1)
        except:
            pass

    def _quick_get_phone(self):
        """Quick phone extraction"""
        try:
            # Direct phone button
            phone_element = self.driver.find_element(By.XPATH, "//button[contains(@data-item-id,'phone')]")
            aria_label = phone_element.get_attribute('aria-label') or ''
            
            for pattern in self.phone_patterns:
                match = pattern.search(aria_label)
                if match:
                    return match.group(0)
            
            return None
        except:
            return None

    def _quick_get_address(self):
        """Quick address extraction"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]')
            address = element.text.strip()
            return address if len(address) > 5 else 'Address not found'
        except:
            return 'Address not found'

    def run_lightning_scraping(self):
        """Lightning fast main process - target 30-60 seconds"""
        start_time = datetime.now()
        results = []

        try:
            print(f"⚡ LIGHTNING FAST GOOGLE MAPS SCRAPING")
            print(f"🔍 Query: '{self.search_query}'")
            print(f"🎯 Target: {self.max_results} leads in 30-60 seconds")
            print("=" * 60)

            # Phase 1: Lightning link extraction (15-30 seconds)
            phase1_start = time.time()
            business_links = self.lightning_search_and_extract()
            phase1_time = time.time() - phase1_start
            
            if not business_links:
                print("❌ No links found")
                return []

            print(f"⚡ Phase 1 complete: {len(business_links)} links in {phase1_time:.1f}s")

            # Phase 2: Lightning data extraction (15-30 seconds)
            print(f"\n⚡ LIGHTNING DATA EXTRACTION")
            print("=" * 60)

            phase2_start = time.time()
            for i, link in enumerate(business_links, 1):
                if i % 5 == 0:  # Progress every 5 items
                    elapsed = time.time() - phase2_start
                    print(f"⚡ Progress: {i}/{len(business_links)} in {elapsed:.1f}s")

                try:
                    business_data = self.lightning_extract_data(link)
                    if business_data:
                        results.append(business_data)
                except:
                    pass

                # Minimal delay for speed
                time.sleep(0.2)

            # Final summary
            end_time = datetime.now()
            total_duration = end_time - start_time
            total_seconds = total_duration.total_seconds()

            print(f"\n" + "=" * 60)
            print(f"⚡ LIGHTNING SCRAPING COMPLETED!")
            print(f"⏱️ Total time: {total_seconds:.1f} seconds")
            print(f"📊 Businesses found: {len(results)}")
            print(f"📞 Contacts found: {self.contacts_found}")
            print(f"⚡ Speed: {len(results)/total_seconds*60:.1f} leads/minute")
            
            # Speed check
            if total_seconds <= 60:
                print(f"🎉 SUCCESS! Completed in {total_seconds:.1f}s (target: 30-60s)")
            else:
                print(f"⚠️ Took {total_seconds:.1f}s (target: 30-60s)")

            return results

        except Exception as e:
            print(f"❌ Critical error: {e}")
            return []
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Quick cleanup"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except:
            pass


def lightning_scrape_google_maps(query, max_results=30):
    """Lightning fast scraping - 30-60 seconds"""
    scraper = LightningFastGoogleMapsScraper(query, max_results)
    return scraper.run_lightning_scraping()


if __name__ == "__main__":
    # Test lightning speed
    start_test = time.time()
    results = lightning_scrape_google_maps("restaurants in New York", max_results=25)
    test_duration = time.time() - start_test
    
    print(f"\n⚡ LIGHTNING TEST RESULTS")
    print(f"📊 Found: {len(results)} businesses")
    print(f"⏱️ Time: {test_duration:.1f} seconds")
    print(f"🎯 Target met: {'✅' if test_duration <= 60 and len(results) >= 20 else '❌'}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lightning_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    
    # Show sample results
    for i, result in enumerate(results[:10], 1):
        phone = f" 📞 {result['mobile']}" if result.get('mobile') else ""
        print(f"{i}. {result['name']}{phone}")
