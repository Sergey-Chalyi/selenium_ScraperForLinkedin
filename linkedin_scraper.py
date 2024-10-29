import logging
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import undetected_chromedriver
from dotenv import load_dotenv
import os
import pickle

# Constants for timeouts and delays
CAPTCHA_TIMEOUT = 300  # Maximum time to wait for manual CAPTCHA solve (5 minutes)
LOGIN_WAIT_TIMEOUT = 10  # Seconds to wait for login elements
TYPE_DELAY_MIN = 0.1  # Minimum delay between keystrokes
TYPE_DELAY_MAX = 0.3  # Maximum delay between keystrokes
PAGE_LOAD_DELAY_MIN = 1  # Minimum delay after page load
PAGE_LOAD_DELAY_MAX = 3  # Maximum delay after page load
PROFILE_ELEMENT_TIMEOUT = 5  # Seconds to wait for profile elements

# Constants for file paths
COOKIES_FILE = "linkedin_cookies.pkl"
LOG_FILE = "out.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class LinkedInScraper:
    class CaptchaHandler:
        """
        Internal class for handling CAPTCHA challenges.
        Implements multiple strategies for CAPTCHA detection and bypass.
        """

        def __init__(self, driver, cookies_file):
            """
            Initialize CaptchaHandler with WebDriver and cookies file path.

            Args:
                driver: Selenium WebDriver instance
                cookies_file: Path to store/retrieve cookies
            """
            self.driver = driver
            self.cookies_file = cookies_file

        def handle_captcha(self):
            """
            Attempt to handle CAPTCHA using multiple strategies.

            Returns:
                bool: True if CAPTCHA was handled successfully, False otherwise
            """
            try:
                if not self.check_for_captcha():
                    return True

                logging.info("CAPTCHA detected, attempting to handle...")

                # List of strategies to try in order
                strategies = [
                    self.try_cookies_auth,
                    self.try_stealth_mode,
                    self.wait_for_manual_solve
                ]

                for strategy in strategies:
                    if strategy():
                        logging.info(f"Successfully handled CAPTCHA using {strategy.__name__}")
                        return True

                logging.error("All CAPTCHA handling strategies failed")
                return False

            except Exception as e:
                logging.error(f"Error handling CAPTCHA: {str(e)}")
                return False

        def check_for_captcha(self):
            """
            Check for various types of CAPTCHA indicators on the page.

            Returns:
                bool: True if CAPTCHA is detected, False otherwise
            """
            captcha_indicators = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//iframe[contains(@src, 'challenges')]",
                "//div[contains(@class, 'captcha')]",
                "//div[contains(text(), 'security check')]",
                "//div[contains(text(), 'Please verify')]"
            ]

            for indicator in captcha_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        return True
                except:
                    continue
            return False

        def try_cookies_auth(self):
            """
            Attempt to bypass CAPTCHA using saved cookies.

            Returns:
                bool: True if successful, False otherwise
            """
            try:
                if os.path.exists(self.cookies_file):
                    cookies = pickle.load(open(self.cookies_file, "rb"))
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                    self.driver.refresh()
                    return not self.check_for_captcha()
                return False
            except:
                return False

        def save_cookies(self):
            """Save current session cookies for future use."""
            try:
                cookies = self.driver.get_cookies()
                pickle.dump(cookies, open(self.cookies_file, "wb"))
                logging.info("Cookies saved successfully")
            except Exception as e:
                logging.error(f"Error saving cookies: {str(e)}")

        def wait_for_manual_solve(self, timeout=CAPTCHA_TIMEOUT):
            """
            Wait for manual CAPTCHA solution.

            Args:
                timeout: Maximum time to wait in seconds

            Returns:
                bool: True if CAPTCHA is solved, False if timeout reached
            """
            try:
                logging.info("Waiting for manual CAPTCHA solve...")
                start_time = time.time()

                while time.time() - start_time < timeout:
                    if not self.check_for_captcha():
                        self.save_cookies()
                        return True
                    time.sleep(5)

                return False
            except:
                return False

        def try_stealth_mode(self):
            """
            Attempt to bypass CAPTCHA using human-like behavior.

            Returns:
                bool: True if successful, False otherwise
            """
            try:
                # Simulate random mouse movements
                action = ActionChains(self.driver)
                for _ in range(random.randint(3, 7)):
                    x = random.randint(100, 700)
                    y = random.randint(100, 500)
                    action.move_by_offset(x, y)
                    action.pause(random.uniform(TYPE_DELAY_MIN, TYPE_DELAY_MAX))
                action.perform()

                # Simulate natural scrolling
                self.driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)})")
                time.sleep(random.uniform(PAGE_LOAD_DELAY_MIN, PAGE_LOAD_DELAY_MAX))

                return not self.check_for_captcha()
            except:
                return False

    def __init__(self):
        """Initialize the LinkedIn scraper with configuration from environment variables."""
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.driver = None
        self.cookies_file = COOKIES_FILE
        self.setup_driver()
        self.captcha_handler = self.CaptchaHandler(self.driver, self.cookies_file)

    def setup_driver(self):
        """Configure and initialize the Chrome WebDriver with anti-detection measures."""
        options = undetected_chromedriver.ChromeOptions()
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-notifications')

        self.driver = undetected_chromedriver.Chrome(options=options)
        logging.info("WebDriver initialized successfully")

    def login(self):
        """
        Perform LinkedIn login with anti-detection measures.

        Raises:
            Exception: If login fails or CAPTCHA cannot be handled
        """
        try:
            self.driver.get('https://www.linkedin.com/login')
            logging.info("Accessing LinkedIn login page")
            self.add_random_delay()

            if self.captcha_handler.check_for_captcha():
                if not self.captcha_handler.handle_captcha():
                    raise Exception("Failed to handle CAPTCHA")

            # Enter credentials with human-like typing
            email_field = WebDriverWait(self.driver, LOGIN_WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            self.type_like_human(email_field, self.email)

            password_field = self.driver.find_element(By.ID, "password")
            self.type_like_human(password_field, self.password)

            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            logging.info("Login attempt successful")

            self.captcha_handler.save_cookies()

        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            raise

    def get_profile_photo(self, profile_url):
        """
        Extract profile photo URL from a LinkedIn profile.

        Args:
            profile_url: URL of the LinkedIn profile

        Returns:
            str or None: Profile photo URL if found, None otherwise
        """
        try:
            self.driver.get(profile_url)
            logging.info(f"Accessing profile: {profile_url}")
            self.add_random_delay(PAGE_LOAD_DELAY_MIN, PAGE_LOAD_DELAY_MAX)

            if self.captcha_handler.check_for_captcha():
                if not self.captcha_handler.handle_captcha():
                    raise Exception("Failed to handle CAPTCHA")

            # List of possible selectors for profile photo
            selectors = [
                "button.profile-photo-edit__edit-btn img.profile-photo-edit__preview",
                "img.pv-top-card-profile-picture__image",
                ".profile-photo-edit__edit-btn img",
                "//img[contains(@class, 'profile-photo-edit__preview')]"
            ]

            photo_url = None
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        photo_element = WebDriverWait(self.driver, PROFILE_ELEMENT_TIMEOUT).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        photo_element = WebDriverWait(self.driver, PROFILE_ELEMENT_TIMEOUT).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )

                    photo_url = photo_element.get_attribute('src')
                    if photo_url:
                        logging.info(f"Found photo URL using selector: {selector}")
                        break
                except:
                    continue

            if photo_url:
                logging.info(f"Successfully extracted photo URL: {photo_url}")
                return photo_url
            else:
                logging.error("Could not find photo URL with any selector")
                return None

        except Exception as e:
            logging.error(f"Failed to extract profile photo: {str(e)}")
            return None

    def add_random_delay(self, min_delay=PAGE_LOAD_DELAY_MIN, max_delay=PAGE_LOAD_DELAY_MAX):
        """Add random delay to simulate human behavior."""
        time.sleep(random.uniform(min_delay, max_delay))

    def type_like_human(self, element, text):
        """
        Simulate human-like typing with random delays between keystrokes.

        Args:
            element: WebElement to type into
            text: Text to type
        """
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(TYPE_DELAY_MIN, TYPE_DELAY_MAX))

    def close(self):
        """Close the browser and cleanup resources."""
        self.driver.quit()
        logging.info("Browser session closed")


def main():
    """Main execution function."""
    scraper = None
    try:
        scraper = LinkedInScraper()
        scraper.login()

        profile_url = "https://www.linkedin.com/in/sergey-chalyi-b0146a298/"
        photo_url = scraper.get_profile_photo(profile_url)

        if photo_url:
            logging.info(f"Successfully retrieved photo URL: {photo_url}")

    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()