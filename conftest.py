"""
Pytest fixtures for Weather Shopper tests
"""
import pytest
from playwright.sync_api import Page
from factories.browser_factory import BrowserFactory
from config.config import Config
import os

def pytest_addoption(parser):
    """Add command line options to pytest"""
    parser.addoption(
        "--browser-type", 
        action="store", 
        default="chromium", 
        help="Browser to run tests on: chromium, firefox, webkit"
    )

@pytest.fixture(scope="function")
def browser_type(request):
    """Get the browser type from command line option"""
    return request.config.getoption("--browser-type")

@pytest.fixture(scope="session")
def setup():
    """Setup browser and page for testing
    
    Uses a single browser instance for the entire test session
    to improve test execution speed and ensure shared state.
    
    Yields:
        Playwright page object
    """
    # Use a fixed browser type for all tests
    browser_type = "chromium"
    # Initialize browser
    browser, playwright = BrowserFactory.get_browser(browser_type)
    
    # Create a new page
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.set_default_timeout(Config.TIMEOUT)
    
    # Yield the page to the test
    yield page
    
    # Teardown
    page.close()
    browser.close()
    playwright.stop()
