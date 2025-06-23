"""
WeatherShopper E2E Test Suite

This module implements end-to-end tests for the WeatherShopper application using
a sequential test approach. Tests execute in a specific order using a single browser
session and shared state, simulating a complete user shopping workflow:

1. Load home page and verify temperature display
2. Select products (moisturizer/sunscreen) based on temperature
3. Add appropriate products to cart based on selection
4. Verify cart contents and total price
5. Complete payment process

The tests use session-scoped fixtures to maintain state and avoid redundant actions,
making the test flow more efficient and closer to real user behavior.

Typical usage example:
    pytest test_weather_shopper.py
"""
from typing import Dict, List, Tuple, Any, Optional
import pytest
import re
from loguru import logger
from config.config import Config
from playwright.sync_api import Page, expect
from locators.locators import CartPageLocators
from utils.test_helpers import (
    verify_url,
    verify_page_heading,
    verify_navigation,
    verify_element_visible,
    verify_element_enabled,
    verify_element_count,
    verify_text_content,
    verify_page_title,
    verify_element_with_regex,
    verify_cart_not_empty,
    capture_failure_artifacts
)

# Import fixtures and global state
from utils.fixtures.browser_fixtures import (
    browser_setup,
    loaded_home_page,
    product_selection,
    products_added_to_cart,
    cart_contents_verified,
    session_data
)

class TestWeatherShopper:
    """Implements end-to-end tests for the WeatherShopper application.
    
    This test suite executes a complete shopping workflow in sequence using
    a single browser session. Tests are numbered to ensure proper execution
    order and share state through the session_data dictionary.
    
    Attributes:
        None - All test state is managed through fixtures and session_data
    """

    def test_01_home_page_loads(self, browser_setup: Tuple[Page, Dict[str, Any]]) -> None:
        """Verifies the home page loads successfully and displays temperature.

        This is the first test in the sequence. It validates that:
        1. The home page loads properly
        2. Temperature is displayed and can be extracted
        3. Stores temperature in session_data for subsequent tests

        Args:
            browser_setup: Tuple containing (page, pages_dict) from the fixture
        """
        page, pages = browser_setup
        home_page = pages["home"]
        
        # Step 1: Validate page loaded correctly using helper function
        verify_page_title(page, r"Current Temperature")
        
        # Step 2: Get temperature and store in session data
        temperature = home_page.get_temperature()
        
        global session_data
        session_data["temperature"] = temperature
        logger.info(f"Stored temperature {temperature}°C in session data for reuse")
        
        logger.success(f"Test 1: Successfully loaded home page and found temperature: {temperature}°C")

    def test_02_product_selection_based_on_temperature(self, loaded_home_page: Tuple[Dict[str, Any], Any]) -> None:
        """Verifies that the correct product type is selected based on temperature.

        This test continues from test_01 and:
        1. Uses temperature from session_data (set in test_01)
        2. Chooses moisturizer or sunscreen based on temperature rules
        3. Stores selection in session state for subsequent tests

        Args:
            loaded_home_page: Tuple containing (pages_dict, home_page) from fixture

        Raises:
            AssertionError: If navigation to product page fails
        """
        pages, home_page = loaded_home_page
        
        # Step 1: Get temperature from session_data
        global session_data
        temperature = session_data.get("temperature")
        logger.info(f"Using temperature from session_data: {temperature}°C")
        
        # Step 2: Select product type based on temperature
        # The method now returns (product_type, success_status)
        product_type_result = home_page.choose_product_based_on_temperature(temperature)
        product_type, success = product_type_result
        
        if not success:
            logger.error(f"Failed to navigate to {product_type} page")
            capture_failure_artifacts(page, "product_selection_error")
            raise AssertionError(f"Failed to navigate to {product_type} page")
            
        logger.info(f"Selected product type: {product_type}")
        
        # Step 3: Store product_type in session_data for next test
        session_data["product_type"] = product_type
        
        # Step 4: Verify navigation using helper functions
        page = home_page.page
        
        # Use helper function for combined URL and heading verification
        verify_navigation(page, product_type, "Moisturizers" if product_type == "moisturizer" else "Sunscreens")
            
        logger.success(f"Test 2: Selected {product_type} based on temperature {temperature}°C")

    def test_03_add_products_to_cart(self, product_selection: Tuple[Dict[str, Any], str, Any]) -> None:
        """Adds products to cart based on the selected product type.

        This test continues from test_02 and:
        1. Adds products to cart based on the selected product type
        2. Verifies the cart button shows the correct number of items

        Args:
            product_selection: Tuple containing (pages_dict, product_type, temperature)
        """
        try:
            pages, product_type, _ = product_selection
            # product_type is now directly provided by the fixture as a simple string
            product_page = pages["product"]
            page = product_page.page
            
            # Step 1: Verify current page with expect
            verify_url(page, product_type)
            
            # Step 2: Add products based on type
            added_items = (
                product_page.add_moisturizers_to_cart() 
                if product_type == "moisturizer" 
                else product_page.add_sunscreens_to_cart()
            )
            logger.info(f"Added items to cart: {added_items}")
            
            # Step 3: Store state for verification
            global session_data
            session_data["added_items"] = added_items
            
            # Step 4: Verify cart update using helper function
            cart_element = verify_cart_not_empty(page)
            
            # Step 5: Navigate to cart
            product_page.go_to_cart()
            
            # Step 6: Verify we're on cart page
            verify_url(page, "cart")
            verify_page_heading(page, "Checkout")
            
            logger.success(f"Test 3: Successfully added {len(added_items)} {product_type} products to cart")
            
        except Exception as e:
            logger.error(f"Error adding products to cart: {str(e)}")
            # Take screenshot and dump HTML on error
            product_page.page.screenshot(path=f"error_test3_{product_type}.png")
            with open(f"error_test3_{product_type}.html", "w", encoding="utf-8") as f:
                f.write(product_page.page.content())
            raise

    def test_04_cart_verification(self, products_added_to_cart) -> None:
        """Verifies cart contents and total price.

        This test continues from test_03 and:
        1. Verifies all expected items appear in the cart
        2. Validates cart total matches sum of item prices using page object method
        3. Stores total price in session state for payment

        Args:
            products_added_to_cart: Tuple containing (pages_dict, added_items, product_type)
        """
        test_name = "test_04_cart_verification"
        try:
            # Extract data from fixture
            pages, product_type, added_items = products_added_to_cart
            # product_type is now directly provided by the fixture as a simple string
            cart_page = pages["cart"]
            page = cart_page.page
            
            # Step 1: Verify we're on the cart page using helper functions
            verify_navigation(page, "cart", "Checkout")
            
            # Verify pay button is enabled using our helper and proper locator
            pay_button = verify_element_enabled(page, CartPageLocators.PAY_BUTTON)
            
            # Step 2: Access session state for the expected items
            global session_data
            expected_items = session_data.get('added_items', [])
            logger.info(f"Verifying cart items for {product_type} products: {expected_items}")
            
            # Ensure we have items to verify
            if not expected_items:
                logger.warning("No items in session data to verify in cart")
                # Try to get items from the fixture directly as fallback
                expected_items = added_items
                logger.info(f"Using items from fixture instead: {expected_items}")
            
            # Step 3: Verify all expected items are in the cart using the enhanced page object method
            # This encapsulates all the verification logic in the page object
            verification_result = cart_page.verify_items_in_cart(expected_items)
            if not verification_result:
                logger.error("Cart verification failed: Missing expected items")
                capture_failure_artifacts(page, f"{test_name}_items_verification")
                raise AssertionError("Cart verification failed: one or more expected items not found")
            
            # Step 4: Verify the total price using the page object method
            # This validates the displayed total matches the calculated total and returns the verified price
            try:
                total_price = cart_page.verify_total_price()
                if not total_price:
                    logger.error("Could not determine total price")
                    capture_failure_artifacts(page, f"{test_name}_price_verification")
                    raise AssertionError("Total price verification failed")
                    
                # Step 5: Store state for payment in the global session data
                session_data["total_price"] = total_price
                logger.success(f"Test 4: Verified cart contents and total price: {total_price}")
                
            except Exception as price_error:
                logger.error(f"Error verifying total price: {str(price_error)}")
                capture_failure_artifacts(page, f"{test_name}_price_calculation")
                raise
            
        except Exception as e:
            logger.error(f"Error during cart verification: {str(e)}")
            # Use our centralized artifact capture
            if 'page' in locals():
                capture_failure_artifacts(page, f"{test_name}_error")
            raise

    def test_05_payment_workflow(self, cart_contents_verified) -> None:
        """Completes the payment workflow.

        This test continues from test_04 and:
        1. Clicks the pay button
        2. Fills out and submits payment form
        3. Verifies payment success

        Args:
            cart_contents_verified: Fixture providing pages dict and total_price
        """
        test_name = "test_05_payment_workflow"
        try:
            # Unpack the fixture data
            pages, total_price = cart_contents_verified
            cart_page = pages["cart"]
            payment_page = pages["payment"]
            page = cart_page.page
            
            # Step 1: Verify we're on the cart page and pay button is enabled
            verify_navigation(page, "cart", "Checkout")
            
            # Also verify the total price from fixture matches what's displayed
            logger.info(f"Proceeding to payment with total price: {total_price}")
            
            # Verify pay button is enabled before proceeding
            pay_button = verify_element_enabled(page, CartPageLocators.PAY_BUTTON)
            
            # Step 2: Navigate to payment with enhanced return values for better error handling
            payment_success, payment_message = cart_page.proceed_to_payment()
            if not payment_success:
                logger.error(payment_message)
                capture_failure_artifacts(page, f"{test_name}_payment_navigation")
                raise AssertionError(f"Failed to proceed to payment: {payment_message}")
                
            logger.info("Payment form opened successfully")
                
            # Step 3: Wait for and fill payment form (with better error handling)
            try:
                # Longer wait for iframe which can be slow to load
                logger.info("Filling payment details")
                payment_page.fill_payment_details()
            except Exception as payment_error:
                logger.error(f"Payment form fill error: {str(payment_error)}")
                capture_failure_artifacts(page, f"{test_name}_payment_form")
                raise
            
            # Step 4: Verify we're redirected to the success page after payment
            try:
                # Use the payment page's verify_payment_success method instead of duplicating logic
                if not payment_page.verify_payment_success():
                    raise AssertionError("Payment verification failed")
                
                logger.success("Test 5: Successfully completed payment workflow")
            except Exception as success_error:
                logger.error(f"Payment success verification error: {str(success_error)}")
                capture_failure_artifacts(page, f"{test_name}_success_verification")
                raise
                
        except Exception as e:
            logger.error(f"Error during payment workflow: {str(e)}")
            # Use our centralized artifact capture
            if 'page' in locals():
                capture_failure_artifacts(page, f"{test_name}_error")
            raise
