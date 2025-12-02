"""
Simple Python script to run button automation examples
Run this directly without Gherkin: python run_button_example.py
"""
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.components.button_handler import ButtonHandler
from framework.utils.driver_setup import DriverSetup

# Ant Design Button page URL
BUTTON_PAGE_URL = "https://ant.design/components/button"


def main():
    """
    Simple example demonstrating button automation
    """
    print("\n" + "="*70)
    print("Ant Design Button Automation - Quick Example")
    print("="*70)
    
    # Setup driver
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    
    try:
        # Navigate to button page
        print(f"\nNavigating to: {BUTTON_PAGE_URL}")
        driver.get(BUTTON_PAGE_URL)
        
        # Wait for page to load and scroll to load dynamic content
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        print(">>> Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(2)
        
        # Scroll down to load all dynamic content
        print(">>> Scrolling to load all buttons...")
        for scroll_position in [500, 1000, 1500, 2000, 2500, 3000]:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.5)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Initialize button handler
        button_handler = ButtonHandler(driver)
        
        # Find all buttons
        print("\n" + "="*70)
        print("FINDING ALL ANT DESIGN BUTTONS")
        print("="*70)
        buttons = button_handler.find_all_ant_buttons()
        print(f"\nTotal buttons found: {len(buttons)}")
        
        if buttons:
            print("\nButton Details (showing first 30):")
            print("-" * 70)
            for idx, button in enumerate(buttons[:30], 1):  # Show first 30
                try:
                    info = button_handler.identify_button_type(button)
                    status = "DISABLED" if info.get('disabled') else "ENABLED"
                    print(f"{idx}. {info.get('text', 'N/A')[:30]:30} | Type: {info.get('type', 'N/A'):10} | {status}")
                except Exception as e:
                    print(f"{idx}. Error getting button info: {str(e)}")
        
        # Automatically click all clickable buttons
        print("\n" + "="*70)
        print(f"AUTOMATICALLY CLICKING ALL CLICKABLE BUTTONS ({len(buttons)} total)")
        print("="*70)
        
        clicked_count = 0
        skipped_count = 0
        failed_count = 0
        
        # Process ALL buttons (not just first 10)
        for idx, button in enumerate(buttons, 1):
            try:
                # Re-find button if stale (buttons can become stale after scrolling)
                try:
                    info = button_handler.identify_button_type(button)
                except:
                    # Button might be stale, try to re-find by index
                    print(f"\n{idx}. Button became stale, re-finding...")
                    all_buttons = button_handler.find_all_ant_buttons()
                    if idx <= len(all_buttons):
                        button = all_buttons[idx - 1]
                        info = button_handler.identify_button_type(button)
                    else:
                        print(f"   ✗ Could not re-find button at index {idx}")
                        failed_count += 1
                        continue
                
                if info.get('disabled') or info.get('loading'):
                    print(f"\n{idx}/{len(buttons)}. Skipping: '{info.get('text', 'N/A')[:30]}' (Disabled or Loading)")
                    skipped_count += 1
                    continue
                
                button_text = info.get('text', 'N/A')[:30]
                print(f"\n{idx}/{len(buttons)}. Clicking: '{button_text}'")
                
                # Scroll button into view
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)
                    time.sleep(0.3)
                except:
                    # If button is stale, try to re-find
                    all_buttons = button_handler.find_all_ant_buttons()
                    if idx <= len(all_buttons):
                        button = all_buttons[idx - 1]
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)
                        time.sleep(0.3)
                
                # Try to click using button handler's robust click method
                try:
                    # Use the button handler's click method which handles stale elements better
                    button_info = button_handler.identify_button_type(button)
                    button_text_for_click = button_info.get('text', '').strip()
                    
                    if button_text_for_click:
                        # Try clicking by text (most reliable)
                        success = button_handler.click_button(button_text_for_click, identifier_type='text', timeout=5)
                        if success:
                            clicked_count += 1
                            print(f"   ✓ Successfully clicked")
                            time.sleep(0.5)  # Wait a bit between clicks
                        else:
                            # Fallback to direct click
                            try:
                                button.click()
                                clicked_count += 1
                                print(f"   ✓ Successfully clicked (direct)")
                                time.sleep(0.5)
                            except:
                                driver.execute_script("arguments[0].click();", button)
                                clicked_count += 1
                                print(f"   ✓ Successfully clicked (via JavaScript)")
                                time.sleep(0.5)
                    else:
                        # No text, try direct click
                        button.click()
                        clicked_count += 1
                        print(f"   ✓ Successfully clicked")
                        time.sleep(0.5)
                        
                except Exception as e:
                    # Try JavaScript click as fallback
                    try:
                        driver.execute_script("arguments[0].click();", button)
                        clicked_count += 1
                        print(f"   ✓ Successfully clicked (via JavaScript fallback)")
                        time.sleep(0.5)
                    except Exception as e2:
                        print(f"   ✗ Failed to click: {str(e2)[:50]}")
                        failed_count += 1
                        
            except Exception as e:
                print(f"\n{idx}/{len(buttons)}. Error processing button: {str(e)[:50]}")
                failed_count += 1
        
        print("\n" + "-" * 70)
        print("Summary:")
        print(f"  Total buttons found: {len(buttons)}")
        print(f"  Clicked: {clicked_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Failed: {failed_count}")
        
        # Example 1: Click button by type
        print("\n" + "="*70)
        print("Example 1: Click Button by Type (Primary)")
        print("="*70)
        success = button_handler.click_button("primary", identifier_type='type')
        print(f"Result: {'✓ Success' if success else '✗ Failed'}\n")
        time.sleep(1)
        
        # Example 2: Click button by text
        print("="*70)
        print("Example 2: Click Button by Text")
        print("="*70)
        # Try to find a common button text
        if buttons:
            try:
                first_button_info = button_handler.identify_button_type(buttons[0])
                button_text = first_button_info.get('text', '').strip()
                if button_text:
                    print(f"Trying to click button with text: '{button_text[:30]}'")
                    success = button_handler.click_button(button_text, identifier_type='text')
                    print(f"Result: {'✓ Success' if success else '✗ Failed'}\n")
                else:
                    print("No button text found for example")
            except:
                print("Could not get button text for example")
        time.sleep(1)
        
        # Example 3: Get button information
        print("="*70)
        print("Example 3: Get Button Information")
        print("="*70)
        if buttons:
            try:
                first_button_info = button_handler.identify_button_type(buttons[0])
                print("First Button Information:")
                print(f"  Type: {first_button_info.get('type', 'N/A')}")
                print(f"  Text: '{first_button_info.get('text', 'N/A')}'")
                print(f"  Size: {first_button_info.get('size', 'N/A')}")
                print(f"  Disabled: {first_button_info.get('disabled', False)}")
                print(f"  Loading: {first_button_info.get('loading', False)}")
                print(f"  Shape: {first_button_info.get('shape', 'N/A')}")
            except Exception as e:
                print(f"Error getting button info: {str(e)}")
        
        print("\n" + "="*70)
        print("Examples completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Keep browser open for 5 seconds to see results
        print("\nKeeping browser open for 5 seconds...")
        time.sleep(5)
        driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    main()

