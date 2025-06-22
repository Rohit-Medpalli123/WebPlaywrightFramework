"""
Base Page class that all page objects will inherit from
"""
from playwright.sync_api import Page
import re

class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, page: Page):
        """Initialize the base page with Playwright page object
        
        Args:
            page: Playwright page object
        """
        self.page = page
    
    def navigate(self, url: str) -> None:
        """Navigate to the specified URL
        
        Args:
            url: The URL to navigate to
        """
        self.page.goto(url)
    
    def get_text(self, locator: str) -> str:
        """Get the text content of an element
        
        Args:
            locator: The XPath or CSS locator
        
        Returns:
            The text content of the element
        """
        return self.page.locator(locator).text_content().strip()
    
    def click(self, locator: str) -> None:
        """Click on an element
        
        Args:
            locator: The XPath or CSS locator
        """
        self.page.locator(locator).click()
    
    def extract_price(self, price_text: str) -> int:
        """Extract the price as an integer from price text
        
        Args:
            price_text: String containing price (e.g., "Price: Rs. 200")
        
        Returns:
            The price as an integer
        """
        match = re.search(r'(\d+)', price_text)
        if match:
            return int(match.group(1))
        return 0
    
    def extract_number_from_text(self, text: str) -> int:
        """Extract a number from text
        
        Args:
            text: String containing a number
            
        Returns:
            The extracted number as an integer
        """
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        return 0
    
    def is_visible(self, locator: str) -> bool:
        """Check if element is visible
        
        Args:
            locator: The XPath or CSS locator
            
        Returns:
            True if element is visible, False otherwise
        """
        return self.page.locator(locator).is_visible()
