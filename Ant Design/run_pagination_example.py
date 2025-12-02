"""
Simple Python script to run pagination automation examples
Run this directly without Gherkin: python run_pagination_example.py
"""
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.components.pagination_handler import PaginationHandler
from framework.utils.driver_setup import DriverSetup
from framework.context.element_context import ElementContext

# Ant Design Pagination page URL
PAGINATION_PAGE_URL = "https://ant.design/components/pagination"


def main():
    """
    Simple example demonstrating pagination automation
    """
    print("\n" + "="*70)
    print("Ant Design Pagination Automation - Quick Example")
    print("="*70)
    
    # Setup driver
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    
    try:
        # Navigate to pagination page
        print(f"\nNavigating to: {PAGINATION_PAGE_URL}")
        driver.get(PAGINATION_PAGE_URL)
        
        # Wait for page to load
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print(">>> Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(3)  # Additional wait for dynamic content
        
        # Scroll down to see pagination examples
        print(">>> Scrolling to see pagination examples...")
        for scroll_pos in [500, 1000, 1500, 2000, 2500]:
            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(0.5)
        time.sleep(2)
        
        # Initialize pagination handler
        context = ElementContext()
        pagination_handler = PaginationHandler(driver, context=context)
        
        # Find all paginations
        print("\n" + "="*70)
        print("FINDING ALL ANT DESIGN PAGINATIONS")
        print("="*70)
        paginations = pagination_handler.locator.find_all_paginations()
        print(f"\nTotal paginations found: {len(paginations)}")
        
        if not paginations:
            print("No paginations found on the page")
            return
        
        # Identify and show details for each pagination
        print("\n" + "="*70)
        print("IDENTIFYING ALL PAGINATIONS")
        print("="*70)
        pagination_details = []
        for idx, pagination in enumerate(paginations, 1):
            try:
                info = pagination_handler.identifier.identify_pagination(pagination)
                pagination_details.append({
                    'index': idx,
                    'element': pagination,
                    'info': info
                })
                print(f"\nPagination {idx}:")
                print(f"  Current page: {info.get('current_page', 'N/A')}")
                print(f"  Total pages: {info.get('total_pages', 'N/A')}")
                print(f"  Page size: {info.get('page_size', 'N/A')}")
                print(f"  Has jump-to: {info.get('has_jump_to', False)}")
                print(f"  Has page size changer: {info.get('has_page_size_changer', False)}")
                print(f"  Style: {info.get('style', 'default')}")
                print(f"  Simple mode: {info.get('simple_mode', False)}")
            except Exception as e:
                print(f"\nPagination {idx}: Error identifying - {str(e)}")
        
        # Interact with each pagination
        print("\n" + "="*70)
        print("INTERACTING WITH ALL PAGINATIONS")
        print("="*70)
        
        for pag_detail in pagination_details:
            idx = pag_detail['index']
            pagination = pag_detail['element']
            info = pag_detail['info']
            
            print(f"\n{'='*70}")
            print(f"PAGINATION {idx} - INTERACTIONS")
            print(f"{'='*70}")
            
            # Store this pagination in context for handler to use
            context.clear()
            element_info = pagination_handler.locator._create_element_info(pagination, str(idx), info)
            context.store_element(str(idx), element_info)
            context.set_current(str(idx))  # Set as current element
            
            # Scroll this pagination into view
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", pagination)
                time.sleep(0.5)
            except:
                pass
            
            # Print initial state
            print(f"\nInitial State:")
            current_page = info.get('current_page')
            total_pages = info.get('total_pages')
            page_size = info.get('page_size')
            print(f"  Current page: {current_page}")
            print(f"  Total pages: {total_pages}")
            print(f"  Page size: {page_size}")
            
            # Example 1: Navigate to specific pages (if not simple mode)
            if not info.get('simple_mode', False) and total_pages and total_pages > 1:
                # Test navigation to page 1
                print(f"\n>>> Navigating to page 1...")
                success = pagination_handler.go_to_page(1, use_context=True)
                print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                if success:
                    time.sleep(1.5)
                    # Verify we're on page 1
                    current = pagination_handler.get_current_page(use_context=True)
                    if current == 1:
                        print(f"  ✓ Verified: Currently on page {current}")
                    else:
                        print(f"  ⚠ Warning: Expected page 1, but on page {current}")
                
                # Test navigation to page 50 (if total pages >= 50)
                if total_pages >= 50:
                    print(f"\n>>> Navigating to page 50...")
                    success = pagination_handler.go_to_page(50, use_context=True)
                    print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                    if success:
                        time.sleep(1.5)
                        # Verify we're on page 50
                        current = pagination_handler.get_current_page(use_context=True)
                        if current == 50:
                            print(f"  ✓ Verified: Currently on page {current}")
                        else:
                            print(f"  ⚠ Warning: Expected page 50, but on page {current}")
                else:
                    # If less than 50 pages, go to last page
                    print(f"\n>>> Navigating to last page ({total_pages})...")
                    success = pagination_handler.go_to_page(total_pages, use_context=True)
                    print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                    if success:
                        time.sleep(1.5)
                        current = pagination_handler.get_current_page(use_context=True)
                        print(f"  Current page: {current}")
                
                # Test navigation to page 3
                print(f"\n>>> Navigating to page 3...")
                success = pagination_handler.go_to_page(3, use_context=True)
                print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                time.sleep(1.5)
            
            # Example 2: Navigate to next page (if enabled)
            if info.get('next_enabled', False):
                print(f"\n>>> Navigating to next page...")
                success = pagination_handler.next_page(use_context=True)
                print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                time.sleep(1.5)
            
            # Example 3: Navigate to previous page (if enabled)
            if info.get('prev_enabled', False):
                print(f"\n>>> Navigating to previous page...")
                success = pagination_handler.previous_page(use_context=True)
                print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                time.sleep(1.5)
            
            # Example 4: Change page size multiple times (if page size changer exists)
            if info.get('has_page_size_changer', False):
                available_sizes = info.get('available_page_sizes', [10, 20, 50, 100])
                current_size = info.get('page_size')
                
                # Test multiple page sizes: 20, 50, 100
                test_sizes = [20, 50, 100]
                for test_size in test_sizes:
                    if test_size in available_sizes and test_size != current_size:
                        print(f"\n>>> Changing page size to {test_size}...")
                        success = pagination_handler.select_page_size(test_size, use_context=True)
                        print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                        if success:
                            time.sleep(2)  # Wait for page to update
                            # Verify the change
                            updated_info = pagination_handler.identifier.identify_pagination(pagination)
                            new_size = updated_info.get('page_size')
                            if new_size == test_size:
                                print(f"  ✓ Verified: Page size is now {new_size}")
                            else:
                                print(f"  ⚠ Warning: Expected {test_size}, but page size is {new_size}")
                        time.sleep(1)
            
            # Example 5: Jump to page (if jump-to input exists)
            if info.get('has_jump_to', False) and total_pages and total_pages > 1:
                target_page = min(2, total_pages)
                print(f"\n>>> Jumping to page {target_page}...")
                success = pagination_handler.jump_to_page(target_page, use_context=True)
                print(f"Result: {'✓ Success' if success else '✗ Failed'}")
                time.sleep(1.5)
            
            # Final state for this pagination
            print(f"\nFinal State:")
            try:
                # Re-identify to get updated state
                updated_info = pagination_handler.identifier.identify_pagination(pagination)
                print(f"  Current page: {updated_info.get('current_page', 'N/A')}")
                print(f"  Page size: {updated_info.get('page_size', 'N/A')}")
            except:
                print(f"  Could not get updated state")
        
        # Summary of all paginations
        print("\n" + "="*70)
        print("SUMMARY OF ALL PAGINATIONS")
        print("="*70)
        for pag_detail in pagination_details:
            idx = pag_detail['index']
            pagination = pag_detail['element']
            print(f"\nPagination {idx}:")
            try:
                final_info = pagination_handler.identifier.identify_pagination(pagination)
                print(f"  Current page: {final_info.get('current_page', 'N/A')}")
                print(f"  Total pages: {final_info.get('total_pages', 'N/A')}")
                print(f"  Page size: {final_info.get('page_size', 'N/A')}")
                print(f"  Next enabled: {final_info.get('next_enabled', False)}")
                print(f"  Prev enabled: {final_info.get('prev_enabled', False)}")
            except Exception as e:
                print(f"  Error: {str(e)}")
        
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

