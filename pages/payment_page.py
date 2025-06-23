"""
Payment page for completing the purchase
"""
from pages.base_page import BasePage
from locators.locators import PaymentPageLocators
from config.config import Config
from loguru import logger
import re
from playwright.sync_api import Page, expect
from utils.test_helpers import (
    verify_element_visible,
    verify_element_enabled,
    verify_url,
    verify_text_content,
    verify_navigation,
    capture_failure_artifacts,
    verify_frame_element_visible,
    verify_frame_element_enabled
)

class PaymentPage(BasePage):
    """Payment page class for Weather Shopper application"""
    
    def fill_payment_details(self) -> bool:
        """Fill in the payment details in the Stripe payment form using config values
        
        Uses helper functions for verification and includes robust error handling with
        failure artifacts. Returns success status to allow for better test flow control.
        
        Returns:
            bool: True if payment details were filled and submitted, False otherwise
        """
        test_name = "fill_payment_details"
        try:
            # Make sure the page is fully loaded before proceeding
            self.page.wait_for_load_state("networkidle")
            
            # Use helper to verify the payment frame is present
            logger.info("Locating payment frame...")
            verify_element_visible(self.page, PaymentPageLocators.PAYMENT_FRAME, timeout=10000)
            
            # Switch to payment iframe using Playwright's frame_locator
            payment_frame = self.page.frame_locator(PaymentPageLocators.PAYMENT_FRAME)
            logger.info("Successfully located payment frame")

            # Verify and fill email field
            # Use our frame-specific helper functions
            email_locator = verify_frame_element_visible(self.page, payment_frame, PaymentPageLocators.EMAIL_FIELD, timeout=5000)
            verify_frame_element_enabled(self.page, payment_frame, PaymentPageLocators.EMAIL_FIELD)
            logger.info("Filling email field")
            email_locator.fill(Config.PAYMENT["email"])
            
            # Verify and fill card number field
            # Use our frame-specific helper functions
            card_number_locator = verify_frame_element_visible(self.page, payment_frame, PaymentPageLocators.CARD_NUMBER_FIELD)
            verify_frame_element_enabled(self.page, payment_frame, PaymentPageLocators.CARD_NUMBER_FIELD)
            logger.info("Filling card number field")
            card_number_locator.fill(Config.PAYMENT["card_number"])
            
            # Verify and fill expiry field
            # Use our frame-specific helper functions
            expiry_locator = verify_frame_element_visible(self.page, payment_frame, PaymentPageLocators.EXPIRY_FIELD)
            verify_frame_element_enabled(self.page, payment_frame, PaymentPageLocators.EXPIRY_FIELD)
            logger.info("Filling expiry date field")
            expiry_locator.fill(f"{Config.PAYMENT['expiry_month']}{Config.PAYMENT['expiry_year']}")
                        
            # Verify and fill CVC field
            # Use our frame-specific helper functions
            cvc_locator = verify_frame_element_visible(self.page, payment_frame, PaymentPageLocators.CVC_FIELD)
            verify_frame_element_enabled(self.page, payment_frame, PaymentPageLocators.CVC_FIELD)
            logger.info("Filling CVC field")
            cvc_locator.fill(Config.PAYMENT["cvc"])
            
            # Wait for and click the pay button
            logger.info("Locating pay button...")
            # Use our frame-specific helper functions
            pay_button = verify_frame_element_visible(self.page, payment_frame, PaymentPageLocators.PAY_BUTTON)
            verify_frame_element_enabled(self.page, payment_frame, PaymentPageLocators.PAY_BUTTON)
            logger.info("Ready to submit payment")
            
            # Click pay button and expect navigation
            with self.page.expect_navigation(wait_until="networkidle"):
                pay_button.click()
                logger.success("Payment submitted successfully")
            
            return True
                
        except Exception as e:
            logger.error(f"Error during payment form filling: {str(e)}")
            capture_failure_artifacts(self.page, f"{test_name}_error")
            return False
    
    def verify_payment_success(self) -> bool:
        """Verify payment was successful.
        
        Uses helper functions to verify successful payment completion.
        Checks for correct URL and success message.
        
        Returns:
            bool: True if payment success message is displayed, False otherwise
        """
        test_name = "verify_payment_success"
        try:
            logger.info(f"Verifying payment success at URL: {self.page.url}")
            
            # Use helper function to verify we're on the confirmation page
            verify_url(self.page, "confirmation", case_sensitive=False)
            
            # Use helper function to verify success message
            success_element = verify_element_visible(
                self.page, 
                PaymentPageLocators.PAYMENT_SUCCESS_MESSAGE, 
                timeout=10000  # Longer timeout for payment processing
            )
            
            # Verify text content with helper
            # The actual text on the page is "PAYMENT SUCCESS"
            verify_text_content(
                self.page,
                PaymentPageLocators.PAYMENT_SUCCESS_MESSAGE,
                "PAYMENT SUCCESS"
            )
            
            logger.success("Payment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            capture_failure_artifacts(self.page, f"{test_name}_error")
            return False
