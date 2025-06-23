"""
Helper functions and utilities for Playwright tests

This module provides reusable verification helper functions for common test patterns
to reduce duplication and standardize verification approaches across tests.
"""
import re
import os
from typing import Dict, List, Optional, Pattern, Tuple, Union
from playwright.sync_api import Page, expect, Locator, FrameLocator
from loguru import logger

def verify_url(page: Page, expected_pattern: str, case_sensitive: bool = False) -> None:
    """Verify the current page URL matches the expected pattern
    
    Args:
        page: Playwright page object
        expected_pattern: String pattern to match in URL (will be wrapped in .* if not already)
        case_sensitive: Whether the match should be case sensitive
        
    Raises:
        AssertionError: If the URL doesn't match the expected pattern
    """
    # Prepare pattern - ensure it has wildcards if it's just a simple string
    if not expected_pattern.startswith('.*') and not expected_pattern.endswith('.*'):
        pattern = f".*{expected_pattern}.*"
    else:
        pattern = expected_pattern
        
    # Create regex pattern with case sensitivity option
    flags = 0 if case_sensitive else re.IGNORECASE
    regex_pattern = re.compile(pattern, flags)
    
    # Log the verification attempt
    logger.info(f"Verifying URL contains: {expected_pattern}")
    
    # Use expect to verify URL
    expect(page).to_have_url(regex_pattern)
    logger.debug(f"URL verification passed: {page.url} contains {expected_pattern}")

def verify_page_heading(page: Page, expected_heading: str, selector: str = "h2") -> None:
    """Verify the page heading matches the expected text
    
    Args:
        page: Playwright page object
        expected_heading: Expected heading text
        selector: CSS selector for the heading element (default: h2)
        
    Raises:
        AssertionError: If the heading doesn't match the expected text
    """
    logger.info(f"Verifying page heading: {expected_heading}")
    heading_locator = page.locator(selector)
    expect(heading_locator).to_be_visible()
    expect(heading_locator).to_contain_text(expected_heading)
    logger.debug(f"Heading verification passed: '{expected_heading}'")

def verify_navigation(page: Page, url_pattern: str, heading: Optional[str] = None, heading_selector: str = "h2") -> None:
    """Combined verification of URL and page heading
    
    Args:
        page: Playwright page object
        url_pattern: String pattern to match in URL
        heading: Optional heading text to verify
        heading_selector: CSS selector for the heading element (default: h2)
        
    Raises:
        AssertionError: If the URL or heading verification fails
    """
    verify_url(page, url_pattern)
    
    if heading:
        verify_page_heading(page, heading, heading_selector)


def verify_element_visible(page: Page, selector_or_locator: Union[str, Locator], timeout: Optional[int] = None) -> Locator:
    """Verify an element is visible on the page
    
    Args:
        page: Playwright page object
        selector_or_locator: Either a CSS selector string or a Playwright Locator object
        timeout: Optional custom timeout in milliseconds
        
    Returns:
        Locator: The verified element locator
        
    Raises:
        AssertionError: If the element is not visible
    """
    # Handle both string selectors and locator objects
    if isinstance(selector_or_locator, str):
        desc = selector_or_locator
        element = page.locator(selector_or_locator)
    else:
        # It's already a locator
        desc = str(selector_or_locator)
        element = selector_or_locator
        
    logger.info(f"Verifying element is visible: {desc}")
    
    # Set timeout if provided
    expect_options = {}
    if timeout:
        expect_options['timeout'] = timeout
    
    expect(element).to_be_visible(**expect_options)
    logger.debug(f"Element visible: {desc}")
    return element


def verify_element_enabled(page: Page, selector: str) -> Locator:
    """Verify an element is visible and enabled on the page
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        
    Returns:
        Locator: The verified element locator
        
    Raises:
        AssertionError: If the element is not visible or not enabled
    """
    logger.info(f"Verifying element is enabled: {selector}")
    element = page.locator(selector)
    expect(element).to_be_visible()
    expect(element).to_be_enabled()
    logger.debug(f"Element enabled: {selector}")
    return element


def verify_text_content(page: Page, selector_or_locator: Union[str, Locator], expected_text: Union[str, Pattern], exact: bool = False, timeout: Optional[int] = None) -> Locator:
    """Verify an element contains the expected text
    
    Args:
        page: Playwright page object
        selector_or_locator: Either a CSS selector string or a Playwright Locator object
        expected_text: Text or pattern expected to be in the element
        exact: Whether to match the exact text or just check if it contains the text
        timeout: Optional custom timeout in milliseconds
        
    Returns:
        Locator: The verified element locator
        
    Raises:
        AssertionError: If the element does not contain the expected text
    """
    # Handle both string selectors and locator objects
    if isinstance(selector_or_locator, str):
        desc = selector_or_locator
        element = page.locator(selector_or_locator)
    else:
        # It's already a locator
        desc = str(selector_or_locator)
        element = selector_or_locator
        
    # Describe the expected text/pattern for logging
    pattern_desc = expected_text.pattern if hasattr(expected_text, 'pattern') else expected_text
    logger.info(f"Verifying text content: {pattern_desc} in {desc}")
    
    # Ensure element is visible first
    verify_element_visible(page, element, timeout)
    
    # Set timeout if provided
    expect_options = {}
    if timeout:
        expect_options['timeout'] = timeout
    
    if exact:
        expect(element).to_have_text(expected_text, **expect_options)
    else:
        expect(element).to_contain_text(expected_text, **expect_options)
        
    logger.debug(f"Text verification passed: {pattern_desc}")
    return element


def verify_element_count(page: Page, selector: str, expected_count: int = None, min_count: int = None) -> List[Locator]:
    """Verify the number of elements matching a selector
    
    Args:
        page: Playwright page object
        selector: CSS selector for the elements
        expected_count: Expected exact number of elements (mutually exclusive with min_count)
        min_count: Minimum number of elements expected (mutually exclusive with expected_count)
        
    Returns:
        List[Locator]: List of found elements
        
    Raises:
        AssertionError: If the count doesn't match the expectation
        ValueError: If neither expected_count nor min_count is provided
    """
    if expected_count is None and min_count is None:
        raise ValueError("Either expected_count or min_count must be provided")
    
    if expected_count is not None and min_count is not None:
        logger.warning("Both expected_count and min_count provided; using expected_count")
        min_count = None
    
    elements = page.locator(selector)
    count = elements.count()
    
    if expected_count is not None:
        logger.info(f"Verifying element count: exactly {expected_count} for {selector}")
        expect(elements).to_have_count(expected_count)
        logger.debug(f"Count verification passed: found exactly {count} elements")
        return [elements.nth(i) for i in range(count)]
    else:  # min_count is not None
        logger.info(f"Verifying element count: at least {min_count} for {selector}")
        # Manual assertion for minimum count
        if count < min_count:
            raise AssertionError(f"Expected at least {min_count} elements for selector '{selector}', found {count}")
        logger.debug(f"Count verification passed: found {count} elements (minimum required: {min_count})")
        return [elements.nth(i) for i in range(count)]


def verify_page_title(page: Page, expected_title: str, exact: bool = False) -> None:
    """Verify page title matches expected pattern or text
    
    Args:
        page: Playwright page object
        expected_title: Expected title text or pattern
        exact: Whether to match exactly or use regex pattern
        
    Raises:
        AssertionError: If the title doesn't match the expected pattern
    """
    logger.info(f"Verifying page title contains: {expected_title}")
    
    if exact:
        expect(page).to_have_title(expected_title)
    else:
        expect(page).to_have_title(re.compile(expected_title))
        
    logger.debug(f"Page title verification passed: {page.title()}")


def verify_element_with_regex(page: Page, selector_or_locator: Union[str, Locator], pattern: str, timeout: Optional[int] = None) -> Locator:
    """Verify element exists and contains text matching pattern
    
    Args:
        page: Playwright page object
        selector_or_locator: Either a CSS selector string or a Playwright Locator object
        pattern: Regex pattern to match against element text
        timeout: Optional custom timeout in milliseconds
    
    Returns:
        Locator: The element locator object
        
    Raises:
        AssertionError: If element is not visible or text doesn't match pattern
    """
    # We can now reuse our refactored verify_text_content function
    # It will handle both string selectors and locator objects
    return verify_text_content(page, selector_or_locator, re.compile(pattern), exact=False, timeout=timeout)


def verify_cart_not_empty(page: Page, cart_selector: str = "#cart") -> Locator:
    """Verify cart is visible and not empty
    
    Args:
        page: Playwright page object
        cart_selector: CSS selector for cart element
    
    Returns:
        Locator: The cart element locator
        
    Raises:
        AssertionError: If cart is not visible or appears empty
    """
    logger.info(f"Verifying cart is not empty")
    cart = page.locator(cart_selector)
    expect(cart).to_be_visible()
    expect(cart).not_to_contain_text("Empty")
    logger.debug("Cart is verified to be not empty")
    return cart


def verify_frame_element_visible(page: Page, frame_locator: FrameLocator, selector: str, timeout: Optional[int] = None) -> Locator:
    """Verify an element within a frame is visible
    
    Args:
        page: Playwright page object
        frame_locator: Playwright FrameLocator object
        selector: CSS selector for the element within the frame
        timeout: Optional custom timeout in milliseconds
        
    Returns:
        Locator: The verified element locator
        
    Raises:
        AssertionError: If the element is not visible
    """
    logger.info(f"Verifying frame element is visible: {selector}")
    element = frame_locator.locator(selector)
    
    # Set timeout if provided
    expect_options = {}
    if timeout:
        expect_options['timeout'] = timeout
    
    expect(element).to_be_visible(**expect_options)
    logger.debug(f"Frame element visible: {selector}")
    return element


def verify_frame_element_enabled(page: Page, frame_locator: FrameLocator, selector: str, timeout: Optional[int] = None) -> Locator:
    """Verify an element within a frame is enabled
    
    Args:
        page: Playwright page object
        frame_locator: Playwright FrameLocator object
        selector: CSS selector for the element within the frame
        timeout: Optional custom timeout in milliseconds
        
    Returns:
        Locator: The verified element locator
        
    Raises:
        AssertionError: If the element is not enabled
    """
    logger.info(f"Verifying frame element is enabled: {selector}")
    element = frame_locator.locator(selector)
    
    # Set timeout if provided
    expect_options = {}
    if timeout:
        expect_options['timeout'] = timeout
    
    expect(element).to_be_enabled(**expect_options)
    logger.debug(f"Frame element enabled: {selector}")
    return element


def extract_number_from_text(text: str) -> int:
    """Extract the first numeric value from a text string
    
    Args:
        text: Text string that may contain numbers
        
    Returns:
        int: The extracted number
        
    Raises:
        ValueError: If no numeric value could be extracted
    """
    logger.debug(f"Extracting number from text: {text}")
    match = re.search(r'\d+', text)
    if not match:
        logger.error(f"Failed to extract numeric value from text: {text}")
        raise ValueError(f"Could not extract numeric value from: {text}")
        
    number = int(match.group())
    logger.debug(f"Extracted number: {number}")
    return number


def capture_failure_artifacts(page: Page, test_name: str, error_dir: str = "./errors") -> Dict[str, str]:
    """Capture screenshot and HTML dump on test failure
    
    Args:
        page: Playwright page object
        test_name: Name of the test for artifacts naming
        error_dir: Directory to save artifacts (default: ./errors)
        
    Returns:
        Dict containing paths to the captured artifacts
    """
    # Create error directory if it doesn't exist
    os.makedirs(error_dir, exist_ok=True)
    
    artifacts = {}
    
    try:
        # Take screenshot
        screenshot_path = f"{error_dir}/{test_name}_error.png"
        page.screenshot(path=screenshot_path)
        artifacts['screenshot'] = screenshot_path
        logger.debug(f"Captured error screenshot: {screenshot_path}")
        
        # Save HTML content
        html_path = f"{error_dir}/{test_name}_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        artifacts['html'] = html_path
        logger.debug(f"Captured error HTML: {html_path}")
    except Exception as e:
        logger.error(f"Failed to capture artifacts: {str(e)}")
    
    return artifacts
