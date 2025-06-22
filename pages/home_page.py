"""
Home page of Weather Shopper application
"""
import re
from typing import Union, Tuple, Optional
from playwright.sync_api import Page, expect
from loguru import logger

from pages.base_page import BasePage
from locators.locators import HomePageLocators
from config.config import Config
from utils.test_helpers import (
    verify_navigation, 
    verify_element_visible, 
    verify_text_content,
    capture_failure_artifacts
)

class HomePage(BasePage):
    """Home page class for Weather Shopper application"""
    
    def __init__(self, page):
        """Initialize the home page
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = Config.BASE_URL
        
    def load(self) -> bool:
        """Load the home page and verify it loaded successfully
        
        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading home page: {self.url}")
            self.navigate(self.url)
            
            # Verify page loaded successfully
            verify_element_visible(self.page, HomePageLocators.TEMPERATURE)
            logger.success("Home page loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load home page: {str(e)}")
            capture_failure_artifacts(self.page, "home_page_load_error")
            return False
        
    def get_temperature(self) -> Union[int, None]:
        """Get the current temperature
        
        Uses helper functions to ensure the temperature element is visible
        before extracting its value. Includes error handling and artifacts.
        
        Returns:
            int: Temperature as an integer, or None if extraction fails
            
        Raises:
            Exception: If temperature cannot be found or extracted
        """
        try:
            # Use helper to verify temperature element is visible and contains digits
            temp_element = verify_element_visible(self.page, HomePageLocators.TEMPERATURE)
            verify_text_content(self.page, HomePageLocators.TEMPERATURE, re.compile(r"\d+"))
            
            # Extract temperature value
            temp_text = temp_element.text_content()
            temperature = self.extract_number_from_text(temp_text)
            
            if temperature is not None:
                logger.info(f"Current temperature: {temperature}°C")
                return temperature
            else:
                logger.error("Could not extract temperature value from text")
                capture_failure_artifacts(self.page, "temperature_extraction_error")
                raise ValueError(f"Could not extract temperature from '{temp_text}'")
                
        except Exception as e:
            logger.error(f"Error getting temperature: {str(e)}")
            capture_failure_artifacts(self.page, "get_temperature_error")
            raise
    
    def navigate_to_product_page(self, product_type: str) -> bool:
        """Click product type button and verify navigation
        
        Args:
            product_type: Type of product ("moisturizer" or "sunscreen")
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        # Get product configuration from central Config
        if product_type not in Config.PRODUCT_MAP:
            logger.error(f"Invalid product type: {product_type}")
            return False
            
        # Retrieve config and map button name to actual selector
        config = Config.PRODUCT_MAP[product_type]
        button_selector = getattr(HomePageLocators, config["button_name"])
        
        try:
            logger.info(f"Clicking Buy {config['log_name']} button")
            
            # Click and wait for navigation with expect
            with self.page.expect_navigation():
                self.page.click(button_selector)
            
            # Use our helper functions to verify navigation
            verify_navigation(self.page, config['url_part'], config['heading'])
            
            logger.success(f"Successfully navigated to {config['log_name']} page: {self.page.url}")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to {config['log_name']}: {str(e)}")
            capture_failure_artifacts(self.page, f"buy_{config['log_name']}_error")
            return False

    def buy_moisturizers(self) -> bool:
        """Click on the Buy Moisturizers button and verify navigation
        
        Uses helper functions to verify successful navigation to moisturizers page.
        Includes error handling and failure artifacts.
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        return self.navigate_to_product_page("moisturizer")
        
    def buy_sunscreens(self) -> bool:
        """Click on the Buy Sunscreens button and verify navigation
        
        Uses helper functions to verify successful navigation to sunscreens page.
        Includes error handling and failure artifacts.
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        return self.navigate_to_product_page("sunscreen")
        
    def choose_product_based_on_temperature(self, temperature=None) -> Tuple[str, bool]:
        """Choose product (moisturizer or sunscreen) based on the temperature
        
        Includes enhanced error handling and logging. Returns both the product type and
        a success indicator so that tests can handle navigation failures gracefully.
        
        Args:
            temperature: Optional temperature value. If None, will get temperature from page
        
        Returns:
            Tuple[str, bool]: (product_type, success_status) where product_type is
                              "moisturizer" or "sunscreen" and success_status indicates
                              if the navigation succeeded
        """
        try:
            logger.info(f"Using provided temperature: {temperature}°C")
            
            # Determine product type based on temperature
            if temperature < 19:
                logger.info(f"Temperature {temperature}°C is below 19°C - choosing moisturizers")
                navigation_success = self.buy_moisturizers()
                return ("moisturizer", navigation_success)
                
            elif temperature > 34:
                logger.info(f"Temperature {temperature}°C is above 34°C - choosing sunscreens")
                navigation_success = self.buy_sunscreens()
                return ("sunscreen", navigation_success)
                
            else:
                # Temperature is between 19 and 34 - default to moisturizer
                logger.info(f"Temperature {temperature}°C is between 19-34°C - defaulting to moisturizers")
                navigation_success = self.buy_moisturizers()
                return ("moisturizer", navigation_success)
                
        except Exception as e:
            logger.error(f"Error during product selection: {str(e)}")
            capture_failure_artifacts(self.page, "product_selection_error")
            # Default to moisturizer on error, but indicate failure
            return ("moisturizer", False)
