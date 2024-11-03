import os
from src.config import settings
from src.api import TokenManager
from src.webhook import WebhookManager
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from loguru import logger

WEBHOOK = WebhookManager(
    webhook_uri=settings.WEBHOOK_URI,
    bot_id=settings.BOT_ID,
)

class AIHawkAuthenticator:

    def __init__(self, driver=None):
        self.driver = driver
        logger.debug(f"AIHawkAuthenticator initialized with driver: {driver}")

    def start(self):
        logger.info("Starting Chrome browser to log in to AIHawk.")
        if self.is_logged_in():
            logger.info("User is already logged in. Skipping login process.")
            return
        else:
            logger.info("User is not logged in. Proceeding with login.")
            self.handle_login()

    def handle_login(self):
        logger.info("Navigating to the AIHawk login page...")
        self.driver.get("https://www.linkedin.com/login")
        if 'feed' in self.driver.current_url:
            logger.debug("User is already logged in.")
            return
        try:
            self.enter_credentials()
            self.click_login_button()
        except NoSuchElementException as e:
            logger.error(f"Could not log in to AIHawk. Element not found: {e}")
        self.handle_security_check()


    def enter_credentials(self):
        try:
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            # ensure the email field is clean:
            email_field.clear()
            email_field.send_keys(settings.LINKEDIN_EMAIL)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(settings.LINKEDIN_PASSWORD)
        except TimeoutException:
            print("Login form not found. Aborting login.")
    
    def click_login_button(self):
        try:
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()
        except NoSuchElementException:
            print("Login button not found. Please verify the page structure.")


    def handle_security_check(self):
        try:
            logger.debug("Handling security check...")
            if 'checkpoint' in self.driver.current_url:
                logger.warning("Security checkpoint detected. Please complete the challenge.")
                WEBHOOK.send_request_token("Please provide the verification code to continue.")
                self.handle_security_checkpoint()
            WebDriverWait(self.driver, 300).until(
                EC.url_contains('https://www.linkedin.com/feed/')
            )
            logger.info("Security check completed")
        except TimeoutException:
            logger.error("Security check not completed. Please try again later.")
            
    def handle_security_checkpoint(self):
        input_elements = self.driver.find_elements(By.CLASS_NAME, "input_verification_pin")
        submit_buttons = self.driver.find_elements(By.ID, "email-pin-submit-button")
        token = TokenManager().wait_for_token()
        for i, input_element in enumerate(input_elements):
            try:
                print(f"Entering key to input {i} with text: {input_element.text if hasattr(input_element, 'text') else 'Não tem texto'}")
                input_element.send_keys(token)
            except Exception as e:
                print(f"Error entering key to input {i}: {e}")
        # now sleep for a few seconds to allow the user to complete the security check
        time.sleep(0.2)
        for i, submit_button in enumerate(submit_buttons):
            try:
                logger.debug(f"Clicking submit button {i}")
                submit_button.click()
                if 'checkpoint' in self.driver.current_url:
                    print("still in checkpoint...")
                    continue
            except Exception as e:
                print(f"Error clicking submit button {i}: {e}")

    def is_logged_in(self):
        try:
            self.driver.get('https://www.linkedin.com/feed')
            logger.debug("Checking if user is logged in...")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'share-box-feed-entry__trigger'))
            )

            # Check for the presence of the "Start a post" button
            buttons = self.driver.find_elements(By.CLASS_NAME, 'share-box-feed-entry__trigger')
            logger.debug(f"Found {len(buttons)} 'Start a post' buttons")

            for i, button in enumerate(buttons):
                logger.debug(f"Button {i + 1} text: {button.text.strip()}")

            if any(button.text.strip().lower() == 'start a post' for button in buttons):
                logger.info("Found 'Start a post' button indicating user is logged in.")
                return True

            profile_img_elements = self.driver.find_elements(By.XPATH, "//img[contains(@alt, 'Photo of')]")
            if profile_img_elements:
                logger.info("Profile image found. Assuming user is logged in.")
                return True

            logger.info("Did not find 'Start a post' button or profile image. User might not be logged in.")
            return False

        except TimeoutException:
            logger.error("Page elements took too long to load or were not found.")
            return False