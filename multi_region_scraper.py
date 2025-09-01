#!/usr/bin/env python3
"""
Multi-Region Google Maps Scraper
Gets 20+ results from a single search by subdividing the search area
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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class MultiRegionGoogleMapsScraper:
    def __init__(self, search_query, target_results=50):
        self.search_query = search_query
        self.target_results = target_results
        self.all_results = []
        self.seen_businesses = set()
        
        # Phone patterns
        self.phone_patterns = [
            re.compile(r'\+?1?[-.]\s?\(?([0-9]{3})\)?[-.]\s?([0-9]{3})[-.]\s?([0-9]{4})'),
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            re.compile(r'\(\d{3}\)\s?\d{3}[-.]?\d{4}'),
            re.compile(r'\d{10}'),
        ]
        
        self.setup_browser()
    
    def setup_browser(self):
        """Setup Chrome browser"""
        print("🔧 Setting up browser for multi-region search...")
        
        self.chrome_options = Options()
        browser_options = [
            "--headless=new",
            "--no-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-images",
            "--window-size=1920,1080",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        for option in browser_options:
            self.chrome_options.add_argument(option)
            
        self.chrome_options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.managed_default_content_settings.images': 2
        })
        
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        print("✅ Browser setup completed")

    def generate_location_variations(self, query):
        """Generate location-based search variations"""
        # Extract city from query
        city_keywords = ['in ', 'near ', 'around ']
        base_query = query
        location = ""
        
        for keyword in city_keywords:
            if keyword in query.lower():
                parts = query.lower().split(keyword)
                if len(parts) > 1:
                    base_query = parts[0].strip()
                    location = parts[1].strip()
                    break
        
        if not location:
            # If no location found, assume the last word is the location
            words = query.split()
            if len(words) > 1:
                base_query = ' '.join(words[:-1])
                location = words[-1]
        
        # Generate variations with different areas/neighborhoods
        variations = [
            f"{base_query} in {location}",
            f"{base_query} near {location}",
            f"{base_query} {location} downtown",
            f"{base_query} {location} center",
            f"{base_query} {location} area",
        ]
        
        # Add specific neighborhood variations if it's a major city
        major_cities = {
            'new york': ['manhattan', 'brooklyn', 'queens', 'bronx'],
            'san francisco': ['downtown', 'mission', 'soma', 'financial district'],
            'los angeles': ['hollywood', 'beverly hills', 'santa monica', 'downtown'],
            'chicago': ['downtown', 'north side', 'south side', 'loop'],
            'miami': ['south beach', 'downtown', 'brickell', 'coral gables']
        }
        
        location_lower = location.lower()
        for city, neighborhoods in major_cities.items():
            if city in location_lower:
                for neighborhood in neighborhoods:
                    variations.append(f"{base_query} in {neighborhood} {location}")
                break
        
        return variations[:6]  # Limit to 6 variations

    def search_and_extract(self, search_query):
        """Search and extract results for a single query"""
        try:
            print(f"🔍 Searching: {search_query}")
            
            # Navigate to Google Maps
            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(8)
            
            # Handle consent
            self._handle_consent()
            
            # Extract business links
            business_links = self._extract_business_links()
            print(f"📋 Found {len(business_links)} links for this search")
            
            # Extract data from each business
            results = []
            for i, link in enumerate(business_links, 1):
                try:
                    business_data = self._extract_business_data(link)
                    if business_data and self._is_unique_business(business_data):
                        results.append(business_data)
                        self.seen_businesses.add(self._get_business_key(business_data))
                        print(f"  ✅ [{i}] {business_data['name']}")
                    else:
                        print(f"  ⚠️ [{i}] Duplicate or invalid business")
                except Exception as e:
                    print(f"  ❌ [{i}] Error: {e}")
                
                # Small delay between extractions
                time.sleep(random.uniform(1, 2))
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed for '{search_query}': {e}")
            return []

    def _handle_consent(self):
        """Handle cookie consent"""
        try:
            consent_selectors = [
                "//button[contains(text(), 'Accept all')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'I agree')]"
            ]
            
            for selector in consent_selectors:
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

    def _extract_business_links(self):
        """Extract business links with aggressive scrolling"""
        all_links = set()
        scroll_attempts = 0
        max_scrolls = 30
        no_new_count = 0
        
        link_selectors = [
            '//a[contains(@href, "/maps/place/")]',
            '//div[@role="article"]//a[contains(@href, "/maps/place/")]'
        ]
        
        while scroll_attempts < max_scrolls and no_new_count < 8:
            # Extract links
            new_links = 0
            for selector in link_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/maps/place/' in href and href not in all_links:
                            all_links.add(href)
                            new_links += 1
                except:
                    continue
            
            if new_links == 0:
                no_new_count += 1
            else:
                no_new_count = 0
            
            # Scroll
            self._scroll_for_more_results()
            time.sleep(random.uniform(2, 4))
            scroll_attempts += 1
        
        return list(all_links)

    def _scroll_for_more_results(self):
        """Scroll to load more results"""
        try:
            # Try multiple scroll methods
            scrollable_selectors = ['[role="main"]', '.m6QErb', '#pane']
            
            for selector in scrollable_selectors:
                try:
                    panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.driver.execute_script("arguments[0].scrollTop += 800", panel)
                    break
                except:
                    continue
            else:
                # Fallback
                self.driver.execute_script("window.scrollBy(0, 800);")
                
        except:
            pass

    def _extract_business_data(self, business_url):
        """Extract data from business page"""
        try:
            self.driver.get(business_url)
            time.sleep(random.uniform(3, 5))
            
            data = {
                'name': self._extract_name(),
                'address': self._extract_address(),
                'phone': self._extract_phone(),
                'website': self._extract_website(),
                'rating': self._extract_rating(),
                'category': self._extract_category(),
                'google_maps_url': business_url,
                'search_query': self.search_query
            }
            
            return data if data['name'] else None
            
        except Exception as e:
            return None

    def _extract_name(self):
        """Extract business name"""
        selectors = ['h1[data-attrid="title"]', 'h1.DUwDvf', 'h1']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                name = element.text.strip()
                if name and len(name) > 1:
                    return name
            except:
                continue
        return None

    def _extract_address(self):
        """Extract address"""
        selectors = ['[data-item-id="address"]', '.Io6YTe.fontBodyMedium']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                address = element.text.strip()
                if address and len(address) > 5:
                    return address
            except:
                continue
        return None

    def _extract_phone(self):
        """Extract phone number"""
        try:
            # Try button selectors first
            phone_selectors = [
                "//button[@data-item-id='phone:tel:']",
                "//button[contains(@data-item-id,'phone')]",
                "//a[starts-with(@href,'tel:')]"
            ]
            
            for selector in phone_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text_sources = [
                            element.get_attribute('aria-label') or '',
                            element.get_attribute('href') or '',
                            element.text or ''
                        ]
                        
                        for text in text_sources:
                            if text:
                                text = text.replace('tel:', '').replace('Phone: ', '')
                                for pattern in self.phone_patterns:
                                    match = pattern.search(text)
                                    if match:
                                        phone = match.group(0)
                                        digits = re.sub(r'\D', '', phone)
                                        if len(digits) >= 10:
                                            return phone
                except:
                    continue
            
            return None
            
        except:
            return None

    def _extract_website(self):
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

    def _extract_rating(self):
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

    def _extract_category(self):
        """Extract category"""
        selectors = ['.DkEaL', 'button[jsaction*="category"]']
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                category = element.text.strip()
                if category and len(category) > 2:
                    return category
            except:
                continue
        return None

    def _get_business_key(self, business_data):
        """Generate unique key for business"""
        name = business_data.get('name', '').lower().strip()
        address = business_data.get('address', '').lower().strip()
        return f"{name}|{address[:50]}"

    def _is_unique_business(self, business_data):
        """Check if business is unique"""
        key = self._get_business_key(business_data)
        return key not in self.seen_businesses

    def run_multi_region_search(self):
        """Main method to run multi-region search"""
        start_time = datetime.now()
        
        print(f"🚀 MULTI-REGION GOOGLE MAPS SEARCH")
        print(f"🔍 Original Query: '{self.search_query}'")
        print(f"🎯 Target: {self.target_results} unique results")
        print("=" * 70)
        
        # Generate search variations
        search_variations = self.generate_location_variations(self.search_query)
        print(f"📍 Generated {len(search_variations)} location variations:")
        for i, variation in enumerate(search_variations, 1):
            print(f"  {i}. {variation}")
        print()
        
        # Search each variation
        for i, search_query in enumerate(search_variations, 1):
            print(f"\n🔍 SEARCH {i}/{len(search_variations)}")
            print("-" * 50)
            
            results = self.search_and_extract(search_query)
            self.all_results.extend(results)
            
            print(f"📊 Search {i} results: {len(results)} new businesses")
            print(f"📈 Total unique businesses: {len(self.all_results)}")
            
            # Check if we've reached target
            if len(self.all_results) >= self.target_results:
                print(f"🎯 Target reached! ({len(self.all_results)} >= {self.target_results})")
                break
            
            # Wait between searches
            if i < len(search_variations):
                wait_time = random.uniform(8, 12)
                print(f"⏳ Waiting {wait_time:.1f}s before next search...")
                time.sleep(wait_time)
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n" + "=" * 70)
        print(f"🎉 MULTI-REGION SEARCH COMPLETED!")
        print(f"⏱️ Duration: {duration}")
        print(f"📊 Total searches: {i}")
        print(f"📋 Unique businesses found: {len(self.all_results)}")
        
        # Count contacts
        contacts = sum(1 for r in self.all_results if r.get('phone') or r.get('website'))
        print(f"📞 Businesses with contact info: {contacts}")
        print(f"📈 Success rate: {(contacts/len(self.all_results)*100):.1f}%" if self.all_results else "0%")
        
        # Show sample results
        if self.all_results:
            print(f"\n📝 SAMPLE RESULTS (first 10):")
            for i, result in enumerate(self.all_results[:10], 1):
                contact_info = []
                if result.get('phone'):
                    contact_info.append(f"📞 {result['phone']}")
                if result.get('website'):
                    contact_info.append("🌐")
                
                contact_str = " | ".join(contact_info) if contact_info else "No contacts"
                print(f"{i:2d}. {result['name']}")
                print(f"    📍 {result.get('address', 'No address')[:60]}...")
                print(f"    {contact_str}")
                if result.get('rating'):
                    print(f"    ⭐ {result['rating']}")
                print()
        
        return self.all_results

    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            print("🧹 Cleanup completed")
        except:
            pass


def multi_region_scrape(query, target_results=50):
    """Convenience function for multi-region scraping"""
    scraper = MultiRegionGoogleMapsScraper(query, target_results)
    try:
        return scraper.run_multi_region_search()
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    # Test the multi-region scraper
    results = multi_region_scrape("restaurants in San Francisco", target_results=30)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"multi_region_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    print(f"🎉 Final count: {len(results)} unique businesses found!")
