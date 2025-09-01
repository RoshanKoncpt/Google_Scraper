#!/usr/bin/env python3
"""
Alternative approach to get more Google Maps results using different strategies
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

class AlternativeGoogleMapsScraper:
    def __init__(self, search_query, max_results=50):
        self.search_query = search_query
        self.max_results = max_results
        self.setup_browser()
    
    def setup_browser(self):
        """Setup browser using the same method as the working scraper"""
        # Use the same Chrome setup that works in google_maps_scraper.py
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
        
        # Enhanced anti-detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use the same Chrome driver setup as the working scraper
        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"Chrome setup failed: {e}")
            # Fallback to basic setup
            basic_options = Options()
            basic_options.add_argument("--headless=new")
            basic_options.add_argument("--no-sandbox")
            basic_options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=basic_options)
    
    def try_alternative_urls(self):
        """Try different Google Maps URL formats"""
        
        base_queries = [
            self.search_query,
            self.search_query.replace(" in ", " "),
            self.search_query.split(" in ")[0] if " in " in self.search_query else self.search_query,
        ]
        
        url_formats = [
            "https://www.google.com/maps/search/{}",
            "https://maps.google.com/maps?q={}",
            "https://www.google.com/maps?q={}",
        ]
        
        all_links = set()
        
        for query in base_queries:
            for url_format in url_formats:
                try:
                    search_url = url_format.format(query.replace(' ', '+'))
                    print(f"🔍 Trying: {search_url}")
                    
                    self.driver.get(search_url)
                    time.sleep(random.uniform(5, 8))
                    
                    # Extract links with this approach
                    links = self.extract_business_links()
                    all_links.update(links)
                    
                    print(f"Found {len(links)} new links, total: {len(all_links)}")
                    
                    if len(all_links) >= self.max_results:
                        break
                        
                    # Random delay between attempts
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    print(f"URL attempt failed: {e}")
                    continue
            
            if len(all_links) >= self.max_results:
                break
        
        return list(all_links)[:self.max_results]
    
    def extract_business_links(self):
        """Extract business links with multiple strategies"""
        links = set()
        
        # Strategy 1: Immediate extraction
        link_selectors = [
            "//a[contains(@href, '/maps/place/')]",
            "//div[@role='article']//a",
            "//div[contains(@class, 'Nv2PK')]//a",
            "//div[contains(@jsaction, 'mouseover')]//a"
        ]
        
        for selector in link_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    href = elem.get_attribute('href')
                    if href and '/maps/place/' in href:
                        links.add(href)
            except:
                continue
        
        # Strategy 2: Aggressive scrolling with shorter intervals
        scroll_count = 0
        max_scrolls = 30
        no_new_links_count = 0
        
        while scroll_count < max_scrolls and len(links) < self.max_results:
            initial_count = len(links)
            
            # Multiple scroll methods
            try:
                # Method 1: Scroll results panel
                results_panel = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
                self.driver.execute_script("arguments[0].scrollTop += 800", results_panel)
                time.sleep(1)
                
                # Method 2: Page scroll
                self.driver.execute_script("window.scrollBy(0, 600)")
                time.sleep(1)
                
                # Method 3: End of page scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                
            except:
                self.driver.execute_script("window.scrollBy(0, 800)")
                time.sleep(2)
            
            # Re-extract links
            for selector in link_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        href = elem.get_attribute('href')
                        if href and '/maps/place/' in href:
                            links.add(href)
                except:
                    continue
            
            new_links = len(links) - initial_count
            if new_links == 0:
                no_new_links_count += 1
                if no_new_links_count >= 8:  # More patience
                    print(f"No new links after 8 attempts, stopping at {len(links)} links")
                    break
            else:
                no_new_links_count = 0
            
            scroll_count += 1
            print(f"Scroll {scroll_count}: {len(links)} total links (+{new_links})")
        
        return links
    
    def scrape(self):
        """Main scraping method"""
        try:
            print(f"🚀 Alternative scraper starting...")
            print(f"🔍 Query: {self.search_query}")
            print(f"🎯 Target: {self.max_results} results")
            
            business_links = self.try_alternative_urls()
            
            print(f"📊 Found {len(business_links)} business links")
            
            # Extract basic data from each business
            results = []
            for i, link in enumerate(business_links, 1):
                try:
                    print(f"Processing business {i}/{len(business_links)}")
                    self.driver.get(link)
                    time.sleep(random.uniform(2, 4))
                    
                    # Extract basic info
                    business_data = {
                        'name': self.extract_name(),
                        'address': self.extract_address(),
                        'phone': self.extract_phone(),
                        'rating': self.extract_rating(),
                        'url': link
                    }
                    
                    if business_data['name']:
                        results.append(business_data)
                    
                except Exception as e:
                    print(f"Error processing business {i}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Alternative scraper failed: {e}")
            return []
        finally:
            self.driver.quit()
    
    def extract_name(self):
        """Extract business name"""
        selectors = ['h1', '.DUwDvf', '[data-attrid="title"]']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                name = element.text.strip()
                if name and len(name) > 1:
                    return name
            except:
                continue
        return "Unknown Business"
    
    def extract_address(self):
        """Extract address"""
        selectors = [
            '[data-item-id="address"]',
            '.Io6YTe.fontBodyMedium',
            'button[data-item-id="address"]'
        ]
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                address = element.text.strip()
                if address and len(address) > 5:
                    return address
            except:
                continue
        return "Address not found"
    
    def extract_phone(self):
        """Extract phone number"""
        phone_patterns = [
            re.compile(r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'),
            re.compile(r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'),
            re.compile(r'\+1\s*\d{3}[-.\s]\d{3}[-.\s]\d{4}'),
        ]
        
        selectors = [
            "//button[contains(@data-item-id,'phone')]",
            "//a[contains(@href,'tel:')]",
            "//button[contains(@aria-label,'Phone')]"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    text_sources = [
                        element.get_attribute('aria-label') or '',
                        element.get_attribute('href') or '',
                        element.text or ''
                    ]
                    
                    for text in text_sources:
                        text = text.replace('tel:', '').replace('Phone: ', '')
                        for pattern in phone_patterns:
                            match = pattern.search(text)
                            if match:
                                return match.group(0)
            except:
                continue
        
        return None
    
    def extract_rating(self):
        """Extract rating"""
        selectors = ['.F7nice span', '.ceNzKf', 'span[aria-hidden="true"]']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                rating_text = element.text.strip()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    return float(rating_match.group(1))
            except:
                continue
        return None

def test_alternative_scraper():
    """Test the alternative scraper"""
    queries = [
        "restaurants Chicago",
        "coffee shops Seattle", 
        "hotels Miami"
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Testing: {query}")
        print(f"{'='*50}")
        
        scraper = AlternativeGoogleMapsScraper(query, max_results=20)
        results = scraper.scrape()
        
        print(f"\nResults: {len(results)} businesses found")
        for i, business in enumerate(results[:5], 1):
            print(f"{i}. {business['name']}")
            print(f"   📞 {business['phone'] or 'No phone'}")
            print(f"   ⭐ {business['rating'] or 'No rating'}")

if __name__ == "__main__":
    test_alternative_scraper()
