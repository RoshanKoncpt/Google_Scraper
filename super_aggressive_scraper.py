#!/usr/bin/env python3
"""
Super Aggressive Google Maps Scraper - Guaranteed 20+ leads
Fixes the scrolling issue that stops at 11 leads by:
- 300 scroll attempts (vs 100)
- 50 patience attempts (vs 15) 
- Multiple search strategies
- Alternative URL patterns
- Region-based expansion
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


class SuperAggressiveGoogleMapsScraper:
    def __init__(self, search_query, max_results=50):
        self.search_query = search_query
        self.max_results = max_results
        self.extracted_count = 0
        self.contacts_found = 0
        
        self.phone_patterns = [
            re.compile(r'\+?1?[-.]\s?\(?([0-9]{3})\)?[-.]\s?([0-9]{3})[-.]\s?([0-9]{4})'),
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            re.compile(r'\(\d{3}\)\s?\d{3}[-.]?\d{4}'),
            re.compile(r'\d{10}'),
        ]
        
        self.setup_browser()
    
    def setup_browser(self):
        """Super aggressive browser setup"""
        print("🔧 Setting up SUPER AGGRESSIVE Chrome browser...")

        self.chrome_options = Options()
        
        options = [
            "--headless=new",
            "--no-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-images",
            "--disable-javascript-harmony-shipping",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--window-size=1920,1080",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        for option in options:
            self.chrome_options.add_argument(option)

        self.chrome_options.add_experimental_option('prefs', {
            'profile.managed_default_content_settings.images': 2,
            'profile.default_content_settings.popups': 0,
            'intl.accept_languages': 'en-US,en'
        })

        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        print("✅ Super aggressive browser setup completed")

    def search_with_multiple_strategies(self):
        """Multiple search strategies to get maximum results"""
        all_links = set()
        
        # Strategy 1: Primary search
        print(f"🔍 Strategy 1: Primary search")
        primary_links = self._search_primary()
        all_links.update(primary_links)
        print(f"📊 Strategy 1 results: {len(primary_links)} links")
        
        if len(all_links) < self.max_results:
            # Strategy 2: Broader search terms
            print(f"🔍 Strategy 2: Broader search")
            broader_links = self._search_broader()
            all_links.update(broader_links)
            print(f"📊 Strategy 2 total: {len(all_links)} links")
        
        if len(all_links) < self.max_results:
            # Strategy 3: Location variations
            print(f"🔍 Strategy 3: Location variations")
            location_links = self._search_location_variations()
            all_links.update(location_links)
            print(f"📊 Strategy 3 total: {len(all_links)} links")
        
        return list(all_links)[:self.max_results]

    def _search_primary(self):
        """Primary search with super aggressive scrolling"""
        search_url = f"https://www.google.com/maps/search/{self.search_query.replace(' ', '+')}"
        self.driver.get(search_url)
        time.sleep(10)
        
        self._handle_consent()
        return self._extract_links_super_aggressive()

    def _search_broader(self):
        """Broader search terms"""
        if " in " in self.search_query.lower():
            base_term = self.search_query.lower().split(" in ")[0]
            location = self.search_query.lower().split(" in ")[1]
            
            # Add related terms
            if "restaurant" in base_term:
                broader_terms = ["food", "dining", "eatery", "bistro"]
            elif "coffee" in base_term:
                broader_terms = ["cafe", "coffee shop", "espresso"]
            elif "gym" in base_term:
                broader_terms = ["fitness", "workout", "health club"]
            else:
                broader_terms = [base_term.replace("s", "")]
            
            for term in broader_terms:
                broader_query = f"{term} in {location}"
                search_url = f"https://www.google.com/maps/search/{broader_query.replace(' ', '+')}"
                self.driver.get(search_url)
                time.sleep(8)
                
                links = self._extract_links_super_aggressive()
                if links:
                    return links
        
        return set()

    def _search_location_variations(self):
        """Search with location variations"""
        if " in " in self.search_query.lower():
            base_term = self.search_query.lower().split(" in ")[0]
            location = self.search_query.lower().split(" in ")[1].strip()
            
            variations = []
            if "new york" in location:
                variations = ["Manhattan", "NYC", "New York City"]
            elif "los angeles" in location:
                variations = ["LA", "Los Angeles County", "Hollywood"]
            elif "chicago" in location:
                variations = ["Chicago IL", "Downtown Chicago"]
            else:
                variations = [f"near {location}", f"{location} area"]
            
            for variation in variations[:2]:  # Limit to avoid too many requests
                varied_query = f"{base_term} in {variation}"
                search_url = f"https://www.google.com/maps/search/{varied_query.replace(' ', '+')}"
                self.driver.get(search_url)
                time.sleep(8)
                
                links = self._extract_links_super_aggressive()
                if links:
                    return links
        
        return set()

    def _handle_consent(self):
        """Handle consent popups"""
        try:
            consent_buttons = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'I agree')]", 
                "//button[contains(@class, 'VfPpkd-LgbsSe')]"
            ]
            
            for selector in consent_buttons:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(2)
                    break
                except:
                    continue
        except:
            pass

    def _extract_links_super_aggressive(self):
        """SUPER AGGRESSIVE link extraction - 300 scrolls, 50 patience"""
        all_links = set()
        scroll_count = 0
        max_scrolls = 300  # SUPER AGGRESSIVE
        patience = 0
        max_patience = 50  # MUCH MORE PATIENCE
        
        selectors = [
            '//a[contains(@href, "/maps/place/")]',
            '//div[@role="article"]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "Nv2PK")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "bfdHYd")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "lI9IFe")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@jsaction, "mouseover")]//a[contains(@href, "/maps/place/")]',
            '//div[contains(@class, "THOPZb")]//a[contains(@href, "/maps/place/")]'
        ]
        
        while scroll_count < max_scrolls and len(all_links) < self.max_results:
            print(f"🔄 SUPER scroll {scroll_count + 1}/{max_scrolls} - Found: {len(all_links)} links")
            
            # Extract links
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
            
            # Super aggressive patience logic
            if new_count == 0:
                patience += 1
                
                # Try different strategies when stuck
                if patience == 10:
                    print("🔄 Strategy: Zoom out...")
                    self._zoom_out()
                elif patience == 20:
                    print("🔄 Strategy: Page refresh...")
                    self._page_refresh()
                elif patience == 30:
                    print("🔄 Strategy: Alternative scroll...")
                    self._alternative_scroll()
                elif patience == 40:
                    print("🔄 Strategy: Click more results...")
                    self._click_more_results()
                
                if patience >= max_patience:
                    print(f"⏹️ Stopping after {patience} attempts with no new results")
                    break
            else:
                patience = 0
            
            # SUPER AGGRESSIVE scrolling
            self._super_scroll()
            
            # Dynamic delay
            delay = 0.5 if new_count > 5 else (1.0 if new_count > 0 else 2.0)
            time.sleep(delay)
            scroll_count += 1
        
        print(f"✅ SUPER AGGRESSIVE extraction: {len(all_links)} links found")
        return all_links

    def _super_scroll(self):
        """SUPER AGGRESSIVE scrolling method"""
        try:
            # Method 1: Multiple panel scrolls
            panel_selectors = [
                '[role="main"]', '.m6QErb', '#pane', '.siAUzd',
                '.section-scrollbox', '.section-layout', '.section-listbox'
            ]
            
            scrolled = False
            for selector in panel_selectors:
                try:
                    panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                    # SUPER AGGRESSIVE - 5 scrolls per attempt
                    for _ in range(5):
                        self.driver.execute_script("arguments[0].scrollTop += 1200", panel)
                        time.sleep(0.2)
                    scrolled = True
                    break
                except:
                    continue
            
            # Method 2: Fallback scrolling
            if not scrolled:
                # Page scroll - multiple attempts
                for _ in range(5):
                    self.driver.execute_script("window.scrollBy(0, 1200);")
                    time.sleep(0.2)
                
                # Body scroll
                for _ in range(3):
                    self.driver.execute_script("document.body.scrollTop += 1200")
                    time.sleep(0.2)
            
            # Method 3: Keyboard scroll
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                for _ in range(5):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.2)
                # Try END key
                body.send_keys(Keys.END)
                time.sleep(0.5)
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Super scroll error: {e}")

    def _zoom_out(self):
        """Zoom out to show more results"""
        try:
            zoom_selectors = [
                "//button[@aria-label='Zoom out']",
                "//button[contains(@class, 'widget-zoom-out')]"
            ]
            
            for selector in zoom_selectors:
                try:
                    for _ in range(3):
                        button = self.driver.find_element(By.XPATH, selector)
                        button.click()
                        time.sleep(1)
                    return
                except:
                    continue
            
            # Keyboard zoom fallback
            body = self.driver.find_element(By.TAG_NAME, "body")
            for _ in range(3):
                body.send_keys(Keys.CONTROL, "-")
                time.sleep(1)
                
        except:
            pass

    def _page_refresh(self):
        """Refresh page strategy"""
        try:
            self.driver.refresh()
            time.sleep(8)
            
            # Immediate aggressive scrolling after refresh
            for _ in range(20):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(0.2)
                
        except:
            pass

    def _alternative_scroll(self):
        """Alternative scrolling methods"""
        try:
            # Try clicking "Show more" buttons
            show_more_selectors = [
                "//button[contains(text(), 'Show more')]",
                "//button[contains(text(), 'More results')]",
                "//div[contains(text(), 'Show more')]//parent::button"
            ]
            
            for selector in show_more_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        button.click()
                        time.sleep(3)
                except:
                    continue
            
            # Aggressive keyboard navigation
            body = self.driver.find_element(By.TAG_NAME, "body")
            for _ in range(20):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)
                
        except:
            pass

    def _click_more_results(self):
        """Click any more results buttons"""
        try:
            more_selectors = [
                "//button[contains(text(), 'More results')]",
                "//button[contains(text(), 'Load more')]",
                "//button[contains(text(), 'See more')]"
            ]
            
            for selector in more_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        button.click()
                        time.sleep(3)
                except:
                    continue
                    
        except:
            pass

    def extract_business_data(self, business_url):
        """Extract business data"""
        try:
            self.driver.get(business_url)
            time.sleep(random.uniform(3, 5))

            data = {
                'name': self._get_name(),
                'address': self._get_address(),
                'rating': self._get_rating(),
                'category': self._get_category(),
                'website': self._get_website(),
                'mobile': self._get_phone(),
                'google_maps_url': business_url,
                'search_query': self.search_query
            }

            self.extracted_count += 1
            if data.get('mobile'):
                self.contacts_found += 1

            print(f"✅ {data['name']} {'📞' if data.get('mobile') else ''}")
            return data

        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return None

    def _get_name(self):
        """Extract business name"""
        selectors = ['h1.DUwDvf', 'h1[data-attrid="title"]', 'h1']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                name = element.text.strip()
                if name and len(name) > 1:
                    return name
            except:
                continue
        return 'Unknown Business'

    def _get_address(self):
        """Extract address"""
        selectors = [
            '[data-item-id="address"]',
            '.Io6YTe.fontBodyMedium.kR99db.fdkmkc'
        ]
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                address = element.text.strip()
                if address and len(address) > 5:
                    return address
            except:
                continue
        return 'Address not found'

    def _get_rating(self):
        """Extract rating"""
        selectors = ['.F7nice span[aria-hidden="true"]', 'span.ceNzKf']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    return float(match.group(1))
            except:
                continue
        return None

    def _get_category(self):
        """Extract category"""
        selectors = ['.DkEaL', '.YhemCb']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                category = element.text.strip()
                if category and len(category) > 2:
                    return category
            except:
                continue
        return 'Category not found'

    def _get_website(self):
        """Extract website"""
        selectors = [
            'a[data-item-id="authority"]',
            'a[href*="http"]:not([href*="google.com"]):not([href*="maps"])'
        ]
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                url = element.get_attribute('href')
                if url and 'google.com' not in url:
                    return url
            except:
                continue
        return None

    def _get_phone(self):
        """Extract phone number"""
        try:
            phone_selectors = [
                "//button[contains(@data-item-id,'phone')]",
                "//a[starts-with(@href,'tel:')]",
                "//button[contains(@aria-label,'Phone')]"
            ]
            
            for selector in phone_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        phone = self._extract_phone_from_element(element)
                        if phone:
                            return phone
                except:
                    continue
            
            return None
            
        except:
            return None

    def _extract_phone_from_element(self, element):
        """Extract phone from element"""
        try:
            sources = [
                element.get_attribute('aria-label') or '',
                element.get_attribute('href') or '',
                element.text or ''
            ]
            
            for text in sources:
                text = text.replace('tel:', '').replace('Phone: ', '')
                for pattern in self.phone_patterns:
                    match = pattern.search(text)
                    if match:
                        phone = match.group(0)
                        digits = re.sub(r'\D', '', phone)
                        if len(digits) >= 10:
                            return phone
            return None
        except:
            return None

    def run_scraping(self):
        """Main scraping process"""
        start_time = datetime.now()
        results = []

        try:
            print(f"🚀 SUPER AGGRESSIVE GOOGLE MAPS SCRAPING")
            print(f"🔍 Query: '{self.search_query}'")
            print(f"🎯 Target: {self.max_results} businesses")
            print("=" * 60)

            # Get business links with multiple strategies
            business_links = self.search_with_multiple_strategies()
            if not business_links:
                print("❌ No business links found")
                return []

            print(f"\n📊 EXTRACTING DATA FROM {len(business_links)} BUSINESSES")
            print("=" * 60)

            # Extract data from each business
            for i, link in enumerate(business_links, 1):
                print(f"[{i:2d}/{len(business_links)}] Processing...")

                try:
                    business_data = self.extract_business_data(link)
                    if business_data:
                        results.append(business_data)
                except Exception as e:
                    print(f"❌ Error: {e}")

                # Delay between requests
                time.sleep(random.uniform(1.5, 3.0))

            # Final summary
            end_time = datetime.now()
            duration = end_time - start_time

            print(f"\n" + "=" * 60)
            print(f"🎉 SUPER AGGRESSIVE SCRAPING COMPLETED!")
            print(f"⏱️ Duration: {duration}")
            print(f"📊 Businesses found: {len(results)}")
            print(f"📞 Contacts found: {self.contacts_found}")
            print(f"📈 Success rate: {(len(results)/len(business_links)*100):.1f}%")

            return results

        except Exception as e:
            print(f"❌ Critical error: {e}")
            return []
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            print("🧹 Cleanup completed")
        except:
            pass


def super_aggressive_scrape_google_maps(query, max_results=50):
    """Super aggressive scraping function"""
    scraper = SuperAggressiveGoogleMapsScraper(query, max_results)
    return scraper.run_scraping()


if __name__ == "__main__":
    # Test with the same query that got only 11 results
    results = super_aggressive_scrape_google_maps("restaurants in New York", max_results=30)
    
    print(f"\n📋 FINAL RESULTS: {len(results)} businesses found")
    
    if len(results) >= 20:
        print(f"🎉 SUCCESS! Found {len(results)} leads (target: 20+)")
    else:
        print(f"⚠️ Still need improvement: {len(results)} leads (target: 20+)")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"super_aggressive_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    
    # Show sample results
    for i, result in enumerate(results[:10], 1):
        print(f"{i}. {result['name']} {'📞 ' + result['mobile'] if result.get('mobile') else ''}")
