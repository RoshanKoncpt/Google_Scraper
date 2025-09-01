import time
import random
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class RailwayOptimizedScraper:
    def __init__(self, search_query, max_results=100, visit_websites=True):
        self.search_query = search_query
        self.max_results = max_results
        self.visit_websites = visit_websites
        self.driver = None
        self.wait = None
        self.contacts_found = 0
        
        # Email patterns for extraction
        self.email_patterns = [
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            re.compile(r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b'),
        ]
        
        # Phone patterns for extraction
        self.phone_patterns = [
            re.compile(r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'),
            re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        ]
        
        self.setup_browser()
    
    def setup_browser(self):
        """Railway-optimized browser setup with maximum anti-detection"""
        print("🚀 Setting up Railway-optimized browser...")

        self.chrome_options = Options()
        
        # Core Railway compatibility options
        core_options = [
            "--headless=new",
            "--no-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--single-process",
            "--no-zygote"
        ]
        
        # Anti-detection options
        stealth_options = [
            "--disable-blink-features=AutomationControlled",
            "--exclude-switches=enable-automation",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--window-size=1920,1080",
            "--lang=en-US",
            "--accept-lang=en-US,en"
        ]
        
        # Performance options
        performance_options = [
            "--disable-extensions",
            "--disable-plugins", 
            "--disable-images",
            "--disable-javascript-harmony-shipping",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-ipc-flooding-protection",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate",
            "--disable-background-networking",
            "--disable-sync",
            "--metrics-recording-only",
            "--no-crash-upload",
            "--disable-logging",
            "--disable-notifications"
        ]
        
        all_options = core_options + stealth_options + performance_options
        for option in all_options:
            self.chrome_options.add_argument(option)

        # Anti-detection preferences
        self.chrome_options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-US,en',
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
            'profile.managed_default_content_settings.images': 2
        })
        
        # Remove automation indicators
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # Execute anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Railway-optimized browser ready")
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            raise

    def search_google_maps(self):
        """Multi-strategy Google Maps access for Railway"""
        try:
            print(f"🔍 Searching for: {self.search_query}")
            
            # Strategy 1: Direct search URL
            search_url = f"https://www.google.com/maps/search/{self.search_query.replace(' ', '+')}"
            print(f"🌐 Direct URL: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(10)
            
            # Check for blocking
            if self._is_blocked():
                print("⚠️ Direct access blocked, trying alternative...")
                return self._fallback_search()
            
            self._handle_consent()
            self._wait_for_results()
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def _is_blocked(self):
        """Check if Google is blocking access"""
        title = self.driver.title.lower()
        url = self.driver.current_url.lower()
        
        blocking_indicators = ['sorry', 'blocked', 'captcha', 'unusual traffic', 'robot']
        
        for indicator in blocking_indicators:
            if indicator in title or indicator in url:
                return True
                
        # Check page source for blocking content
        try:
            page_source = self.driver.page_source[:1000].lower()
            if any(indicator in page_source for indicator in blocking_indicators):
                return True
        except:
            pass
            
        return False
    
    def _fallback_search(self):
        """Fallback search strategy"""
        try:
            print("🔄 Using fallback search strategy...")
            
            # Go to Google first
            self.driver.get("https://www.google.com")
            time.sleep(5)
            
            # Accept cookies
            self._handle_consent()
            
            # Navigate to Maps
            self.driver.get("https://www.google.com/maps")
            time.sleep(8)
            
            # Use search box
            try:
                search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "searchboxinput")))
                search_box.clear()
                search_box.send_keys(self.search_query)
                search_box.send_keys(Keys.RETURN)
                time.sleep(10)
                
                self._wait_for_results()
                return True
                
            except Exception as e:
                print(f"❌ Fallback search failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Fallback strategy failed: {e}")
            return False
    
    def _handle_consent(self):
        """Handle consent and cookie dialogs"""
        try:
            consent_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'I agree')]", 
                "//button[contains(text(), 'Accept all')]",
                "//button[@id='L2AGLb']",
                "//div[contains(text(), 'Accept')]",
                "//span[contains(text(), 'Accept')]"
            ]
            
            for selector in consent_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    if button.is_displayed():
                        button.click()
                        time.sleep(2)
                        print("✅ Consent handled")
                        return
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Consent handling: {e}")
    
    def _wait_for_results(self):
        """Wait for search results to load"""
        print("⏳ Waiting for results...")
        
        result_selectors = [
            "//div[contains(@class, 'Nv2PK')]",
            "//div[@role='article']",
            "//a[contains(@href, '/maps/place/')]",
            "//div[contains(@class, 'bfdHYd')]",
            "//div[contains(@class, 'lI9IFe')]"
        ]
        
        for attempt in range(30):
            for selector in result_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if len(elements) > 0:
                        print(f"✅ Found {len(elements)} result elements")
                        return True
                except:
                    continue
            time.sleep(1)
            
        print("⚠️ No results found, continuing anyway...")
        return True

    def get_business_links(self):
        """Extract business links with Railway optimization"""
        try:
            print("🔗 Extracting business links...")
            all_links = set()
            
            # Debug current state
            print(f"📍 Current URL: {self.driver.current_url}")
            print(f"📄 Page title: {self.driver.title}")
            
            if self._is_blocked():
                print("❌ Page is blocked")
                return []
            
            # Enhanced link selectors
            link_selectors = [
                '//a[contains(@href, "/maps/place/")]',
                '//div[@role="article"]//a[contains(@href, "/maps/place/")]',
                '//div[contains(@class, "Nv2PK")]//a[contains(@href, "/maps/place/")]',
                '//div[contains(@class, "bfdHYd")]//a[contains(@href, "/maps/place/")]',
                '//div[contains(@class, "lI9IFe")]//a[contains(@href, "/maps/place/")]',
                '//div[contains(@jsaction, "click")]//a[contains(@href, "/maps/place/")]',
                '//div[contains(@class, "THOPZb")]//a[contains(@href, "/maps/place/")]'
            ]
            
            max_scrolls = 50
            scroll_attempts = 0
            no_new_links_count = 0
            
            while scroll_attempts < max_scrolls and len(all_links) < self.max_results:
                scroll_attempts += 1
                initial_count = len(all_links)
                
                # Extract links using all selectors
                for selector in link_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            href = element.get_attribute('href')
                            if href and '/maps/place/' in href and href not in all_links:
                                all_links.add(href)
                    except:
                        continue
                
                new_links = len(all_links) - initial_count
                print(f"🔄 Scroll {scroll_attempts}/{max_scrolls}: {len(all_links)} total links (+{new_links} new)")
                
                if new_links == 0:
                    no_new_links_count += 1
                    if no_new_links_count >= 5:
                        print("⏹️ No new links found, stopping")
                        break
                else:
                    no_new_links_count = 0
                
                # Scroll strategies
                if scroll_attempts % 10 == 0:
                    # Page scroll
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                else:
                    # Panel scroll
                    try:
                        panel = self.driver.find_element(By.XPATH, "//div[contains(@class, 'm6QErb')]")
                        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
                    except:
                        self.driver.execute_script("window.scrollBy(0, 500);")
                
                time.sleep(random.uniform(0.5, 1.5))
            
            print(f"✅ Extraction complete: {len(all_links)} business links")
            return list(all_links)
            
        except Exception as e:
            print(f"❌ Link extraction failed: {e}")
            return []

    def extract_business_data(self, business_url):
        """Extract business data from individual business page"""
        try:
            self.driver.get(business_url)
            time.sleep(random.uniform(2, 4))
            
            business_data = {
                'name': 'Unknown Business',
                'address': '',
                'rating': None,
                'review_count': None,
                'category': '',
                'website': '',
                'mobile': '',
                'email': '',
                'secondary_email': '',
                'google_maps_url': business_url,
                'website_visited': False,
                'additional_contacts': ''
            }
            
            # Extract name
            name_selectors = [
                "//h1[contains(@class, 'DUwDvf')]",
                "//h1[@data-attrid='title']",
                "//h1[contains(@class, 'x3AX1-LfntMc-header-title-title')]"
            ]
            
            for selector in name_selectors:
                try:
                    name_element = self.driver.find_element(By.XPATH, selector)
                    business_data['name'] = name_element.text.strip()
                    break
                except:
                    continue
            
            # Extract address
            address_selectors = [
                "//button[@data-item-id='address']//div[contains(@class, 'Io6YTe')]",
                "//div[contains(@class, 'Io6YTe fontBodyMedium')]",
                "//div[@data-item-id='address']"
            ]
            
            for selector in address_selectors:
                try:
                    address_element = self.driver.find_element(By.XPATH, selector)
                    business_data['address'] = address_element.text.strip()
                    break
                except:
                    continue
            
            # Extract rating and reviews
            try:
                rating_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'F7nice')]//span[@aria-hidden='true']")
                business_data['rating'] = float(rating_element.text.strip())
            except:
                pass
            
            try:
                review_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'F7nice')]//span[contains(text(), 'reviews')]")
                review_text = review_element.text.strip()
                business_data['review_count'] = int(re.search(r'(\d+)', review_text).group(1))
            except:
                pass
            
            # Extract phone
            phone_selectors = [
                "//button[@data-item-id='phone:tel:']//div[contains(@class, 'Io6YTe')]",
                "//button[contains(@data-item-id, 'phone')]//div[contains(@class, 'Io6YTe')]",
                "//a[starts-with(@href, 'tel:')]"
            ]
            
            for selector in phone_selectors:
                try:
                    phone_element = self.driver.find_element(By.XPATH, selector)
                    business_data['mobile'] = phone_element.text.strip()
                    break
                except:
                    continue
            
            # Extract website
            website_selectors = [
                "//a[@data-item-id='authority']",
                "//button[@data-item-id='authority']//div[contains(@class, 'Io6YTe')]",
                "//a[contains(@class, 'CsEnBe')]"
            ]
            
            for selector in website_selectors:
                try:
                    website_element = self.driver.find_element(By.XPATH, selector)
                    href = website_element.get_attribute('href')
                    if href and not href.startswith('tel:'):
                        business_data['website'] = href
                        break
                except:
                    continue
            
            return business_data
            
        except Exception as e:
            print(f"❌ Data extraction error: {e}")
            return None

    def run_extraction(self):
        """Main extraction process optimized for Railway"""
        start_time = datetime.now()
        results = []
        
        try:
            print("🚀 RAILWAY-OPTIMIZED EXTRACTION")
            print(f"🔍 Query: '{self.search_query}'")
            print(f"🎯 Target: {self.max_results} businesses")
            print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)
            
            # Search
            if not self.search_google_maps():
                print("❌ Search failed")
                return []
            
            # Extract links
            business_links = self.get_business_links()
            if not business_links:
                print("❌ No business links found")
                return []
            
            print(f"✅ Found {len(business_links)} business links")
            
            # Extract data
            print("📊 EXTRACTING BUSINESS DATA")
            print("=" * 70)
            
            for i, link in enumerate(business_links[:self.max_results], 1):
                print(f"[{i:2d}/{len(business_links)}] Processing...")
                
                try:
                    business_data = self.extract_business_data(link)
                    if business_data and business_data.get('name') != 'Unknown Business':
                        results.append(business_data)
                        
                        if business_data.get('email') or business_data.get('mobile'):
                            self.contacts_found += 1
                            
                except Exception as e:
                    print(f"❌ Error processing {link}: {e}")
                
                # Progress update
                if i % 10 == 0:
                    elapsed = datetime.now() - start_time
                    rate = i / elapsed.total_seconds() * 60 if elapsed.total_seconds() > 0 else 0
                    print(f"📈 Progress: {len(results)} extracted, {rate:.1f}/min")
                
                time.sleep(random.uniform(1, 2))
            
            # Final summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("=" * 70)
            print("🎉 EXTRACTION COMPLETED!")
            print(f"⏱️ Duration: {duration}")
            print(f"📊 Links found: {len(business_links)}")
            print(f"✅ Businesses extracted: {len(results)}")
            print(f"📞 Contacts found: {self.contacts_found}")
            print(f"📈 Success rate: {(len(results)/len(business_links)*100):.1f}%")
            
            return results
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
            return []
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.driver:
                self.driver.quit()
                print("🧹 Browser cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    scraper = RailwayOptimizedScraper("restaurants in New York", max_results=20)
    results = scraper.run_extraction()
    print(f"Final results: {len(results)} businesses")
