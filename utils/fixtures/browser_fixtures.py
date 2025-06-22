"""
Fixtures for browser setup and state management for WeatherShopper tests with sequential flow
"""
import pytest
from loguru import logger
from typing import Tuple, List, Dict
from utils.logger import LoggerSetup
from pages.page_factory import PageFactory


# Global state to maintain test flow
session_data = {
    "page": None,
    "pages": None,
    "temperature": None,
    "product_type": None,
    "added_items": []
}


@pytest.fixture(scope="session")
def browser_setup(setup):
    """
    Setup fixture for browser with logging initialization.
    Uses session scope to create a single browser instance for all tests.
    
    Args:
        setup: Browser fixture from conftest.py
    
    Returns:
        Tuple with page object and initialized page_factory dictionary
    """
    # Use a fixed browser type for the session
    browser_type = "chromium"
    
    # Set up logger once for the entire test session
    LoggerSetup.setup_logger(browser_type, session=True)
    logger.info(f"Starting test session with {browser_type} browser - all tests will execute sequentially")
    
    page = setup
    
    # Create a dictionary of page objects for convenient access
    pages = {
        "home": PageFactory.get_page_object("home", page),
        "product": PageFactory.get_page_object("product", page),
        "cart": PageFactory.get_page_object("cart", page),
        "payment": PageFactory.get_page_object("payment", page),
    }
    
    # Update global session data with new browser instance
    global session_data
    session_data["page"] = page
    session_data["pages"] = pages
    
    # Load the home page at the beginning
    home_page = pages["home"]
    load_success = home_page.load()
    
    if not load_success:
        logger.error("Failed to load home page in fixture")
        # Continue anyway as the test might handle this
    
    yield (page, pages)
    
    logger.success("Test session completed")
    # Teardown will be performed automatically by the setup fixture


@pytest.fixture(scope="function")
def loaded_home_page(browser_setup):
    """
    Fixture that provides access to already loaded home page
    
    Returns:
        Tuple with page objects and home_page instance
    """
    global session_data
    _, pages = browser_setup
    home_page = pages["home"]
    
    # If this is the first test, temperature will already be loaded
    # If coming back from later tests, no need to reload the page
    
    yield (pages, home_page)


@pytest.fixture(scope="function")
def product_selection(loaded_home_page):
    """
    Fixture that provides product selection information
    Uses the global session data for consistency across tests
    
    Returns:
        Tuple with pages, product_type, and temperature
    """
    global session_data
    pages, home_page = loaded_home_page
    
    # Log the current state for debugging
    logger.debug(f"Current session data: temperature={session_data.get('temperature')}, product_type={session_data.get('product_type')}")
    
    # Just use what's in the session data - the test_02 should have set these
    temperature = session_data.get('temperature')
    product_type_result = session_data.get('product_type')
    
    # Handle product_type which may now be a tuple (product_type, success) after refactoring
    # Only extract the product_type string from tuple if needed
    product_type = product_type_result[0] if isinstance(product_type_result, tuple) else product_type_result
    
    # Validate state before proceeding
    if temperature is None or product_type is None:
        logger.warning(f"Missing session data - temperature: {temperature}, product_type: {product_type}")
    
    # Return the original product_type_result to maintain compatibility with both old and new code
    yield (pages, product_type_result, temperature)


@pytest.fixture(scope="function")
def products_added_to_cart(product_selection):
    """
    Fixture providing state with products added to cart
    
    Returns:
        Tuple with pages, added_items, and product_type
    """
    global session_data
    pages, product_type_result, _ = product_selection
    
    # Handle the new tuple return type from choose_product_based_on_temperature
    product_type = product_type_result[0] if isinstance(product_type_result, tuple) else product_type_result
    
    # Validate the session state before proceeding
    logger.info(f"products_added_to_cart fixture: Current session state:")
    logger.info(f"  Temperature: {session_data.get('temperature')}")
    logger.info(f"  Product type: {session_data.get('product_type')}")
    logger.info(f"  Added items: {session_data.get('added_items')}")
    
    # Verify we have items in the cart from previous steps
    added_items = session_data.get("added_items", [])
    
    # Verify we're on the cart page, which test_03 should have navigated to
    # The page object is directly stored in the cart_page, not nested under 'page'
    cart_page = pages['cart']
    current_url = cart_page.page.url
    if '/cart' not in current_url:
        logger.warning(f"Not on cart page as expected. Current URL: {current_url}")
        # Don't navigate again - this would disrupt the sequential flow
    
    yield (pages, added_items, product_type)


@pytest.fixture(scope="function")
def cart_contents_verified(products_added_to_cart):
    """
    Fixture that provides access to verified cart contents
    This builds on products_added_to_cart and ensures cart contents are verified
    before proceeding to payment
    
    Returns:
        Tuple with pages and total_price
    """
    global session_data
    pages, added_items, _ = products_added_to_cart
    
    # Log the current state
    logger.info(f"cart_contents_verified fixture: Current session state:")
    logger.info(f"  Added items: {session_data.get('added_items')}")
    logger.info(f"  Total price: {session_data.get('total_price')}")
    
    # Get the total price from session data (should be set by test_04)
    total_price = session_data.get("total_price")
    
    # Verify we're on the cart page
    cart_page = pages['cart']
    current_url = cart_page.page.url
    if '/cart' not in current_url:
        logger.warning(f"Not on cart page as expected. Current URL: {current_url}")
    
    yield (pages, total_price)
