# Weather Shopper Automation

An automation framework for the Weather Shopper application built using Playwright and following the Page Object Model (POM) pattern.

## Overview

This automation framework automates the following workflow:
1. Visit https://weathershopper.pythonanywhere.com/
2. Get the current temperature
3. Choose to buy moisturizers or sunscreens based on temperature
   - Moisturizers if temperature < 19°C
   - Sunscreens if temperature > 34°C
4. Add two products to cart based on criteria
   - For moisturizers: least expensive with Aloe and least expensive with Almond
   - For sunscreens: least expensive SPF-50 and least expensive SPF-30
5. Verify the cart contains the correct items
6. Complete the payment process using Stripe test cards
7. Verify successful payment

## Project Structure

```
WeatherShopper/
├── config/             # Configuration settings
├── locators/           # Element locators
├── pages/              # Page objects
├── tests/              # Test scripts
├── utils/              # Utility functions
├── requirements.txt    # Dependencies
└── run_tests.py        # Test runner script
```

## Setup

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```
   playwright install
   ```

## Running Tests

To run tests with the default browser (Chromium):
```
python run_tests.py
```

To run tests with a specific browser:
```
python run_tests.py firefox
```
or
```
python run_tests.py webkit
```

You can also run tests directly with pytest:
```
pytest tests/test_weather_shopper.py --browser=chromium -v
```

## Features

- Page Object Model design pattern
- Page Factory pattern for creating page objects
- Cross-browser testing (Chromium, Firefox, WebKit)
- Configurable test settings
- Automatic handling of product selection based on temperature
- Verification of cart items and successful payment
