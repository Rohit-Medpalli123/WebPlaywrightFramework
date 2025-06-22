"""
Locators for Weather Shopper application
"""

class HomePageLocators:
    TEMPERATURE = "#temperature"
    BUY_MOISTURIZERS = "button:has-text('Buy moisturizers')"
    BUY_SUNSCREENS = "button:has-text('Buy sunscreens')"


class ProductPageLocators:
    # Common product locators
    CART_BUTTON = "button.thin-text.nav-link"
    # More specific selector with row to ensure we get all products
    PRODUCT_CONTAINERS = ".container .row .text-center.col-4"
    PRODUCT_NAME = "p.font-weight-bold"
    PRODUCT_PRICE = "p:has-text('Price:')"
    ADD_BUTTON = "button.btn.btn-primary"


class CartPageLocators:
    CART_ITEMS = "table.table-striped tbody tr"
    CART_ITEM_NAME = "td:nth-child(1)"
    CART_ITEM_PRICE = "td:nth-child(2)"
    PAY_BUTTON = "button.stripe-button-el"


class PaymentPageLocators:
    # iFrame
    PAYMENT_FRAME = "iframe[name='stripe_checkout_app']"
    
    # Payment form fields
    EMAIL_FIELD = "input[type='email']"
    CARD_NUMBER_FIELD = "input[placeholder='Card number']"
    EXPIRY_FIELD = "input[placeholder='MM / YY']"
    CVC_FIELD = "input[placeholder='CVC']"
    ZIP_FIELD = "input[placeholder='ZIP Code']"
    PAY_BUTTON = "button[type='submit']"
    
    # Confirmation
    PAYMENT_SUCCESS_MESSAGE = "h2:has-text('PAYMENT SUCCESS')"
