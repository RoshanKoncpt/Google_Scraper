import time
import random
import platform
import requests
import zipfile
import io
import os
import subprocess
import re
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, \
    StaleElementReferenceException


class GoogleMapsBusinessScraper:
    def __init__(self, query, location, max_results=30, headless=False, min_results=10, debug_dir="debug_evidence"):
        self.query = query
        self.location = location  # Specific location to search in
        self.max_results = max_results
        self.min_results = min_results
        self.driver = None
        self.results = []
        self.headless = headless
        self.debug_dir = debug_dir
        self.setup_debug_directory()
        self.setup_browser()

    def setup_debug_directory(self):
        """Create directory for debug evidence"""
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
        print(f"📁 Debug evidence will be saved to: {self.debug_dir}")

    def capture_evidence(self, name, page_source=False):
        """Capture screenshot and optionally page source"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Capture screenshot
        screenshot_path = os.path.join(self.debug_dir, f"{name}_{timestamp}.png")
        try:
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Saved screenshot: {screenshot_path}")
        except Exception as e:
            print(f"❌ Failed to save screenshot: {e}")

        # Capture page source if requested
        if page_source:
            page_source_path = os.path.join(self.debug_dir, f"{name}_{timestamp}.html")
            try:
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print(f"📄 Saved page source: {page_source_path}")
                return len(self.driver.page_source)
            except Exception as e:
                print(f"❌ Failed to save page source: {e}")

        return 0

    def get_chrome_version(self):
        """Get the installed Chrome version"""
        try:
            if platform.system() == "Windows":
                # Try different registry paths for 32-bit and 64-bit Chrome
                try:
                    # For 64-bit Windows with 64-bit Chrome
                    import winreg
                    reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        version, _ = winreg.QueryValueEx(key, "version")
                        return version.split('.')[0]  # Return major version
                except:
                    try:
                        # For 32-bit Chrome on 64-bit Windows
                        reg_path = r"SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                            version, _ = winreg.QueryValueEx(key, "version")
                            return version.split('.')[0]
                    except:
                        # Try command line approach
                        try:
                            result = subprocess.run(
                                ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v',
                                 'version'],
                                capture_output=True, text=True, check=True)
                            version_line = [line for line in result.stdout.split('\n') if 'version' in line][0]
                            version = version_line.split('REG_SZ')[1].strip()
                            return version.split('.')[0]
                        except:
                            # Final fallback - try to get version from Chrome executable
                            try:
                                paths = [
                                    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                                    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                                    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
                                ]
                                for path in paths:
                                    if os.path.exists(path):
                                        version = subprocess.check_output(
                                            [path, '--version']).decode('utf-8').split(' ')[2]
                                        return version.split('.')[0]
                            except:
                                pass
            else:
                # For macOS and Linux
                try:
                    version = subprocess.check_output(['google-chrome', '--version']).decode('utf-8').split(' ')[2]
                    return version.split('.')[0]
                except:
                    try:
                        version = subprocess.check_output(['chromium-browser', '--version']).decode('utf-8').split(' ')[
                            1]
                        return version.split('.')[0]
                    except:
                        pass

            print("⚠️ Could not detect Chrome version, using default ChromeDriver")
            return None
        except Exception as e:
            print(f"⚠️ Error detecting Chrome version: {e}")
            return None

    def download_chromedriver(self, version):
        """Download the appropriate ChromeDriver for the detected Chrome version"""
        try:
            # Get the latest ChromeDriver version for the detected Chrome major version
            if version:
                url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version}"
            else:
                url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"

            response = requests.get(url)
            driver_version = response.text.strip()

            # Determine the system architecture
            system = platform.system().lower()
            architecture = platform.architecture()[0]

            if system == "windows":
                if architecture == "64bit":
                    driver_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
                else:
                    driver_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
            elif system == "darwin":
                # Check if it's Apple Silicon or Intel
                if platform.processor() == 'arm' or platform.machine() == 'arm64':
                    driver_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_mac_arm64.zip"
                else:
                    driver_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_mac64.zip"
            else:  # linux
                driver_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_linux64.zip"

            print(f"📥 Downloading ChromeDriver {driver_version} from {driver_url}")

            # Download and extract ChromeDriver
            response = requests.get(driver_url)
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            zip_file.extractall("chromedriver")

            driver_path = os.path.join("chromedriver", "chromedriver")
            if system == "windows":
                driver_path += ".exe"

            # Make executable on Unix systems
            if system != "windows":
                os.chmod(driver_path, 0o755)

            print(f"✅ ChromeDriver downloaded to {driver_path}")
            return driver_path

        except Exception as e:
            print(f"❌ Error downloading ChromeDriver: {e}")
            return None

    def setup_browser(self):
        print("🔧 Starting Chrome setup...")

        # Get Chrome version
        chrome_version = self.get_chrome_version()
        print(f"🔍 Detected Chrome major version: {chrome_version or 'Unknown'}")

        # Try to use webdriver_manager first
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.os_manager import ChromeType

            try:
                # Try to install using webdriver_manager
                driver_path = ChromeDriverManager(
                    chrome_type=ChromeType.GOOGLE,
                    version=chrome_version
                ).install()

                service = Service(driver_path)
                chrome_options = self.get_chrome_options()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ ChromeDriverManager setup successful")
                return
            except Exception as e:
                print(f"⚠️ ChromeDriverManager failed: {e}")
        except ImportError:
            print("⚠️ webdriver_manager not available, trying alternative methods")

        # Fallback: download ChromeDriver directly
        try:
            driver_path = self.download_chromedriver(chrome_version)
            if driver_path and os.path.exists(driver_path):
                service = Service(driver_path)
                chrome_options = self.get_chrome_options()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Direct ChromeDriver download successful")
                return
        except Exception as e:
            print(f"⚠️ Direct ChromeDriver download failed: {e}")

        # Final fallback: try system ChromeDriver
        try:
            service = Service()
            chrome_options = self.get_chrome_options()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ System ChromeDriver setup successful")
        except Exception as e:
            print(f"❌ All Chrome setup attempts failed: {e}")
            raise Exception(f"❌ Chrome initialization error: {e}")

    def get_chrome_options(self):
        """Create and return Chrome options"""
        chrome_options = Options()

        # Set headless mode if specified
        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,800")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Rotate user agents to avoid detection
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")

        return chrome_options

    def search(self):
        try:
            # First, search for the location to set the map view
            print(f"📍 Setting location to: {self.location}")
            location_url = f"https://www.google.com/maps/place/{self.location.replace(' ', '+')}"
            self.driver.get(location_url)
            time.sleep(5)

            # Capture evidence after page load
            self.capture_evidence("after_location_load", page_source=True)

            # Now search for the query within this location
            print(f"🔍 Searching for '{self.query}' in {self.location}")
            self.enter_search_query()

            # Wait for results to load
            time.sleep(5)

            # Capture evidence after search
            self.capture_evidence("after_search_load", page_source=True)

            # Accept cookies if prompted (for EU users)
            try:
                cookie_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//button[contains(., 'Accept all') or contains(., 'I agree') or contains(., 'Accept')]"))
                )
                cookie_button.click()
                print("✅ Accepted cookies")
                time.sleep(2)
            except:
                print("ℹ️ No cookie consent dialog found")

            # Scroll and collect results
            self.scroll_for_more_results()

            # If we don't have enough results, try alternative methods within the same location
            if len(self.results) < self.min_results:
                print(f"⚠️ Only {len(self.results)} results found, trying alternative methods...")
                self.try_alternative_queries()

            # Final extraction to ensure we have all possible results
            self.extract_business_data()

            print(f"📊 Total results collected: {len(self.results)}")

        except Exception as e:
            print(f"❌ Error during search: {e}")
            # Take screenshot for debugging
            self.capture_evidence("error", page_source=True)

    def enter_search_query(self):
        """Enter the search query in the search box within the location"""
        try:
            # Find the search box and enter the query
            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input#searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(self.query)

            # Click the search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button#searchbox-searchbutton")
            search_button.click()
            time.sleep(3)

        except Exception as e:
            print(f"❌ Error entering search query: {e}")
            # Fallback to URL-based search
            search_url = f"https://www.google.com/maps/search/{self.query.replace(' ', '+')}+in+{self.location.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(5)

    def scroll_for_more_results(self):
        """Improved scrolling with auto-detection of scrollable elements and evidence capture"""
        print("🔄 Scrolling to load more results...")

        # Try multiple selectors for scroll container
        scroll_selectors = [
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",
            "div[role='feed']",
            "div[aria-label*='results']",
            "div[aria-label*='Results for']",
            "div.scrollable-show"
        ]

        scroll_container = None
        for selector in scroll_selectors:
            try:
                containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if containers:
                    scroll_container = containers[0]
                    print(f"✅ Found scroll container with selector: {selector}")
                    break
            except:
                continue

        if not scroll_container:
            print("⚠️ Could not find scroll container, using window scroll")

        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 50  # Reduced for location-specific searches
        no_new_results_count = 0
        max_no_new_results = 5  # Reduced for location-specific searches

        # Capture initial state
        initial_source_length = self.capture_evidence("before_scroll", page_source=True)

        while (scroll_attempts < max_scroll_attempts and
               len(self.results) < self.max_results and
               no_new_results_count < max_no_new_results):

            previous_result_count = len(self.results)

            # Scroll with multiple techniques
            try:
                if scroll_container:
                    # Scroll to bottom of container
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)

                    # Also try smooth scrolling
                    self.driver.execute_script("""
                        arguments[0].scrollTo({
                            top: arguments[0].scrollHeight,
                            behavior: 'smooth'
                        });
                    """, scroll_container)
                else:
                    # Window scrolling with multiple approaches
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    self.driver.execute_script("window.scrollBy(0, 1000);")
            except StaleElementReferenceException:
                print("⚠️ Scroll container became stale, trying to find it again")
                scroll_container = None
                for selector in scroll_selectors:
                    try:
                        containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if containers:
                            scroll_container = containers[0]
                            break
                    except:
                        continue

            # Random wait time to mimic human behavior
            time.sleep(random.uniform(1.5, 3.5))

            # Try to click "See more places" and similar buttons
            more_buttons_selectors = [
                "//button[contains(., 'See more places')]",
                "//button[contains(., 'More places')]",
                "//button[contains(., 'Show more results')]",
                "//div[contains(@class, 'PbZDve')]//button",
                "//button[@aria-label*='more']"
            ]

            for xpath in more_buttons_selectors:
                try:
                    button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    button.click()
                    print(f"✅ Clicked button: {xpath}")
                    time.sleep(2)
                    break
                except:
                    continue

            # Check scroll progress
            try:
                if scroll_container:
                    new_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                else:
                    new_height = self.driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    scroll_attempts += 1
                    print(f"⏹️ No new content loaded ({scroll_attempts}/{max_scroll_attempts})")

                    # Try alternative scrolling method
                    if scroll_attempts % 5 == 0:
                        self.driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)
                else:
                    scroll_attempts = 0
                    last_height = new_height
                    print(f"📜 Scrolled to load more results ({len(self.results)}/{self.max_results})")
            except:
                last_height = self.driver.execute_script("return document.body.scrollHeight")

            # Extract data after each scroll
            self.extract_business_data()

            # Check if we got new results
            if len(self.results) == previous_result_count:
                no_new_results_count += 1
                print(f"ℹ️ No new results found ({no_new_results_count}/{max_no_new_results})")
            else:
                no_new_results_count = 0

            # Break if we have enough results
            if len(self.results) >= self.max_results:
                break

            # Occasionally try to find more elements
            if no_new_results_count % 3 == 0:
                self.find_hidden_elements()

        # Capture final state after scrolling
        final_source_length = self.capture_evidence("after_scroll", page_source=True)

        # Compare page source lengths
        if initial_source_length > 0 and final_source_length > 0:
            length_diff = final_source_length - initial_source_length
            print(f"📊 Page source length changed by: {length_diff} characters")
            if length_diff > 1000:
                print("✅ Significant content was loaded during scrolling")
            else:
                print("⚠️ Little to no new content was loaded during scrolling")

    def find_hidden_elements(self):
        """Try to find hidden or lazy-loaded elements"""
        print("🔍 Looking for hidden elements...")

        # Try to expand any collapsed sections
        expand_selectors = [
            "//button[contains(., 'Expand')]",
            "//button[contains(., 'Show more')]",
            "//button[contains(@aria-label, 'Expand')]",
            "//div[contains(@class, 'expander')]//button"
        ]

        for xpath in expand_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, xpath)
                for button in buttons:
                    try:
                        if button.is_displayed():
                            button.click()
                            time.sleep(0.5)
                            print(f"✅ Expanded section: {xpath}")
                    except:
                        continue
            except:
                continue

    def extract_business_data(self):
        """Enhanced business data extraction with multiple strategies"""
        print("📝 Extracting business data...")

        # Multiple strategies to find listings
        strategies = [
            self.extract_using_css_selectors,
            self.extract_using_xpath,
            self.extract_using_aria_attributes,
        ]

        for strategy in strategies:
            if len(self.results) >= self.max_results:
                break
            try:
                strategy()
            except Exception as e:
                print(f"⚠️ Strategy failed: {e}")

    def extract_using_css_selectors(self):
        """Extract using CSS selectors"""
        selectors_to_try = [
            "div.Nv2PK",
            "div.qjESne",
            "div[role='article']",
            "div[data-index]",
            "div[jsaction*='mouseover']",
            "div.a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd",
            "div[jslog*='poi']",
            "div[jslog*='place']",
            "div[aria-label*='results'] div[role='article']",
            "div[aria-label*='Results list'] div[role['article']",
            "div[aria-label*='Results for'] div[role='article']",
            "div[aria-label*='Search results'] div[role='article']",
            "div[class*='section-result']",
            "div[class*='search-result']",
        ]

        for selector in selectors_to_try:
            if len(self.results) >= self.max_results:
                break

            try:
                listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if listings:
                    print(f"🔍 Found {len(listings)} listings with selector: {selector}")
                    self.process_listings(listings)
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")

    def extract_using_xpath(self):
        """Extract using XPath selectors"""
        xpaths_to_try = [
            "//div[contains(@class, 'section-result')]",
            "//div[contains(@class, 'search-result')]",
            "//div[@role='article']",
            "//div[contains(@jsaction, 'mouseover')]",
            "//div[@data-index]",
            "//div[contains(@aria-label, 'results')]//div[@role='article']"
        ]

        for xpath in xpaths_to_try:
            if len(self.results) >= self.max_results:
                break

            try:
                listings = self.driver.find_elements(By.XPATH, xpath)
                if listings:
                    print(f"🔍 Found {len(listings)} listings with XPath: {xpath}")
                    self.process_listings(listings)
            except Exception as e:
                print(f"⚠️ Error with XPath {xpath}: {e}")

    def extract_using_aria_attributes(self):
        """Extract using aria attributes"""
        aria_selectors = [
            "[aria-labelledby]",
            "[aria-label*='result']",
            "[aria-label*='place']",
            "[aria-label*='business']"
        ]

        for selector in aria_selectors:
            if len(self.results) >= self.max_results:
                break

            try:
                listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if listings:
                    print(f"🔍 Found {len(listings)} listings with aria selector: {selector}")
                    self.process_listings(listings)
            except Exception as e:
                print(f"⚠️ Error with aria selector {selector}: {e}")

    def process_listings(self, listings):
        """Process found listings"""
        seen = set()

        for listing in listings:
            if len(self.results) >= self.max_results:
                break

            try:
                # Create a unique ID for the listing
                listing_id = (
                        listing.get_attribute("data-index") or
                        listing.get_attribute("id") or
                        listing.get_attribute("aria-label") or
                        str(hash(listing.text[:100]))
                )

                if listing_id in seen:
                    continue

                seen.add(listing_id)

                business_data = self.extract_business_info(listing)
                if business_data and business_data.get("name"):
                    # Check for duplicates
                    is_duplicate = any(
                        existing.get("name") == business_data.get("name") and
                        existing.get("address") == business_data.get("address")
                        for existing in self.results
                    )

                    if not is_duplicate:
                        self.results.append(business_data)
                        print(f"✅ Added: {business_data['name']} - {business_data.get('rating', 'N/A')}⭐")

            except StaleElementReferenceException:
                print("⚠️ Listing became stale during processing")
            except Exception as e:
                print(f"⚠️ Error processing listing: {e}")

    def extract_business_info(self, listing):
        """Extract business information from a listing element"""
        # Try multiple selectors for name
        name = None
        name_selectors = [
            "div.qBF1Pd",
            "div.fontHeadlineSmall",
            "h2.fontHeadlineSmall",
            "div[aria-label*='restaurant']",
            "div[aria-label*='store']",
            "div[aria-label*='business']",
            "div[role='heading']",
            "h3",
            "h2",
            "div[jslog*='title']",
            "div[aria-label]",
            "a[href*='/maps/place/']",
            "div[data-index] div[aria-label]"
        ]

        for selector in name_selectors:
            try:
                name_elem = listing.find_element(By.CSS_SELECTOR, selector)
                name = name_elem.text.strip()
                if name and len(name) > 1:
                    break
            except StaleElementReferenceException:
                print("⚠️ Element became stale while extracting name")
                return None
            except:
                continue

        if not name:
            # Try to get name from aria-label
            try:
                name = listing.get_attribute("aria-label")
                if name and ("stars" in name or "reviews" in name):
                    # Extract just the name part from aria-label
                    name_parts = name.split("stars")[0].strip()
                    if name_parts:
                        name = name_parts
            except StaleElementReferenceException:
                print("⚠️ Element became stale while extracting name from aria-label")
                return None
            except:
                pass

        if not name:
            return None

        # Extract rating
        rating = None
        rating_selectors = [
            "span.MW4etd",
            "span[aria-label*='stars']",
            "span[aria-label*='rating']",
            "div[jslog*='rating']",
            "span[role='img']",
            "span[aria-label]"
        ]

        for selector in rating_selectors:
            try:
                rating_elem = listing.find_element(By.CSS_SELECTOR, selector)
                rating_text = rating_elem.text.strip()
                if rating_text:
                    # Extract numeric rating
                    rating_match = re.search(r'(\d+\.\d+)', rating_text)
                    if rating_match:
                        rating = rating_match.group(1)
                        break
                    # Check if rating is in aria-label
                    aria_label = rating_elem.get_attribute("aria-label")
                    if aria_label and "stars" in aria_label:
                        rating_match = re.search(r'(\d+\.\d+)', aria_label)
                        if rating_match:
                            rating = rating_match.group(1)
                            break
            except StaleElementReferenceException:
                print("⚠️ Element became stale while extracting rating")
                continue
            except:
                continue

        # Extract number of reviews
        reviews = None
        reviews_selectors = [
            "span.UY7F9",
            "span[aria-label*='reviews']",
            "span:not([class])",  # Fallback
            "span[jsaction*='reviews']"
        ]

        for selector in reviews_selectors:
            try:
                reviews_elem = listing.find_element(By.CSS_SELECTOR, selector)
                reviews_text = reviews_elem.text.strip()
                if reviews_text:
                    # Extract number from parentheses
                    reviews_match = re.search(r'\((\d+,?\d*)\)', reviews_text)
                    if reviews_match:
                        reviews = reviews_match.group(1).replace(",", "")
                        break
                    # If no parentheses, try to extract number directly
                    reviews_match = re.search(r'(\d+,?\d*)', reviews_text)
                    if reviews_match:
                        reviews = reviews_match.group(1).replace(",", "")
                        break
            except StaleElementReferenceException:
                print("⚠️ Element became stale while extracting reviews")
                continue
            except:
                continue

        # Try multiple selectors for category
        category = None
        category_selectors = [
            "span.YhemCb",
            "div.fontBodyMedium",
            "div.W4Efsd:last-child",
            "div[aria-label*='category']",
            "div[aria-label*='type']",
            "div[jslog*='type']",
            "span[aria-label*='category']",
            "div:not([class])",  # Fallback for any div without class
            "div.W4Efsd:nth-child(1)"
        ]

        for selector in category_selectors:
            try:
                category_elem = listing.find_element(By.CSS_SELECTOR, selector)
                category_text = category_elem.text.strip()
                if category_text and len(category_text) > 1:
                    category = category_text
                    break
            except StaleElementReferenceException:
                print("⚠️ Element became stale while extracting category")
                continue
            except:
                continue

        # Extract address
        address = None
        address_selectors = [
            "div.W4Efsd:nth-child(2)",
            "div[aria-label*='address']",
            "div[jslog*='address']",
            "div[data-item-id*='address']",
            "div.W4Efsd"
        ]

        for selector in address_selectors:
            try:
                address_elem = listing.find_element(By.CSS_SELECTOR, selector)
                address_text = address_elem.text.strip()
                if address_text and len(address_text) > 5:  # Minimum reasonable address length
                    # Check if this is actually an address (contains numbers or common address words)
                    if any(char.isdigit() for char in address_text) or any(word in address_text.lower() for word in
                                                                           ['street', 'st', 'avenue', 'ave', 'road',
                                                                            'rd', 'lane', 'ln']):
                        address = address_text
                        break
            except StaleElementReferenceException:
                print("⚠️ Element became stale while extracting address")
                continue
            except:
                continue

        # Try to click on the listing to get more details
        more_details = {}
        try:
            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listing)
            time.sleep(0.5)

            # Click on the listing
            listing.click()
            time.sleep(2)  # Wait for details to load

            # Extract phone number
            try:
                phone_elems = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "button[data-item-id*='phone'], a[href*='tel:']"))
                )
                for elem in phone_elems:
                    phone = elem.get_attribute("aria-label") or elem.text or elem.get_attribute("href")
                    if phone and any(char.isdigit() for char in phone):
                        more_details["phone"] = phone
                        break
            except:
                pass

            # Extract website
            try:
                website_elems = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "a[data-item-id*='authority'], a[href*='http']"))
                )
                for elem in website_elems:
                    website = elem.get_attribute("href")
                    if website and ("http://" in website or "https://" in website):
                        more_details["website"] = website
                        break
            except:
                pass

            # Extract hours of operation
            try:
                hours_elem = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[data-item-id*='hours'], div[aria-label*='hours']"))
                )
                hours = hours_elem.text.strip()
                if hours:
                    more_details["hours"] = hours
            except:
                pass

            # Close the details panel
            try:
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                                                          "button[aria-label*='Close'], button[jsaction*='close']")
                if close_buttons:
                    close_buttons[0].click()
                time.sleep(1)
            except:
                # If we can't find close button, try going back
                self.driver.execute_script("window.history.back()")
                time.sleep(1)

        except StaleElementReferenceException:
            print("⚠️ Element became stale while extracting additional details")
        except Exception as e:
            print(f"⚠️ Could not extract additional details: {e}")

        return {
            "name": name,
            "category": category or "N/A",
            "rating": rating or "N/A",
            "reviews": reviews or "N/A",
            "address": address or "N/A",
            **more_details
        }

    def try_alternative_queries(self):
        """Try alternative queries within the same location"""
        print("🔄 Trying alternative queries within the same location...")

        # Try different search variations within the same location
        search_variations = [
            self.query,
            f"{self.query} near me",
            f"best {self.query}",
            f"top rated {self.query}"
        ]

        for variation in search_variations:
            if len(self.results) >= self.min_results:
                break

            try:
                print(f"🔍 Trying search variation: {variation}")

                # Find the search box and enter the query
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input#searchboxinput"))
                )
                search_box.clear()
                search_box.send_keys(variation)

                # Click the search button
                search_button = self.driver.find_element(By.CSS_SELECTOR, "button#searchbox-searchbutton")
                search_button.click()
                time.sleep(3)

                # Scroll for more results
                self.scroll_for_more_results()
            except:
                continue

    def save_progress(self, filename="progress.json"):
        """Save current progress to a file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"💾 Progress saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving progress: {e}")

    def load_progress(self, filename="progress.json"):
        """Load progress from a file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.results = json.load(f)
                print(f"📂 Loaded {len(self.results)} results from {filename}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error loading progress: {e}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
            print("🔚 Browser closed")


def scrape_google_maps(query, location, max_results=30, headless=False, resume=False, min_results=10,
                       debug_dir="debug_evidence"):
    scraper = GoogleMapsBusinessScraper(query, location, max_results, headless, min_results, debug_dir)

    # Try to resume from previous progress
    if resume:
        scraper.load_progress()

    scraper.search()
    scraper.close()
    return scraper.results


if __name__ == "__main__":
    print("🚀 Starting Google Maps scraper...")
    query = "restaurants"
    location = "Manhattan, New York"
    results = scrape_google_maps(query, location, max_results=20, headless=False, resume=False, min_results=10)
    print("\n📋 Final Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('name', 'N/A')}")
        print(f"   ⭐ Rating: {result.get('rating', 'N/A')} ({result.get('reviews', 'N/A')} reviews)")
        print(f"   🏪 Category: {result.get('category', 'N/A')}")
        print(f"   📍 Address: {result.get('address', 'N/A')}")
        if result.get('phone'):
            print(f"   📞 Phone: {result.get('phone')}")
        if result.get('website'):
            print(f"   🌐 Website: {result.get('website')}")
        if result.get('hours'):
            print(f"   🕒 Hours: {result.get('hours')}")
        print()
    print(f"✅ Total results: {len(results)}")
