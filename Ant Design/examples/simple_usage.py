"""
Simple usage example for Ant Design button automation
"""
from selenium import webdriver
from framework.components.button_handler import ButtonHandler
from framework.utils.driver_setup import DriverSetup
from run_example import DEFAULT_URL


def main():
    """
    Simple example demonstrating button automation
    """
    # Setup driver
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    
    try:
        # Navigate to your page
        driver.get(DEFAULT_URL)
        
        # Initialize button handler
        button_handler = ButtonHandler(driver)
        
        # Example 1: Click button by data-atr-id (most reliable)
        print("Example 1: Clicking button by data-atr-id...")
        success = button_handler.click_button("example-button-id", identifier_type='data_attr')
        print(f"Result: {'Success' if success else 'Failed'}\n")
        
        # Example 2: Auto-detect and click (most generic)
        print("Example 2: Auto-detecting and clicking button...")
        success = button_handler.click_button_by_auto_detect("submit-button")
        print(f"Result: {'Success' if success else 'Failed'}\n")
        
        # Example 3: Get button information
        print("Example 3: Getting button information...")
        button_info = button_handler.get_button_info("example-button-id", identifier_type='data_attr')
        if button_info:
            print(f"Button Type: {button_info['type']}")
            print(f"Button Text: {button_info['text']}")
            print(f"Disabled: {button_info['disabled']}")
            print(f"Loading: {button_info['loading']}\n")
        
        # Example 4: Find all buttons
        print("Example 4: Finding all Ant Design buttons...")
        buttons = button_handler.find_all_ant_buttons()
        print(f"Found {len(buttons)} buttons on the page")
        for idx, button in enumerate(buttons[:5], 1):  # Show first 5
            info = button_handler.identify_button_type(button)
            print(f"  Button {idx}: {info['text']} ({info['type']})")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Keep browser open for 3 seconds to see results
        import time
        time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    main()

