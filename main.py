from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import time
import logging
import json
from typing import List, Dict

class InstagramBot:
    def __init__(self, username: str, password: str, config_path: str = 'config.json'):
        """Initialize the Instagram bot with user credentials and configuration."""
        self.username = username
        self.password = password
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.setup_driver()
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "wait_time": {
                    "min": 2,
                    "max": 4
                },
                "posts_per_user": 3,
                "max_likes_per_session": 50,
                "random_comments": [
                    "Great post! 👍",
                    "Amazing! 🔥",
                    "Love this! ❤️",
                    "Awesome content! ✨"
                ],
                "comment_probability": 0.2
            }

    def setup_logging(self):
        """Configure logging for the bot."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('instagram_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        """Set up and configure the Chrome WebDriver with optimal settings."""
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def random_sleep(self, min_time: float = None, max_time: float = None):
        """Sleep for a random amount of time within the specified range."""
        min_time = min_time or self.config['wait_time']['min']
        max_time = max_time or self.config['wait_time']['max']
        time.sleep(random.uniform(min_time, max_time))

    def login(self) -> bool:
        """Log in to Instagram with error handling."""
        try:
            self.logger.info(f"Attempting to log in as {self.username}")
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for and fill in login forms
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            password_input.submit()
            
            # Wait for login to complete
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main[role='main']"))
            )
            
            self.logger.info("Successfully logged in")
            return True
            
        except TimeoutException:
            self.logger.error("Login failed - timeout while waiting for elements")
            return False
        except Exception as e:
            self.logger.error(f"Login failed - unexpected error: {str(e)}")
            return False

    def interact_with_user(self, username: str):
        """Interact with a specific user's posts."""
        try:
            self.logger.info(f"Navigating to {username}'s profile")
            self.driver.get(f"https://www.instagram.com/{username}/")
            self.random_sleep()

            # Get posts
            posts = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article a"))
            )[:self.config['posts_per_user']]

            for i, post in enumerate(posts):
                try:
                    post.click()
                    self.random_sleep()
                    
                    # Like the post
                    like_button = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Like']"))
                    )
                    if like_button:
                        like_button.click()
                        self.logger.info(f"Liked post {i+1} from {username}")
                    
                    # Potentially leave a comment
                    if random.random() < self.config['comment_probability']:
                        self.leave_comment(random.choice(self.config['random_comments']))
                    
                    # Close post
                    close_button = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']"))
                    )
                    close_button.click()
                    self.random_sleep()

                except Exception as e:
                    self.logger.error(f"Error interacting with post {i+1}: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error accessing {username}'s profile: {str(e)}")

    def leave_comment(self, comment_text: str):
        """Leave a comment on the current post."""
        try:
            comment_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label='Add a comment…']"))
            )
            comment_input.click()
            comment_input.send_keys(comment_text)
            comment_input.submit()
            self.logger.info(f"Left comment: {comment_text}")
            self.random_sleep()
        except Exception as e:
            self.logger.error(f"Failed to leave comment: {str(e)}")

    def cleanup(self):
        """Clean up resources and close the browser."""
        try:
            self.driver.quit()
            self.logger.info("Bot session ended, browser closed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def run(self, target_users: List[str] | str):
        """Run the bot for the specified target users."""
        try:
            # Convert single username to list if necessary
            if isinstance(target_users, str):
                target_users = [target_users]
            
            if not self.login():
                return
            
            for username in target_users:
                self.interact_with_user(username)
                self.random_sleep(4, 7)  # Longer wait between users
                
        except Exception as e:
            self.logger.error(f"Bot execution failed: {str(e)}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    # Configuration
    USERNAME = "sandanu_hewage"
    PASSWORD = ""
    
    # List of target users
    TARGET_USERS = [
        "chairo_store101",
        "sandanu_hewage"
    ]
    
    # Initialize and run bot
    bot = InstagramBot(USERNAME, PASSWORD)
    # Pass the list of usernames, not individual arguments
    bot.run(TARGET_USERS)
