"""
Cart page for verifying added items and proceeding to payment
"""
from pages.base_page import BasePage
from locators.locators import CartPageLocators, PaymentPageLocators
from typing import List, Dict, Union, Tuple
from loguru import logger
import re
from playwright.sync_api import expect
from utils.test_helpers import verify_element_visible, verify_element_enabled, verify_element_count, capture_failure_artifacts, extract_number_from_text, verify_frame_element_visible

class CartPage(BasePage):
    """Cart page class for Weather Shopper application"""
    
    def normalize_product_name(self, product_name: str) -> str:
        """Normalize a product name for consistent comparison.
        
        Args:
            product_name: The product name to normalize
            
        Returns:
            str: Normalized product name (lowercase, spaces standardized)
        """
        return product_name.lower().replace('-', ' ').replace('  ', ' ').strip()
    
    def get_cart_items(self) -> List[Dict[str, Union[str, int]]]:
        """Get all items in the cart
        
        Uses Playwright locators and expects to ensure the cart table is present
        before attempting to extract item information.
        
        Returns:
            List of items with name and price
            
        Raises:
            AssertionError: If the cart table is not visible
        """
        try:
            items = []
            
            # First verify the cart table exists using our helper and proper locator
            verify_element_visible(self.page, CartPageLocators.CART_TABLE)
            
            # Get all cart rows using locator
            cart_rows_locator = self.page.locator(CartPageLocators.CART_ITEMS)
            row_count = cart_rows_locator.count()
            
            if row_count == 0:
                logger.warning("No items found in cart")
                return items
                
            logger.info(f"Found {row_count} items in cart")
            
            # Loop through each row by index
            for i in range(row_count):
                try:
                    row = cart_rows_locator.nth(i)
                    name_cell = row.locator(CartPageLocators.CART_ITEM_NAME)
                    price_cell = row.locator(CartPageLocators.CART_ITEM_PRICE)
                    
                    # Use evaluate to safely extract text content
                    name = name_cell.text_content()
                    price_text = price_cell.text_content()
                    price = self.extract_price(price_text)
                    
                    items.append({
                        "name": name,
                        "price": price
                    })
                    logger.debug(f"Cart item {i+1}: {name} = {price}")
                except Exception as row_error:
                    logger.error(f"Error processing cart row {i}: {str(row_error)}")
                    # Continue with next item instead of failing entire method
                    
            return items
            
        except Exception as e:
            logger.error(f"Failed to get cart items: {str(e)}")
            capture_failure_artifacts(self.page, "get_cart_items_error")
            raise
    
    def verify_items_in_cart(self, expected_items: List[str]) -> bool:
        """Verify that specific items are in the cart
        
        Args:
            expected_items: List of item names expected to be in the cart
            
        Returns:
            True if all expected items are in the cart, False otherwise
            
        Raises:
            AssertionError: If cart verification fails and raise_on_failure is True
        """
        try:
            if not expected_items:
                logger.warning("No expected items provided for verification")
                return True
                
            cart_items = self.get_cart_items()
            
            if not cart_items:
                logger.error("Cart is empty but expected items were provided")
                capture_failure_artifacts(self.page, "empty_cart_error")
                return False
                
            cart_item_names = [item["name"] for item in cart_items]
            
            logger.info(f"Verifying cart items")
            logger.info(f"Expected items: {expected_items}")
            logger.info(f"Actual items in cart: {cart_item_names}")
            
            # Normalize cart item names for consistent comparison
            normalized_cart_items = [self.normalize_product_name(name) for name in cart_item_names]
            
            # Track verification results for detailed reporting
            verification_results = []
            
            for expected_item in expected_items:
                # Normalize expected item for comparison
                normalized_expected = self.normalize_product_name(expected_item)
                
                # Simple exact match check
                found_match = any(normalized_expected in item for item in normalized_cart_items)
                
                if not found_match:
                    logger.error(f"❌ Failed to find match for: {expected_item}")
                    verification_results.append((expected_item, False))
                else:
                    logger.info(f"✓ Found match for: {expected_item}")
                    verification_results.append((expected_item, True))
            
            # Check if all items were verified successfully
            all_verified = all(result[1] for result in verification_results)
            
            if all_verified:
                logger.success("Successfully verified all items in cart")
                return True
            else:
                failed_items = [result[0] for result in verification_results if not result[1]]
                logger.error(f"Failed to verify the following items: {failed_items}")
                capture_failure_artifacts(self.page, "cart_verification_error")
                return False
                
        except Exception as e:
            logger.error(f"Error during cart verification: {str(e)}")
            capture_failure_artifacts(self.page, "cart_verification_exception")
            return False
    
    def get_displayed_total(self) -> int:
        """Get the total price displayed on the cart page
        
        Returns:
            Total price as integer from the UI
        """
        logger.info("Extracting displayed total from cart page UI")
        
        # Get the total element using our locator
        total_element = self.page.locator(CartPageLocators.CART_TOTAL)
        verify_element_visible(self.page, total_element)
        
        # Extract the text content
        total_text = total_element.text_content()
        logger.debug(f"Raw total text from UI: {total_text}")
        
        # Use our helper function to extract the numeric part
        # Format is typically "Total: Rupees XXX"
        total = extract_number_from_text(total_text)
        logger.debug(f"Extracted total: {total}")
        return total
        
    def calculate_total_from_items(self, items: List[Dict]) -> int:
        """Calculate the total price from a list of cart items
        
        Args:
            items: List of cart items with price information
            
        Returns:
            Total price as integer
        """
        return sum(item["price"] for item in items)
        
    def verify_total_price(self) -> int:
        """Verify the displayed total price matches the calculated sum of item prices
        
        Returns:
            int: The verified total price
            
        Raises:
            AssertionError: If the displayed total doesn't match the calculated total
        """
        logger.info("Verifying cart total price")
        
        # Get cart items once to avoid duplicate DOM queries
        cart_items = self.get_cart_items()
        
        # Get displayed total and calculate expected total
        displayed_total = self.get_displayed_total()
        calculated_total = self.calculate_total_from_items(cart_items)
        
        # Verify totals match
        if displayed_total != calculated_total:
            logger.error(f"Total price mismatch: displayed {displayed_total} vs calculated {calculated_total}")
            raise AssertionError(f"Total price mismatch: displayed {displayed_total} vs calculated {calculated_total}")
            
        logger.success(f"Cart total verified: {displayed_total}")
        return displayed_total
    
    def proceed_to_payment(self) -> Tuple[bool, str]:
        """Click on the Pay with Card button and wait for the payment modal
        
        Uses Playwright expect to ensure the button is visible and clickable
        before proceeding to payment.
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            # First verify pay button is visible using helper
            pay_button = verify_element_enabled(self.page, CartPageLocators.PAY_BUTTON)
            
            logger.info("Clicking Pay with Card button")
            pay_button.click()
            
            # Wait for Stripe iframe to appear
            stripe_frame = self.page.frame_locator(PaymentPageLocators.PAYMENT_FRAME)
            logger.info("Waiting for payment form iframe to load")
            
            # Verify payment form iframe is loaded - use the locator from PaymentPageLocators
            verify_element_visible(self.page, PaymentPageLocators.PAYMENT_FRAME)
            
            # Extra validation that email field is visible within the frame
            # Use our frame-specific helper function
            verify_frame_element_visible(self.page, stripe_frame, PaymentPageLocators.EMAIL_FIELD, timeout=10000)  # Longer timeout for iframe loading
            logger.info("Successfully loaded payment form")
            
            return True, "Payment form loaded successfully"
            
        except Exception as e:
            error_message = f"Failed to proceed to payment: {str(e)}"
            logger.error(error_message)
            capture_failure_artifacts(self.page, "payment_navigation_error")
            return False, error_message
