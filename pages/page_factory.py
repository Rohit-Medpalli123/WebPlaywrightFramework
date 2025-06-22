"""
Page Factory class for creating page objects
"""
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.payment_page import PaymentPage

class PageFactory:
    """Factory class to create page objects"""
    
    @staticmethod
    def get_page_object(page_name: str, page: Page):
        """Get the page object based on the page name
        
        Args:
            page_name: Name of the page
            page: Playwright page object
            
        Returns:
            The page object
        """
        if page_name.lower() == "home":
            return HomePage(page)
        elif page_name.lower() == "product":
            return ProductPage(page)
        elif page_name.lower() == "cart":
            return CartPage(page)
        elif page_name.lower() == "payment":
            return PaymentPage(page)
        else:
            raise ValueError(f"Invalid page name: {page_name}")
