"""
Browser factory for creating browser instances
"""
from playwright.sync_api import sync_playwright
from config.config import Config

class BrowserFactory:
    """Factory class for creating browser instances"""
    
    @staticmethod
    def get_browser(browser_type="chromium"):
        """Get a browser instance
        
        Args:
            browser_type: Type of browser (chromium, firefox, webkit)
            
        Returns:
            A browser instance
        """
        playwright = sync_playwright().start()
        
        if browser_type.lower() == "chromium":
            return playwright.chromium.launch(
                headless=Config.BROWSER_OPTIONS["chrome"]["headless"]
            ), playwright
            
        elif browser_type.lower() == "firefox":
            return playwright.firefox.launch(
                headless=Config.BROWSER_OPTIONS["firefox"]["headless"]
            ), playwright
            
        elif browser_type.lower() == "webkit":
            return playwright.webkit.launch(
                headless=Config.BROWSER_OPTIONS["webkit"]["headless"]
            ), playwright
            
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
