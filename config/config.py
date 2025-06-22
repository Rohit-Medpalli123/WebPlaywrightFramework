"""
Configuration file for the Weather Shopper application
"""

class Config:
    BASE_URL = "https://weathershopper.pythonanywhere.com/"
    TIMEOUT = 30000  # milliseconds
    
    # Browser configurations
    BROWSER_OPTIONS = {
        "chrome": {
            "headless": False,
        },
        "firefox": {
            "headless": False,
        },
        "webkit": {
            "headless": False,
        }
    }
    
    # Product type configurations
    # Note: Actual selectors are imported in page classes to avoid circular imports
    PRODUCT_MAP = {
        "moisturizer": {
            "url_part": "moisturizer",
            "heading": "Moisturizers",
            "log_name": "moisturizers",
            "button_name": "BUY_MOISTURIZERS"
        },
        "sunscreen": {
            "url_part": "sunscreen", 
            "heading": "Sunscreens",
            "log_name": "sunscreens",
            "button_name": "BUY_SUNSCREENS"
        }
    }
    
    # Test card details (from Stripe testing docs)
    PAYMENT = {
        "email": "test@example.com",
        "card_number": "4242424242424242",
        "expiry_month": "12",
        "expiry_year": "25",
        "cvc": "123",
        "zip": "12345"
    }
