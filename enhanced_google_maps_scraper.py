#!/usr/bin/env python3
"""
Enhanced Google Maps Scraper - Optimized for maximum lead extraction
Addresses issues with limited results (4-5 leads) by implementing:
- More aggressive scrolling strategies
- Better selector coverage
- Improved wait times and retry logic
- Enhanced result extraction methods
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


class EnhancedGoogleMapsBusinessScraper:
    def __init__(self, search_query, max_results=10, visit_websites=True):
        self.search_query = search_query
        self.max_results = max_results
        self.visit_websites = visit_websites
        self.results = []
        self.extracted_count = 0
        self.chrome_options = Options()
        self.driver = None
        self.wait = None
        self.max_retries = 3
        self.retry_delay = 2
        
        # Enhanced email and phone patterns
        self.email_patterns = [
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            re.compile(r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'),
            re.compile(r'email[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})', re.IGNORECASE),
        ]
        
        # Enhanced phone patterns with better support for Indian numbers
        self.phone_patterns = [
            # Indian numbers with country code (e.g., +91 98765 43210, 91-98765-43210)
            re.compile(r'(?:\+?(91)|(0)|(\+?\d{1,3}))?[\s.-]?\b(\d{5})\s?-?\s?(\d{5})\b'),
            # Standard 10-digit numbers
            re.compile(r'(?:\+?(\d{1,3})[\s.-]?)?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})\b'),
            # Numbers with special characters
            re.compile(r'(?:\+?(\d{1,3})[\s.-]?)?\(?\s*(\d{2,})\s*\)?[\s.-]?\s*(\d+)[\s.-]?\s*(\d+)\b'),
            # Simple 10+ digit numbers
            re.compile(r'\b(?:\+?\d{1,3}[\s.-]?)?(\d[\s.-]?){9,}\d\b'),
            # Phone numbers in href attributes
            re.compile(r'tel:(\+?[\d\s.-]{10,})\b'),
            # Common phone number formats
            re.compile(r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            # Indian mobile numbers
            re.compile(r'\b(?:0|\+?91[\s-]?)?[6-9]\d{9}\b')
        ]
        
        self._setup_browser()
    
    def _setup_browser(self):
        """Setup Chrome browser with enhanced options and memory management"""
        print("🛠️ Setting up enhanced browser with crash protection...")
        
        self.chrome_options = Options()
        
        # Memory and performance optimizations
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-software-rasterizer')
        self.chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        self.chrome_options.add_argument('--disable-site-isolation-trials')
        self.chrome_options.add_argument('--disable-web-security')
        self.chrome_options.add_argument('--disable-background-timer-throttling')
        self.chrome_options.add_argument('--disable-renderer-backgrounding')
        self.chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        self.chrome_options.add_argument('--disable-ipc-flooding-protection')
        self.chrome_options.add_argument('--disable-hang-monitor')
        self.chrome_options.add_argument('--disable-breakpad')
        self.chrome_options.add_argument('--disable-crash-reporter')
        self.chrome_options.add_argument('--disable-crashpad')
        self.chrome_options.add_argument('--js-flags=--max-old-space-size=512')
        
        # Disable features that can cause crashes
        self.chrome_options.add_argument('--disable-accelerated-2d-canvas')
        self.chrome_options.add_argument('--disable-accelerated-jpeg-decoding')
        self.chrome_options.add_argument('--disable-accelerated-mjpeg-decode')
        self.chrome_options.add_argument('--disable-accelerated-video-decode')
        self.chrome_options.add_argument('--disable-features=ScriptStreaming')
        self.chrome_options.add_argument('--disable-gpu-early-init')
        self.chrome_options.add_argument('--disable-threaded-animation')
        self.chrome_options.add_argument('--disable-threaded-scrolling')
        self.chrome_options.add_argument('--disable-v8-idle-tasks')
        self.chrome_options.add_argument('--disable-webgl')
        self.chrome_options.add_argument('--disable-webgl2')
        
        # Headless mode settings
        self.chrome_options.add_argument('--headless=new')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Memory management
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--no-zygote')
        self.chrome_options.add_argument('--single-process')
        
        # Disable extensions and automation detection
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Language and encoding
        self.chrome_options.add_argument('--lang=en-US')
        self.chrome_options.add_argument('--accept-lang=en-US,en')
        
        # User agent
        self.chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Enhanced options for better performance and stability
        browser_options = [
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-software-rasterizer",
            "--disable-dev-tools",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-default-apps",
            "--mute-audio",
            "--disable-sync",
            "--disable-translate",
            "--disable-logging",
            "--disable-permissions-api",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--disable-site-isolation-trials",
            "--disable-web-security",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-hang-monitor",
            "--no-pings",
            "--window-size=1920,1080",
            "--disable-ipc-flooding-protection",
            "--password-store=basic",
            "--use-mock-keychain",
            "--disable-breakpad",
            "--disable-crash-reporter",
            "--disable-crashpad",
            "--lang=en-US",
            "--accept-lang=en-US,en",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--js-flags=--max-old-space-size=512",
            "--disable-accelerated-2d-canvas",
            "--disable-accelerated-jpeg-decoding",
            "--disable-accelerated-mjpeg-decode",
            "--disable-accelerated-video-decode",
            "--disable-backgrounding-occluded-windows",
            "--disable-background-timer-throttling",
            "--disable-features=ScriptStreaming",
            "--disable-gpu-early-init",
            "--disable-remote-fonts",
            "--disable-threaded-animation",
            "--disable-threaded-scrolling",
            "--disable-v8-idle-tasks",
            "--disable-webgl",
            "--disable-webgl2",
            "--enable-features=NetworkService,NetworkServiceInProcess",
            "--force-color-profile=srgb",
            "--no-first-run",
            "--no-sandbox-and-elevated"
        ]
        
        for option in browser_options:
            self.chrome_options.add_argument(option)

        # Enhanced preferences with memory optimizations
        prefs = {
            'intl.accept_languages': 'en-US,en',
            'intl.charset_default': 'UTF-8',
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
            'profile.managed_default_content_settings.images': 2,  # Block images
            'profile.managed_default_content_settings.javascript': 1,  # Keep JS enabled
            'profile.managed_default_content_settings.cookies': 2,  # Block cookies
            'profile.managed_default_content_settings.plugins': 2,  # Block plugins
            'profile.managed_default_content_settings.geolocation': 2,  # Block geolocation
            'profile.managed_default_content_settings.media_stream': 2,  # Block media
            'profile.managed_default_content_settings.popups': 2,  # Block popups
            'profile.managed_default_content_settings.midi_sysex': 2,  # Block MIDI
            'profile.managed_default_content_settings.media_stream_mic': 2,  # Block mic
            'profile.managed_default_content_settings.media_stream_camera': 2,  # Block camera
            'profile.managed_default_content_settings.protocol_handlers': 2,  # Block protocol handlers
            'profile.managed_default_content_settings.ppapi_broker': 2,  # Block PPAPI
            'profile.managed_default_content_settings.automatic_downloads': 2,  # Block auto-downloads
            'profile.managed_default_content_settings.midi_devices': 2,  # Block MIDI devices
            'profile.managed_default_content_settings.clipboard': 2,  # Block clipboard
            'profile.managed_default_content_settings.download_restrictions': 1,  # Safe browsing
        }
        self.chrome_options.add_experimental_option('prefs', prefs)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add memory management options
                self.chrome_options.add_argument(f'--js-flags=--max-old-space-size={512 + (attempt * 128)}')
                
                # Initialize WebDriver with error handling
                self.driver = webdriver.Chrome(options=self.chrome_options)
                self.wait = WebDriverWait(self.driver, 20 + (attempt * 5))  # Increase timeout with retries
                
                # Set page load timeout and script timeout
                self.driver.set_page_load_timeout(60)
                self.driver.set_script_timeout(30)
                
                # Clear browser cache and cookies safely
                self.driver.delete_all_cookies()
                
                # Only clear storage if we're on a valid URL
                current_url = self.driver.current_url or ''
                if current_url and (current_url.startswith('http') or current_url.startswith('https')):
                    try:
                        self.driver.execute_script('''
                            try {
                                if (window.localStorage) window.localStorage.clear();
                                if (window.sessionStorage) window.sessionStorage.clear();
                            } catch(e) {
                                console.log('Storage clear error:', e);
                            }
                        ''')
                    except Exception as e:
                        print(f"⚠️ Warning: Could not clear storage: {str(e)}")
                
                print(f"✅ Enhanced browser setup completed (Attempt {attempt + 1}/{max_retries})")
                return
                
            except Exception as e:
                print(f"❌ Browser setup attempt {attempt + 1} failed: {str(e)}")
                if hasattr(self, 'driver'):
                    try:
                        self.driver.quit()
                    except:
                        pass
                
                if attempt == max_retries - 1:
                    print("❌ All browser setup attempts failed")
                    raise
                
                # Wait before retry
                import time
                time.sleep(2 ** attempt)  # Exponential backoff

    def search_google_maps(self):
        """Enhanced Google Maps search with multiple strategies"""
        try:
            print(f"🔍 Enhanced search for: {self.search_query}")

            # Direct search with enhanced URL and parameters
            search_url = f"https://www.google.com/maps/search/{self.search_query.replace(' ', '+')}?hl=en&gl=us"
            print(f"🌐 Navigating to: {search_url}")

            self.driver.set_page_load_timeout(20)
            self.driver.set_script_timeout(20)
            self.driver.get(search_url)
            
            # More efficient initial wait
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='main']"))
            )

            # Handle consent/cookies more aggressively
            self._handle_consent_and_cookies()

            # Wait for results with multiple indicators
            self._wait_for_search_results()

            print("✅ Enhanced search completed")
            return True

        except Exception as e:
            print(f"❌ Enhanced search failed: {e}")
            return False

    def _handle_consent_and_cookies(self):
        """Ultra-fast consent handling with minimal delays"""
        try:
            # Use JavaScript to handle consent (faster than Selenium clicks)
            consent_script = """
            // Try to find and click any consent button
            const clickButton = (selectors) => {
                for (const selector of selectors) {
                    try {
                        const btn = document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        if (btn && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    } catch(e) {}
                }
                return false;
            };
            
            const buttons = [
                '//button[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "accept")]',
                '//button[contains(., "✓")]',
                '//button[contains(., "OK")]',
                '//button[contains(., "Got it")]',
                '//button[contains(., "Continue")]',
                '//button[contains(@class, "VfPpkd")]',
                '//button[contains(@class, "lssxud")]',
                '//button[not(@disabled)]',
                '//button[1]'
            ];
            
            return clickButton(buttons);
            """
            
            # Execute with minimal timeout
            self.driver.set_script_timeout(2)
            result = self.driver.execute_script(consent_script)
            
            if result:
                print("✅ Consent handled (fast path)")
                return
                
            # Fallback to Selenium method if JS method failed
            consent_selectors = [
                "//button[contains(., 'Accept all')]",
                "//button[contains(., 'I agree')]",
                "//button[contains(., 'Accept')]",
                "//button[contains(@class, 'VfPpkd-LgbsSe')]"
            ]
            
            for selector in consent_selectors:
                try:
                    button = WebDriverWait(self.driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.driver.execute_script("arguments[0].click();", button)
                    print("✅ Consent handled (fallback)")
                    time.sleep(0.5)  # Minimal delay after click
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Consent handling: {e}")

    def _wait_for_search_results(self):
        """Optimized waiting for search results"""
        print("⏳ Waiting for search results...")
        
        # Optimized result indicators (reduced to most common selectors)
        result_selectors = [
            "//div[contains(@class, 'Nv2PK')]",
            "//div[@role='article']",
            "//a[contains(@href, '/maps/place/')]"
        ]

        # Use WebDriverWait with expected conditions for better performance
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: any(d.find_elements(By.XPATH, selector) for selector in result_selectors)
            )
            elements = []
            for selector in result_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Found {len(elements)} results")
                    return True
        except TimeoutException:
            print("⚠️ Timeout waiting for results, but continuing...")
            
        return True

    def get_business_links(self):
        """Ultra-fast business link extraction with optimized performance"""
        try:
            print("🚀 Starting ultra-fast link extraction...")
            all_links = set()
            scroll_attempts = 0
            max_scrolls = min(50, max(20, self.max_results))  # More dynamic scroll limit
            no_new_content_count = 0
            max_patience = 8  # Even more aggressive patience

            # Ultra-optimized link selectors (prioritized by speed and reliability)
            link_selectors = [
                '//div[contains(@class, "Nv2PK")]//a[contains(@href, "/maps/place/")]',  # Primary
                '//div[@role="article"]//a[contains(@href, "/maps/place/")][1]',  # First article
                '//div[contains(@class, "hfpxzc")]//a[contains(@href, "/maps/place/")]',  # New cards
                '//a[contains(@href, "/maps/place/")][1]'  # First fallback
            ]

            while scroll_attempts < max_scrolls and len(all_links) < self.max_results:
                print(f"🔄 Enhanced scroll {scroll_attempts + 1}/{max_scrolls}")

                # Ultra-fast link extraction with batched processing
                new_links_count = 0
                try:
                    # Use JavaScript for faster link extraction
                    extract_script = """
                    const links = new Set();
                    const selectors = [
                        'div.Nv2PK a[href*="/maps/place/"]',
                        'div[role="article"] a[href*="/maps/place/"]',
                        'div.hfpxzc',
                        'a[href*="/maps/place/"]'
                    ];
                    
                    // Find all matching elements
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            const href = el.href || el.getAttribute('href');
                            if (href && href.includes('/maps/place/')) {
                                links.add(href.split('?')[0]); // Remove URL parameters
                            }
                        });
                    });
                    
                    return Array.from(links);
                    """
                    
                    # Execute extraction script
                    self.driver.set_script_timeout(2)
                    links = self.driver.execute_script(extract_script) or []
                    
                    # Process found links
                    for href in links:
                        if href and href not in all_links:
                            all_links.add(href)
                            new_links_count += 1
                            if len(all_links) >= self.max_results:
                                break
                                    
                except Exception as e:
                    print(f"⚠️ Fast link extraction error: {e}")
                    # Fallback to Selenium method if JS fails
                    try:
                        elements = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]')
                        for el in elements[:50]:  # Limit to first 50 elements
                            try:
                                href = el.get_attribute('href')
                                if href and '/maps/place/' in href and href not in all_links:
                                    all_links.add(href)
                                    new_links_count += 1
                                    if len(all_links) >= self.max_results:
                                        break
                            except:
                                continue
                    except Exception as e2:
                        print(f"⚠️ Fallback extraction failed: {e2}")

                current_count = len(all_links)
                progress = (current_count / self.max_results) * 100 if self.max_results > 0 else 0
                print(f"📊 Found {current_count} links (+{new_links_count} new) - {progress:.1f}% of target")

                # Early exit if target reached
                if current_count >= self.max_results:
                    print(f"🎯 Target reached: {current_count} links")
                    break

                # Super aggressive patience logic
                if new_links_count == 0:
                    no_new_content_count += 1
                    # Try different scroll strategies when stuck
                    if no_new_content_count == 3:
                        print("🔄 Trying alternative scroll strategy...")
                        self._alternative_scroll_strategy()
                    elif no_new_content_count == 6:
                        print("🔄 Trying page refresh strategy...")
                        self._page_refresh_strategy()
                    elif no_new_content_count == 10:
                        print("🔄 Trying zoom out strategy...")
                        self._zoom_out_strategy()
                    
                    if no_new_content_count >= max_patience:
                        print(f"⏹️ No new content after {max_patience} attempts")
                        break
                else:
                    no_new_content_count = 0

                # Enhanced scrolling strategy
                self._enhanced_scroll()
                
                # Ultra-fast delay strategy
                if new_links_count > 0:
                    delay = random.uniform(0.1, 0.5)  # Much faster when finding results
                else:
                    delay = random.uniform(0.5, 1.0)  # Reduced delay when stuck
                
                # Process any pending events
                try:
                    self.driver.execute_script("return 1;")  # Keep connection alive
                except:
                    pass
                    
                time.sleep(delay)
                
                # Early exit if we have enough links
                if len(all_links) >= self.max_results:
                    break
                
                scroll_attempts += 1

            business_links = list(all_links)[:self.max_results]
            print(f"✅ Enhanced extraction complete: {len(business_links)} links")

            # Show sample links for debugging
            if business_links:
                print("🔗 Sample links:")
                for i, link in enumerate(business_links[:5]):
                    print(f"  {i+1}. {link[:80]}...")

            return business_links

        except Exception as e:
            print(f"❌ Enhanced link extraction failed: {e}")
            return []

    def _enhanced_scroll(self):
        """Ultra-fast scrolling with optimized performance"""
        try:
            # Single efficient scroll script with multiple fallbacks
            scroll_script = """
            // Try multiple scroll strategies
            function scrollPage() {
                // Try main scroll container first
                const containers = [
                    document.querySelector('div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.tLjsW'),
                    document.querySelector('div.e07Vkf.kA9KIf'),
                    document.documentElement,
                    document.body
                ];
                
                // Find first valid container
                const target = containers.find(el => el && el.scrollHeight > 0) || window;
                
                // Calculate scroll amount (larger scrolls for faster loading)
                const scrollAmount = Math.max(
                    1000,
                    Math.min(2000, target.scrollHeight * 0.3)  // Scroll 30% of container height
                );
                
                // Smooth scroll to trigger lazy loading
                target.scrollBy({
                    top: scrollAmount,
                    behavior: 'smooth'
                });
                
                return true;
            }
            
            return scrollPage();
            """
            
            # Execute scroll with minimal timeout
            self.driver.set_script_timeout(1.5)
            self.driver.execute_script(scroll_script)
            
            # Tiny delay to allow content to load
            time.sleep(0.15)
            
        except Exception as e:
            # Ultra-fast fallback
            self.driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(0.5)
            # Body scroll
            self.driver.execute_script("document.body.scrollTop += 1000")
            time.sleep(0.5)
            # Try to find and scroll any scrollable div
            try:
                scrollable_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[style*='overflow']")
                for div in scrollable_divs[:3]:
                    self.driver.execute_script("arguments[0].scrollTop += 500", div)
                    time.sleep(0.3)
            except:
                pass

            # Method 2: Fallback scrolling
            if not scrolled:
                # Page scroll
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(0.5)
                # Body scroll
                self.driver.execute_script("document.body.scrollTop += 1000")
                time.sleep(0.5)
                # Try to find and scroll any scrollable div
                try:
                    scrollable_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[style*='overflow']")
                    for div in scrollable_divs[:3]:
                        self.driver.execute_script("arguments[0].scrollTop += 500", div)
                        time.sleep(0.3)
                except:
                    pass

            # Method 3: Keyboard scrolling (sometimes more effective)
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
                body.send_keys(Keys.PAGE_DOWN)
            except:
                pass

        except Exception as e:
            print(f"⚠️ Enhanced scroll error: {e}")

    def _alternative_scroll_strategy(self):
        """Alternative scrolling when normal scrolling fails"""
        try:
            # Strategy 1: Click "Show more results" if available
            show_more_selectors = [
                "//button[contains(text(), 'Show more')]",
                "//button[contains(text(), 'More results')]",
                "//div[contains(text(), 'Show more')]//parent::button",
                "//span[contains(text(), 'Show more')]//parent::button"
            ]
            
            for selector in show_more_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    button.click()
                    print("✅ Clicked 'Show more' button")
                    time.sleep(3)
                    return
                except:
                    continue
            
            # Strategy 2: Try keyboard navigation
            from selenium.webdriver.common.keys import Keys
            body = self.driver.find_element(By.TAG_NAME, "body")
            for _ in range(10):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
            
            print("✅ Used alternative keyboard scrolling")
            
        except Exception as e:
            print(f"⚠️ Alternative scroll failed: {e}")

    def _page_refresh_strategy(self):
        """Refresh page and scroll to get more results"""
        try:
            print("🔄 Refreshing page to get more results...")
            current_url = self.driver.current_url
            self.driver.refresh()
            time.sleep(5)
            
            # Scroll immediately after refresh
            for _ in range(20):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.3)
            
            print("✅ Page refresh strategy completed")
            
        except Exception as e:
            print(f"⚠️ Page refresh failed: {e}")

    def _zoom_out_strategy(self):
        """Zoom out to show more results"""
        try:
            print("🔍 Zooming out to show more results...")
            
            # Try to find and click zoom out button
            zoom_selectors = [
                "//button[@aria-label='Zoom out']",
                "//button[contains(@class, 'widget-zoom-out')]",
                "//div[@data-value='Zoom out']//parent::button"
            ]
            
            for selector in zoom_selectors:
                try:
                    for _ in range(3):  # Zoom out multiple times
                        button = self.driver.find_element(By.XPATH, selector)
                        button.click()
                        time.sleep(1)
                    print("✅ Zoomed out successfully")
                    return
                except:
                    continue
            
            # Fallback: Use keyboard zoom
            from selenium.webdriver.common.keys import Keys
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.CONTROL, "-", "-", "-")  # Zoom out
            time.sleep(2)
            
            print("✅ Used keyboard zoom out")
            
        except Exception as e:
            print(f"⚠️ Zoom out failed: {e}")

    def extract_business_data(self, business_url):
        """Enhanced business data extraction"""
        try:
            print(f"📊 Enhanced extraction: {business_url[:60]}...")
            self.driver.get(business_url)
            time.sleep(random.uniform(4, 7))  # Longer wait for full page load

            data = {
                'name': '',
                'address': '',
                'rating': None,
                'review_count': None,
                'category': '',
                'website': None,
                'mobile': None,
                'email': None,
                'secondary_email': None,
                'google_maps_url': business_url,
                'search_query': self.search_query,
                'website_visited': False,
                'additional_contacts': ''
            }

            # Safe extraction of all data with error handling
            data['name'] = self._safe_extract(self._extract_business_name, 'Not available')
            data['address'] = self._safe_extract(self._extract_address, 'Address not found')
            
            # Extract rating and reviews safely
            rating_data = self._safe_extract(self._extract_rating_and_reviews, (None, None))
            data['rating'], data['review_count'] = rating_data if isinstance(rating_data, tuple) else (None, None)
            
            data['category'] = self._safe_extract(self._extract_category, 'Not specified')
            data['website'] = self._safe_extract(self._extract_website)
            data['mobile'] = self._safe_extract(self._extract_phone_enhanced)

            self.extracted_count += 1

            # Enhanced summary
            summary = f"✅ {data['name']}"
            if data['rating']:
                summary += f" ({data['rating']}⭐)"
            if data['mobile']:
                summary += f" 📞{data['mobile']}"
            if data['website']:
                summary += f" 🌐"

            print(summary)
            return data

        except Exception as e:
            print(f"❌ Enhanced extraction failed: {e}")
            return None

    def _extract_business_name(self):
        """Enhanced business name extraction"""
        name_selectors = [
            'h1[data-attrid="title"]',
            'h1.DUwDvf',
            'h1.x3AX1-LfntMc-header-title-title',
            'h1.fontHeadlineLarge',
            'h1',
            '.x3AX1-LfntMc-header-title-title',
            '.DUwDvf',
            '.fontHeadlineLarge',
            '[data-attrid="title"]'
        ]

        for selector in name_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                name = element.text.strip()
                if name and len(name) > 1:
                    return name
            except:
                continue
        return 'Unknown Business'

    def _extract_address(self):
        """Enhanced address extraction"""
        address_selectors = [
            '[data-item-id="address"]',
            '.Io6YTe.fontBodyMedium.kR99db.fdkmkc',
            '.rogA2c .Io6YTe',
            'button[data-item-id="address"]',
            '.fccl3c .Io6YTe',
            '[data-item-id*="address"]',
            '.fontBodyMedium[data-item-id*="address"]'
        ]

        for selector in address_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                address = element.text.strip()
                if address and len(address) > 5:
                    return address
            except:
                continue
        return 'Address not found'

    def _extract_rating_and_reviews(self):
        """Enhanced rating and review extraction with error handling"""
        rating = None
        review_count = None
        
        # Add a small delay to ensure elements are loaded
        time.sleep(0.5)

        # Rating selectors
        rating_selectors = [
            '.F7nice span[aria-hidden="true"]',
            '.ceNzKf[aria-label*="stars"]',
            'span.ceNzKf',
            '.MW4etd',
            '.fontDisplayLarge'
        ]

        for selector in rating_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    rating = float(match.group(1))
                    break
            except:
                continue

        # Review count selectors
        review_selectors = [
            '.F7nice span:nth-child(2)',
            'button[aria-label*="reviews"]',
            '.UY7F9',
            '.fontBodyMedium[aria-label*="reviews"]'
        ]

        for selector in review_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                match = re.search(r'[\(]?(\d+(?:,\d+)*)[\)]?', text)
                if match:
                    review_count = int(match.group(1).replace(',', ''))
                    break
            except:
                continue

        return rating, review_count

    def _extract_category(self):
        """Enhanced category extraction"""
        category_selectors = [
            '.DkEaL',
            'button[jsaction*="category"]',
            '.YhemCb',
            '.fontBodyMedium[data-value*="category"]'
        ]

        for selector in category_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                category = element.text.strip()
                if category and len(category) > 2:
                    return category
            except:
                continue
        return 'Category not found'

    def _extract_website(self):
        """Enhanced website extraction"""
        website_selectors = [
            'a[data-item-id="authority"]',
            'a[href*="http"]:not([href*="google.com"]):not([href*="maps"])',
            '.CsEnBe a[href*="http"]',
            'a[data-item-id*="website"]'
        ]

        for selector in website_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                url = element.get_attribute('href')
                if url and 'google.com' not in url and 'maps' not in url:
                    return url
            except:
                continue
        return None

    def _extract_phone_enhanced(self):
        """Enhanced phone number extraction with multiple strategies"""
        try:
            # Strategy 1: Direct phone button/link selectors
            phone_selectors = [
                "//button[@data-item-id='phone:tel:']",
                "//button[contains(@data-item-id,'phone')]",
                "//div[@data-item-id='phone:tel:']",
                "//div[contains(@data-item-id,'phone')]//div[contains(@class,'Io6YTe')]",
                "//a[starts-with(@href,'tel:')]",
                "//button[contains(@aria-label,'Phone')]",
                "//button[contains(@aria-label,'Call')]"
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
            
            # Strategy 2: Text-based search in visible elements
            text_selectors = [
                "//span[contains(text(),'(') and contains(text(),')')]",
                "//div[contains(text(),'(') and contains(text(),')')]",
                "//div[contains(@class,'fontBodyMedium')]"
            ]
            
            for selector in text_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        phone = self._extract_phone_from_element(element)
                        if phone:
                            return phone
                except:
                    continue
            
            # Strategy 3: Page source search (last resort)
            page_source = self.driver.page_source
            for pattern in self.phone_patterns:
                matches = pattern.findall(page_source)
                for match in matches:
                    if isinstance(match, tuple):
                        match = ''.join(match)
                    digits = re.sub(r'\D', '', str(match))
                    if len(digits) >= 10:
                        return str(match)
            
            return None
            
        except Exception as e:
            print(f"❌ Enhanced phone extraction error: {e}")
            return None

    def _extract_phone_from_element(self, element):
        """Extract phone from element with enhanced patterns"""
        try:
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
                for pattern in self.phone_patterns:
                    match = pattern.search(text)
                    if match:
                        phone = match.group(0) if not isinstance(match.group(0), tuple) else ''.join(match.group(0))
                        digits = re.sub(r'\D', '', phone)
                        if len(digits) >= 10:
                            return phone
            
            return None
            
        except:
            return None

    def run_extraction(self):
        """Enhanced main extraction process"""
        start_time = datetime.now()
        results = []

        try:
            print(f"🚀 ENHANCED GOOGLE MAPS EXTRACTION")
            print(f"🔍 Query: '{self.search_query}'")
            print(f"🎯 Target: {self.max_results} businesses")
            print(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)

            # Enhanced search
            if not self.search_google_maps():
                print("❌ Enhanced search failed")
                return []

            # Enhanced link extraction
            business_links = self.get_business_links()
            if not business_links:
                print("❌ No business links found")
                return []

            print(f"✅ Found {len(business_links)} business links")

            # Enhanced data extraction
            print(f"\n📊 ENHANCED DATA EXTRACTION")
            print("=" * 70)

            successful = 0
            failed = 0

            for i, link in enumerate(business_links, 1):
                print(f"\n[{i:2d}/{len(business_links)}] Processing...")

                try:
                    business_data = self.extract_business_data(link)
                    if business_data and business_data.get('name') != 'Unknown Business':
                        results.append(business_data)
                        successful += 1
                        
                        if business_data.get('email') or business_data.get('mobile'):
                            self.contacts_found += 1
                    else:
                        failed += 1

                except Exception as e:
                    failed += 1
                    print(f"❌ Error: {e}")

                # Progress updates
                if i % 10 == 0:
                    elapsed = datetime.now() - start_time
                    rate = i / elapsed.total_seconds() * 60 if elapsed.total_seconds() > 0 else 0
                    print(f"📈 Progress: {successful} successful, {rate:.1f}/min")

                # Adaptive delay
                delay = random.uniform(1.5, 3.5)
                time.sleep(delay)

            # Enhanced final summary
            end_time = datetime.now()
            duration = end_time - start_time

            print(f"\n" + "=" * 70)
            print(f"🎉 ENHANCED EXTRACTION COMPLETED!")
            print(f"⏱️ Duration: {duration}")
            print(f"📊 Links processed: {len(business_links)}")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📞 Contacts found: {self.contacts_found}")
            print(f"📋 Final results: {len(results)} businesses")
            print(f"📈 Success rate: {(successful/len(business_links)*100):.1f}%")

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
            print("🧹 Enhanced cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


def enhanced_scrape_google_maps(query, max_results=100, visit_websites=True):
    """Enhanced convenience function"""
    scraper = EnhancedGoogleMapsBusinessScraper(
        search_query=query,
        max_results=max_results,
        visit_websites=visit_websites
    )
    return scraper.run_extraction()


if __name__ == "__main__":
    # Test the enhanced scraper
    results = enhanced_scrape_google_maps("restaurants in New York", max_results=50)
    print(f"\nEnhanced test completed. Found {len(results)} results.")
    for result in results[:5]:
        print(f"- {result['name']}: {result['address']}")
