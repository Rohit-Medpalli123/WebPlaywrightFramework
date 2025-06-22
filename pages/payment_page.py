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
    capture_failure_artifacts
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
            
            # Fill email field
            logger.info("Filling email field...")
            email_locator = payment_frame.locator(PaymentPageLocators.EMAIL_FIELD)
            expect(email_locator).to_be_visible(timeout=5000)
            expect(email_locator).to_be_enabled()
            email_locator.fill(Config.PAYMENT["email"])
            
            # Fill card number (this usually reveals other fields)
            logger.info("Filling card number...")
            card_number_locator = payment_frame.locator(PaymentPageLocators.CARD_NUMBER_FIELD)
            expect(card_number_locator).to_be_visible()
            expect(card_number_locator).to_be_enabled()
            card_number_locator.fill(Config.PAYMENT["card_number"])
            
            # Wait slightly to ensure form updates (some stripe forms need this)
            self.page.wait_for_timeout(1000)
            
            # Fill expiry date
            logger.info("Filling expiry date...")
            expiry_locator = payment_frame.locator(PaymentPageLocators.EXPIRY_FIELD)
            expect(expiry_locator).to_be_visible()
            expect(expiry_locator).to_be_enabled()
            expiry_locator.fill(f"{Config.PAYMENT['expiry_month']}{Config.PAYMENT['expiry_year']}")
            
            # Fill CVC
            logger.info("Filling CVC...")
            cvc_locator = payment_frame.locator(PaymentPageLocators.CVC_FIELD)
            expect(cvc_locator).to_be_visible()
            expect(cvc_locator).to_be_enabled()
            cvc_locator.fill(Config.PAYMENT["cvc"])
            
            # Try to fill ZIP code if it exists
            try:
                # Check if ZIP field exists and is visible
                zip_locator = payment_frame.locator(PaymentPageLocators.ZIP_FIELD)
                if zip_locator.count() > 0:
                    logger.info("ZIP field found, filling it...")
                    expect(zip_locator).to_be_visible(timeout=2000)
                    zip_locator.fill(Config.PAYMENT.get("zip", "12345"))
                    logger.info("ZIP code entered")
            except Exception as e:
                # This is not critical, just log and continue
                logger.debug(f"ZIP field not found or not required: {str(e)}")
            
            # Wait for and click the pay button
            logger.info("Locating pay button...")
            pay_button = payment_frame.locator(PaymentPageLocators.PAY_BUTTON)
            expect(pay_button).to_be_visible()
            expect(pay_button).to_be_enabled()
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
            verify_text_content(
                self.page,
                PaymentPageLocators.PAYMENT_SUCCESS_MESSAGE,
                "Your payment was successful"
            )
            
            logger.success("Payment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            capture_failure_artifacts(self.page, f"{test_name}_error")
            return False
