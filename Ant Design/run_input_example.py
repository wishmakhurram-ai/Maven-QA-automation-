"""
Quick runner script - Automatically detects and fills Ant Design input fields
Run this file directly: python run_input_example.py
"""
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.components.input_handler import InputHandler
from framework.utils.driver_setup import DriverSetup

# Global URL variable - Change this to your target URL
# This URL is used for input automation examples
DEFAULT_URL = "https://ant.design/components/input"


def main():
    """
    Simple example demonstrating input field automation
    """
    print("\n" + "="*70)
    print("Ant Design Input Field Automation - Quick Example")
    print("="*70)
    
    # Setup driver
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    
    try:
        # Navigate to your page
        print(f"\nNavigating to: {DEFAULT_URL}")
        driver.get(DEFAULT_URL)
        time.sleep(2)  # Wait for page to load
        
        # Initialize input handler
        input_handler = InputHandler(driver)
        
        # Print summary of all detected inputs (including non-Ant Design)
        print("\n" + "="*70)
        print("SUMMARY OF ALL DETECTED INPUTS (All Inputs)")
        print("="*70)
        input_handler.print_inputs_summary(include_all=True)
        
        # Fill all inputs with random values
        print("\n" + "="*70)
        print("AUTOMATICALLY FILLING ALL INPUTS WITH RANDOM VALUES")
        print("="*70)
        fill_results = input_handler.fill_all_inputs(use_random_values=True)
        
        print(f"\nFill Results:")
        print(f"  Total inputs: {fill_results['total']}")
        print(f"  Filled: {fill_results['filled']}")
        print(f"  Skipped: {fill_results['skipped']}")
        print(f"  Failed: {fill_results['failed']}")
        
        # Example 1: Fill input by label (semantic matching)
        print("\n" + "="*70)
        print("Example 1: Fill Input by Label (Semantic Matching)")
        print("="*70)
        print("Trying to fill input with label 'Basic usage' or similar...")
        success = input_handler.fill_input(
            "Basic usage",  # Label text to search for
            "Sample text value",
            identifier_type='label'
        )
        print(f"Result: {'✓ Success' if success else '✗ Failed'}\n")
        
        # Example 2: Fill first text input
        print("="*70)
        print("Example 2: Fill First Text Input")
        print("="*70)
        success = input_handler.fill_input(
            "text",
            "First text input value",
            identifier_type='type'
        )
        print(f"Result: {'✓ Success' if success else '✗ Failed'}\n")
        
        # Example 3: Fill input by position
        print("="*70)
        print("Example 3: Fill Input by Position (First Input)")
        print("="*70)
        success = input_handler.fill_input(
            "1",  # Position 1
            "Position 1 value",
            identifier_type='position'
        )
        print(f"Result: {'✓ Success' if success else '✗ Failed'}\n")
        
        # Example 4: Get input information
        print("="*70)
        print("Example 4: Get Input Information")
        print("="*70)
        input_info = input_handler.get_input_info("text", identifier_type='type')
        if input_info:
            print("Input Information:")
            print(f"  Type: {input_info['input_type']}")
            print(f"  Size: {input_info['size']}")
            print(f"  Disabled: {input_info['disabled']}")
            print(f"  Readonly: {input_info['readonly']}")
            print(f"  Clearable: {input_info['clearable']}")
            print(f"  Placeholder: '{input_info['placeholder']}'")
            print(f"  Label: '{input_info['label']}'")
        else:
            print("✗ Input not found")
        
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

