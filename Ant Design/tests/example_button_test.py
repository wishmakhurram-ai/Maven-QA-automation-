"""
Example test file demonstrating Ant Design button automation
"""
from selenium import webdriver
from framework.components.button_handler import ButtonHandler
from framework.utils.driver_setup import DriverSetup
from run_example import DEFAULT_URL
import time

# URL variable - accessible to other files
# Can be imported: from tests.example_button_test import TEST_URL
TEST_URL = DEFAULT_URL  # Uses global URL from run_example.py


def setup_driver():
    """
    Setup and return Chrome WebDriver instance
    
    Returns:
        WebDriver instance
    """
    # Using the driver setup utility
    return DriverSetup.get_chrome_driver(headless=False, maximize=True)


def test_button_by_data_attr():
    """
    Example: Click button using data-atr-id attribute
    """
    driver = setup_driver()
    try:
        # Navigate to your Ant Design page
        driver.get(TEST_URL)
        
        # Initialize button handler
        button_handler = ButtonHandler(driver)
        
        # Click button by data-atr-id
        success = button_handler.click_button("submit-button", identifier_type='data_attr')
        
        if success:
            print("✓ Button clicked successfully using data-atr-id")
        else:
            print("✗ Failed to click button")
            
    finally:
        time.sleep(2)  # Wait to see the result
        driver.quit()


def test_button_by_text():
    """
    Example: Click button by its text content
    """
    driver = setup_driver()
    try:
        driver.get(TEST_URL)
        
        button_handler = ButtonHandler(driver)
        
        # Click button by text
        success = button_handler.click_button("Submit", identifier_type='text')
        
        if success:
            print("✓ Button clicked successfully using text")
        else:
            print("✗ Failed to click button")
            
    finally:
        time.sleep(2)
        driver.quit()


def test_button_by_type():
    """
    Example: Click button by type (primary, default, etc.)
    """
    driver = setup_driver()
    try:
        driver.get(TEST_URL)
        
        button_handler = ButtonHandler(driver)
        
        # Click first primary button on the page
        success = button_handler.click_button("primary", identifier_type='type')
        
        if success:
            print("✓ Primary button clicked successfully")
        else:
            print("✗ Failed to click button")
            
    finally:
        time.sleep(2)
        driver.quit()


def test_auto_detect_button():
    """
    Example: Auto-detect and click button (most generic method)
    Tries data-attr-id, text, and type in sequence
    """
    driver = setup_driver()
    try:
        driver.get(TEST_URL)
        
        button_handler = ButtonHandler(driver)
        
        # Auto-detect button - tries all methods
        success = button_handler.click_button_by_auto_detect("submit-button")
        
        if success:
            print("✓ Button auto-detected and clicked successfully")
        else:
            print("✗ Failed to auto-detect and click button")
            
    finally:
        time.sleep(2)
        driver.quit()


def test_get_button_info():
    """
    Example: Get button information without clicking
    """
    driver = setup_driver()
    try:
        driver.get(TEST_URL)
        
        button_handler = ButtonHandler(driver)
        
        # Get button information
        button_info = button_handler.get_button_info("submit-button", identifier_type='data_attr')
        
        if button_info:
            print(f"Button Information:")
            print(f"  Type: {button_info['type']}")
            print(f"  Size: {button_info['size']}")
            print(f"  Text: {button_info['text']}")
            print(f"  Disabled: {button_info['disabled']}")
            print(f"  Loading: {button_info['loading']}")
            print(f"  Shape: {button_info['shape']}")
        else:
            print("✗ Button not found")
            
    finally:
        time.sleep(2)
        driver.quit()


def test_find_all_buttons():
    """
    Example: Find all Ant Design buttons on the page
    """
    driver = setup_driver()
    try:
        driver.get(TEST_URL)
        
        button_handler = ButtonHandler(driver)
        
        # Find all buttons
        buttons = button_handler.find_all_ant_buttons()
        
        print(f"Found {len(buttons)} Ant Design buttons on the page")
        
        # Identify each button
        for idx, button in enumerate(buttons, 1):
            button_info = button_handler.identify_button_type(button)
            print(f"\nButton {idx}:")
            print(f"  Type: {button_info['type']}")
            print(f"  Text: '{button_info['text']}'")
            print(f"  Data-attr-id: {button_info['data_attr_id']}")
            
    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    print("Running Ant Design Button Automation Examples\n")
    
    # Uncomment the test you want to run:
    # test_button_by_data_attr()
    # test_button_by_text()
    # test_button_by_type()
    # test_auto_detect_button()
    # test_get_button_info()
    # test_find_all_buttons()
    
    print("\nPlease uncomment a test function to run it")

