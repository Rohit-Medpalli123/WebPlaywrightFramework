"""
Product page for selecting and adding items to cart.

This module contains the ProductPage class which handles all product selection
and cart addition logic for the WeatherShopper application.
"""
from pages.base_page import BasePage
from locators.locators import ProductPageLocators
from loguru import logger
from typing import Dict, List, Tuple, Optional
import re
from playwright.sync_api import expect
from utils.test_helpers import (
    verify_element_visible,
    verify_element_count,
    verify_text_content,
    verify_url,
    capture_failure_artifacts
)

class ProductPage(BasePage):
    """Product page class for managing moisturizers and sunscreens selection.
    
    This class handles product discovery, filtering by criteria (ingredient/SPF),
    and adding products to cart. It uses a unified approach to find products
    based on different search criteria.
    """
    
    def get_all_products(self) -> List[Dict]:
        """Get all products from the current product page.
        
        Uses helper functions to wait for and verify product containers are visible
        before processing them. Extracts product information using Playwright locators.
        
        Returns:
            List[Dict]: List of product dictionaries with name, price, and add_button
        
        Raises:
            Exception: If products cannot be loaded or found
        """
        test_name = "get_all_products"
        try:
            # Verify current page and log information
            current_url = self.page.url
            logger.info(f"Loading products from: {current_url}")
            
            # Use helper function to verify product containers are visible
            # This replaces manual wait_for_selector with a more robust solution
            containers_locator = self.page.locator(ProductPageLocators.PRODUCT_CONTAINERS)
            elements = verify_element_count(self.page, ProductPageLocators.PRODUCT_CONTAINERS, min_count=1)
            element_count = len(elements)
            logger.info(f"Verified {element_count} product containers on page")
            
            # Wait for page to stabilize (keep this as it's still useful)
            self.page.wait_for_load_state('networkidle', timeout=5000)
            
            # Use locator API instead of query_selector_all (more modern Playwright pattern)
            product_elements = containers_locator.all()
            
            # Extract product information using modern locator patterns
            products = []
            for i, element in enumerate(product_elements):
                try:
                    # Use locator API instead of query_selector
                    name_locator = element.locator(ProductPageLocators.PRODUCT_NAME)
                    price_locator = element.locator(ProductPageLocators.PRODUCT_PRICE)
                    add_button_locator = element.locator(ProductPageLocators.ADD_BUTTON)
                    
                    # Verify all components are present
                    expect(name_locator).to_be_visible()
                    expect(price_locator).to_be_visible()
                    expect(add_button_locator).to_be_visible()
                    
                    # Extract text content
                    name = name_locator.text_content().strip()
                    price_text = price_locator.text_content().strip()
                    price = self.extract_price(price_text)
                    
                    products.append({
                        "name": name,
                        "price": price,
                        "add_button": add_button_locator  # Store locator instead of element
                    })
                    logger.debug(f"Product {i+1}: {name}, ${price}")
                    
                except Exception as item_error:
                    # Log issues with individual products but continue processing others
                    logger.warning(f"Skipping incomplete product {i+1}: {str(item_error)}")
            
            logger.info(f"Successfully extracted {len(products)} complete products")
            return products
            
        except Exception as e:
            logger.error(f"Error loading products: {str(e)}")
            # Use centralized helper for capturing failure artifacts
            capture_failure_artifacts(self.page, f"{test_name}_error")
            raise
    
    def add_to_cart(self, button_locator) -> bool:
        """Add a product to cart by clicking its 'Add' button.
        
        Uses the button locator (not element) to click and add to cart.
        Verifies the cart indicator updates to confirm successful addition.
        
        Args:
            button_locator: The Playwright locator for the add button
            
        Returns:
            bool: True if product was successfully added, False otherwise
        """
        test_name = "add_to_cart"
        try:
            # Get current cart count before adding item
            cart_button = self.page.locator(ProductPageLocators.CART_BUTTON)
            pre_count_text = cart_button.text_content() or ""
            pre_count = self._extract_cart_count(pre_count_text) or 0
            
            logger.info(f"Current cart count: {pre_count}. Adding new item...")
            # Click the button using the locator
            button_locator.click()
            
            # Wait for and verify cart update
            logger.debug("Verifying cart indicator update")
            expect(cart_button).to_contain_text(re.compile(r"\d+"), timeout=5000)
            
            # Verify the count increased
            post_count_text = cart_button.text_content() or ""
            post_count = self._extract_cart_count(post_count_text) or 0
            
            if post_count > pre_count:
                logger.success(f"Product successfully added to cart. Count: {pre_count} → {post_count}")
                return True
            else:
                logger.warning(f"Cart indicator did not increase as expected: {pre_count} → {post_count}")
                return False
            
        except Exception as e:
            logger.error(f"Error adding product to cart: {str(e)}")
            capture_failure_artifacts(self.page, f"{test_name}_error")
            return False
            
    def _extract_cart_count(self, text):
        """Extract numeric cart count from cart button text.
        
        Args:
            text: Text from the cart button
            
        Returns:
            int or None: The extracted count or None if no match
        """
        if not text:
            return None
            
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        return None
    
    def find_least_expensive_product(self, criteria: str, criteria_type: str = 'ingredient') -> Dict:
        """Find the least expensive product matching the given criteria.
        
        This unified method handles both ingredient and SPF-based searches.
        
        Args:
            criteria: The search criteria (ingredient name or SPF value)
            criteria_type: Type of search - 'ingredient' or 'spf' (default: 'ingredient')
            
        Returns:
            Dict: The product with the lowest price matching the criteria
            
        Raises:
            ValueError: If no matching products are found
        """
        products = self.get_all_products()
        logger.info(f"Looking for products with {criteria_type}={criteria}")
        logger.info(f"Found {len(products)} total products")
        
        matching_products = []
        
        # Simple matching strategy based on criteria type
        if criteria_type.lower() == 'ingredient':
            # For ingredients - case-insensitive substring match is sufficient
            matching_products = [product for product in products 
                                if criteria.lower() in product["name"].lower()]
            logger.info(f"Found {len(matching_products)} products with {criteria}")
            
        elif criteria_type.lower() == 'spf':
            # For SPF - case-insensitive match for the SPF string
            matching_products = [product for product in products 
                                if criteria.lower() in product["name"].lower()]
            logger.info(f"Found {len(matching_products)} products with {criteria}")
        
        # Check if we found any matching products
        if not matching_products:
            error_msg = f"No products found matching {criteria_type}={criteria}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Select the cheapest product
        selected_product = min(matching_products, key=lambda x: x["price"])
        logger.info(f"Selected: {selected_product['name']}, Price: {selected_product['price']}")
        return selected_product
    
    def add_moisturizers_to_cart(self) -> Tuple[str, str]:
        """Add the cheapest moisturizers with Aloe and Almond to the cart.
        
        Returns:
            Tuple[str, str]: Names of the two added products
        """
        logger.info("Adding moisturizers to cart: looking for Aloe and Almond products")
        
        # Add least expensive moisturizer with Aloe
        aloe_moisturizer = self.find_least_expensive_product("Aloe", "ingredient")
        self.add_to_cart(aloe_moisturizer["add_button"])
        logger.info(f"Added Aloe product: {aloe_moisturizer['name']}")
        
        # Add least expensive moisturizer with Almond
        almond_moisturizer = self.find_least_expensive_product("Almond", "ingredient")
        self.add_to_cart(almond_moisturizer["add_button"])
        logger.info(f"Added Almond product: {almond_moisturizer['name']}")
        
        return (aloe_moisturizer["name"], almond_moisturizer["name"])
    
    def add_sunscreens_to_cart(self) -> Tuple[str, str]:
        """Add the cheapest sunscreens with SPF-50 and SPF-30 to the cart.
        
        Returns:
            Tuple[str, str]: Names of the two added products
        """
        logger.info("Adding sunscreens to cart: looking for SPF-50 and SPF-30 products")
        
        # Add least expensive sunscreen with SPF-50
        spf50_sunscreen = self.find_least_expensive_product("SPF-50", "spf")
        self.add_to_cart(spf50_sunscreen["add_button"])
        logger.info(f"Added SPF-50 product: {spf50_sunscreen['name']}")
        
        # Add least expensive sunscreen with SPF-30
        spf30_sunscreen = self.find_least_expensive_product("SPF-30", "spf")
        self.add_to_cart(spf30_sunscreen["add_button"])
        logger.info(f"Added SPF-30 product: {spf30_sunscreen['name']}")
        
        return (spf50_sunscreen["name"], spf30_sunscreen["name"])
    
    def go_to_cart(self) -> None:
        """Navigate to the cart page by clicking the cart button.
        
        This method clicks on the cart button and waits for navigation to complete.
        Uses expect API for validation of successful navigation.
        
        Raises:
            Exception: If navigation to cart page fails
        """
        try:
            logger.info("Navigating to cart page")
            
            # Click cart button and wait for navigation
            with self.page.expect_navigation():
                self.page.click(ProductPageLocators.CART_BUTTON)
                
            # Use expect to verify we've navigated to cart page
            expect(self.page).to_have_url(re.compile(r".*cart.*", re.IGNORECASE))
            checkout_header = self.page.locator("h2")
            expect(checkout_header).to_contain_text("Checkout")
            
            logger.info(f"Successfully navigated to cart page: {self.page.url}")
        except Exception as e:
            logger.error(f"Error navigating to cart page: {str(e)}")
            self.page.screenshot(path="cart_navigation_error.png")
            raise
