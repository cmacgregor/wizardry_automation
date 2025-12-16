import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class WizardryBot:
    def __init__(self, config_file='config.json'):
        """Initialize the bot with configuration."""
        # Load config file if it exists
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Use defaults if no config file (Docker mode)
            self.config = {
                'website_url': 'https://store.wizardry.info/',
                'button_selector': {
                    'type': 'data-testid',
                    'value': 'free-button'
                },
                'wait_time': 15,
                'headless': True
            }

        # Override/set user_id from environment variable (required for Docker)
        env_user_id = os.getenv('USER_ID')
        if env_user_id:
            self.config['user_id'] = env_user_id
            print(f"Using USER_ID from environment variable")

        # Validate user_id is set
        if not self.config.get('user_id') or self.config['user_id'] == 'YOUR_USER_ID_HERE':
            raise ValueError("USER_ID must be set in config.json or USER_ID environment variable")

        self.driver = None

    def setup_driver(self):
        """Set up the Chrome WebDriver."""
        import subprocess

        # Diagnostic: Check Chrome/Chromium installation
        try:
            chrome_version = subprocess.run(['google-chrome-stable', '--version'],
                                          capture_output=True, text=True, timeout=5)
            print(f"Chrome version: {chrome_version.stdout.strip()}")
        except Exception as e:
            print(f"google-chrome-stable not found: {e}")
            try:
                chromium_version = subprocess.run(['chromium', '--version'],
                                                capture_output=True, text=True, timeout=5)
                print(f"Chromium version: {chromium_version.stdout.strip()}")
            except Exception as e2:
                print(f"chromium not found either: {e2}")

        options = webdriver.ChromeOptions()

        if self.config.get('headless', False):
            options.add_argument('--headless=new')  # Use new headless mode

        # Essential arguments for Docker/containerized environments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-setuid-sandbox')

        # Completely disable crash reporting and breakpad
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--crash-dumps-dir=/tmp')  # Set crash dump dir to prevent handler errors
        options.add_argument('--disable-breakpad')

        # Anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Use pre-installed chromedriver if available (for Docker with read-only filesystem)
        # Otherwise, Selenium will auto-download the driver
        chromedriver_path = '/usr/local/bin/chromedriver'
        if os.path.exists(chromedriver_path):
            print(f"Using pre-installed ChromeDriver at {chromedriver_path}")
            # Enable verbose logging for debugging
            service = Service(
                executable_path=chromedriver_path,
                service_args=['--verbose', '--log-path=/tmp/chromedriver.log']
            )
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            print("ChromeDriver not found at /usr/local/bin/chromedriver, using Selenium WebDriver Manager")
            self.driver = webdriver.Chrome(options=options)

        self.driver.maximize_window()

    def navigate_to_site(self):
        """Navigate to the Wizardry store."""
        print(f"Navigating to {self.config['website_url']}...")
        self.driver.get(self.config['website_url'])
        time.sleep(3)

    def handle_gdpr_popup(self):
        """Handle GDPR cookie consent popup."""
        print("Checking for GDPR cookie consent popup...")
        try:
            # Look for common GDPR accept buttons
            gdpr_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".gdpr-buttons button, [class*='gdpr'] button, [class*='cookie'] button")

            if gdpr_buttons:
                print(f"Found {len(gdpr_buttons)} GDPR button(s), clicking the first one...")
                gdpr_buttons[0].click()
                time.sleep(2)
                print("GDPR popup handled")
            else:
                print("No GDPR popup found")
        except Exception as e:
            print(f"Note: Could not handle GDPR popup: {str(e)}")
            # Continue anyway

    def login(self):
        """Log in using the configured User ID via quick login."""
        print("Attempting to log in using quick login...")
        wait = WebDriverWait(self.driver, self.config.get('wait_time', 5))

        try:
            # Wait for page to fully load after GDPR
            print("Waiting for page to fully load...")
            time.sleep(4)

            # Scroll down to find the fast-login section
            print("Scrolling to find quick login section...")
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)

            # Find the fast-login container specifically
            print("Looking for .fast-login container...")
            fast_login_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".fast-login, .block--index-8"))
            )

            # Scroll the container into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fast_login_container)
            time.sleep(1)

            # Find the input field within the fast-login container
            print("Looking for input field in fast-login container...")
            user_id_input = fast_login_container.find_element(By.CSS_SELECTOR, "input#user-id-input, .fast-login__input-container input")

            # Click and enter the User ID
            print("Attempting to enter User ID...")
            user_id_input.click()
            time.sleep(0.5)
            user_id_input.send_keys(self.config['user_id'])
            time.sleep(1)
            print(f"Entered User ID: {self.config['user_id']}")

            # Find and click the login button in the fast-login container
            print("Looking for quick login button in container...")
            time.sleep(1)

            # Try to find the button within the fast-login container
            try:
                login_button = fast_login_container.find_element(By.CSS_SELECTOR, ".fast-login__input-container-button, [data-testid='fast-login-button-authorization-user-id']")
            except:
                # Fallback: try finding it by data-testid globally
                login_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='fast-login-button-authorization-user-id']"))
                )

            login_button.click()
            print("Clicked quick login button")

            # Wait for login to process
            time.sleep(5)
            print("Login complete")

        except TimeoutException:
            print("Error: Could not find quick login elements. The page structure may have changed.")
            raise

    def handle_popup(self):
        """Handle any remaining popups after login."""
        print("Checking for any remaining popups...")
        time.sleep(2)

        try:
            # Check if there are multiple windows (popup window)
            if len(self.driver.window_handles) > 1:
                print("Found popup window, switching to main window...")
                self.driver.switch_to.window(self.driver.window_handles[0])

            # Check if login popup is still there and try to close it
            try:
                # Look for close buttons but be more selective
                close_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'close') or contains(@aria-label, 'close')]")
                if close_buttons and len(close_buttons) > 0:
                    # Check if it's visible
                    if close_buttons[0].is_displayed():
                        print(f"Found visible close button, clicking it...")
                        close_buttons[0].click()
                        time.sleep(1)
            except:
                pass

            print("Ready to proceed")

        except Exception as e:
            print(f"Note: {str(e)}")
            # Continue anyway

    def click_button(self):
        """Click the configured button."""
        print("Looking for the target button...")
        wait = WebDriverWait(self.driver, self.config.get('wait_time', 5))

        button_config = self.config.get('button_selector', {})
        selector_type = button_config.get('type', 'text')
        selector_value = button_config.get('value', '')

        try:
            # Scroll down to load more content (Free Items section might be lower on page)
            print("Scrolling down to load Free Items section...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(3)

            if selector_type == 'text':
                # Find button by text content
                print(f"Searching for button with text: '{selector_value}'...")
                button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{selector_value}')]"))
                )
            elif selector_type == 'id':
                button = wait.until(
                    EC.element_to_be_clickable((By.ID, selector_value))
                )
            elif selector_type == 'class':
                button = wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, selector_value))
                )
            elif selector_type == 'data-testid':
                print(f"Searching for button with data-testid: '{selector_value}'...")
                button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-testid='{selector_value}']"))
                )
            elif selector_type == 'xpath':
                button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector_value))
                )
            else:
                raise ValueError(f"Unknown selector type: {selector_type}")

            button.click()
            print(f"Successfully clicked button with {selector_type}: {selector_value}")
            time.sleep(2)

        except TimeoutException:
            print(f"Error: Could not find button with {selector_type}: {selector_value}")
            raise

    def run(self):
        """Execute the full automation workflow."""
        try:
            self.setup_driver()
            self.navigate_to_site()
            self.handle_gdpr_popup()
            self.login()
            self.handle_popup()
            self.click_button()

            print("\nAutomation completed successfully!")
            print("Browser will remain open for 10 seconds...")
            time.sleep(10)

        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print("Browser will remain open for 30 seconds for debugging...")
            time.sleep(30)
            raise

        finally:
            if self.driver:
                self.driver.quit()
                print("Browser closed.")

if __name__ == "__main__":
    print("=== Wizardry Store Automation Bot ===\n")

    bot = WizardryBot('config.json')
    bot.run()
