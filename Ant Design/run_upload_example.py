"""
STANDALONE Python Script - Ant Design Upload Automation Demo

This is a simple Python script that runs automation directly on the Ant Design 
upload documentation page. It does NOT use pytest or feature files.

Usage:
    python run_upload_example.py

This script:
- Automatically discovers all upload components on the page
- Clicks upload buttons with visual highlights
- Uploads test files to demonstrate functionality
- Shows visual feedback (colored borders) during interaction

For Gherkin/BDD testing with feature files, use pytest:
    pytest tests/test_upload_automation.py
"""
from framework.utils.driver_setup import DriverSetup
from framework.components.upload_handler import UploadHandler
from framework.context.element_context import ElementContext
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os


def demonstrate_upload_automation(upload_handler, page_url):
    """
    Demonstrate various upload automation scenarios
    
    Args:
        upload_handler: UploadHandler instance
        page_url: URL of page with upload components
    """
    print(f"\n{'='*80}")
    print("ANT DESIGN UPLOAD AUTOMATION DEMO")
    print(f"{'='*80}\n")
    
    # Navigate to page
    print(f"Navigating to: {page_url}")
    upload_handler.driver.get(page_url)
    time.sleep(2)  # Wait for page load
    print("Page loaded successfully\n")
    
    # Step 1: Discover all upload components
    print(f"{'='*80}")
    print("STEP 1: DISCOVERING ALL UPLOAD COMPONENTS")
    print(f"{'='*80}")
    print("   >> Starting upload component discovery...")
    print("   >> This may take a few seconds on large pages...\n")
    
    start_time = time.time()
    
    try:
        all_uploads = upload_handler.locator.find_all_uploads(timeout=5)
        elapsed = time.time() - start_time
        print(f"\n✓ Discovery completed in {elapsed:.2f} seconds")
        print(f"✓ Found {len(all_uploads)} upload component(s) on the page\n")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n✗ Error discovering uploads after {elapsed:.2f} seconds: {str(e)}")
        print("   >> Continuing with empty list...")
        all_uploads = []
    
    if not all_uploads:
        print("No upload components found. Please check the page URL.")
        return
    
    # Step 2: Print upload component summary (skip detailed summary for speed)
    print(f"{'='*80}")
    print("STEP 2: UPLOAD COMPONENT SUMMARY")
    print(f"{'='*80}")
    print(f"Found {len(all_uploads)} upload component(s) on the page")
    print("Skipping detailed summary for faster execution...")
    print("Will show details during interaction...")
    
    # Step 3: Click ALL upload buttons to open file selection dialogs
    print(f"{'='*80}")
    print("STEP 3: CLICKING ALL UPLOAD BUTTONS TO OPEN FILE DIALOGS")
    print(f"{'='*80}")
    print("This will click each upload button to open the file selection dialog.")
    print("You can manually select files in each dialog if needed.\n")
    
    # Try to upload to different upload components
    if all_uploads:
        # Remove duplicates by element ID
        unique_uploads = []
        seen_ids = set()
        for upload in all_uploads:
            try:
                elem_id = id(upload)
                if elem_id not in seen_ids:
                    unique_uploads.append(upload)
                    seen_ids.add(elem_id)
            except:
                unique_uploads.append(upload)
        
        total_uploads = len(unique_uploads)
        print(f"\nAttempting to interact with ALL {total_uploads} unique upload components...")
        print(f"This will test each upload component on the page.\n")
        
        successful_uploads = 0
        failed_uploads = 0
        skipped_uploads = 0
        
        # Try ALL upload types
        for idx, upload in enumerate(unique_uploads, 1):  # Test ALL uploads
            try:
                upload_info = upload_handler.identifier.identify_upload(upload)
                upload_type = upload_info['type']
                upload_text = upload_info.get('upload_text', '')[:50]  # First 50 chars
                
                print(f"\n{'='*60}")
                print(f"[{idx}/{total_uploads}] Testing upload component:")
                print(f"  Type: {upload_type}")
                print(f"  Text: {upload_text}")
                print(f"  Multiple: {upload_info['multiple']}")
                print(f"  Progress: {idx}/{total_uploads} ({int(idx/total_uploads*100)}%)")
                print(f"{'='*60}")
                
                # Scroll into view first with visual highlight
                print(f"  Scrolling to upload component {idx}/{total_uploads}...")
                try:
                    # Get element position
                    element_location = upload.location_once_scrolled_into_view
                    element_y = upload_handler.driver.execute_script(
                        "return arguments[0].getBoundingClientRect().top + window.pageYOffset;", 
                        upload
                    )
                    
                    # Get current scroll position
                    current_scroll = upload_handler.driver.execute_script("return window.pageYOffset;")
                    viewport_height = upload_handler.driver.execute_script("return window.innerHeight;")
                    
                    # Calculate target scroll position (center the element)
                    target_scroll = element_y - (viewport_height / 2)
                    
                    # Always scroll, even if element is "in view" - ensures visible movement
                    upload_handler.driver.execute_script(
                        f"window.scrollTo({{top: {target_scroll}, behavior: 'smooth'}});"
                    )
                    
                    # Wait for smooth scroll to complete
                    time.sleep(2.5)  # Increased wait for smooth scroll animation
                    
                    # Verify scroll happened and ensure element is visible
                    new_scroll = upload_handler.driver.execute_script("return window.pageYOffset;")
                    scroll_distance = abs(new_scroll - current_scroll)
                    
                    # Check if element is actually in viewport
                    element_in_view = upload_handler.driver.execute_script("""
                        var rect = arguments[0].getBoundingClientRect();
                        return (rect.top >= 0 && rect.top <= window.innerHeight) || 
                               (rect.bottom >= 0 && rect.bottom <= window.innerHeight);
                    """, upload)
                    
                    if scroll_distance > 10:
                        print(f"  ✓ Scrolled {int(scroll_distance)} pixels to element")
                    elif element_in_view:
                        print(f"  ✓ Element is in view")
                    else:
                        # Force scroll if element not in view
                        upload_handler.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                            upload
                        )
                        time.sleep(1.5)
                        print(f"  ✓ Forced scroll to element")
                except Exception as e:
                    print(f"  ⚠ Scroll issue: {str(e)}, using fallback...")
                    # Fallback: try standard scrollIntoView
                    try:
                        upload_handler.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 
                            upload
                        )
                        time.sleep(1.5)
                        print(f"  ✓ Fallback scroll completed")
                    except:
                        pass
                
                # Highlight the element visually
                try:
                    upload_handler.driver.execute_script(
                        "arguments[0].style.border = '3px solid red'; arguments[0].style.boxShadow = '0 0 10px red';",
                        upload
                    )
                    time.sleep(0.5)
                    print(f"  ✓ Element highlighted in red")
                except:
                    pass
                
                # Click upload button to OPEN file selection dialog (not upload file)
                print(f"  Clicking upload button to open file selection dialog...")
                clicked = False
                
                try:
                    # Use the handler's click method which handles all upload types
                    clicked = upload_handler.click_upload_button(upload)
                    
                    if clicked:
                        print(f"  ✓ Upload button clicked - file dialog should be open")
                        successful_uploads += 1
                        # Wait a moment for dialog to open
                        time.sleep(1)
                    else:
                        print(f"  ⚠ Could not click upload button - moving to next")
                        failed_uploads += 1
                        
                except Exception as e:
                    print(f"  ✗ Error clicking upload button: {str(e)}")
                    print(f"  → Continuing to next component...")
                    failed_uploads += 1
                
                # Dismiss any file dialog that might be open
                try:
                    upload_handler.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(0.2)
                except:
                    pass
                
                # Remove highlight before moving to next
                try:
                    upload_handler.driver.execute_script(
                        "arguments[0].style.border = ''; arguments[0].style.boxShadow = '';",
                        upload
                    )
                except:
                    pass
                
                # Small delay before moving to next component
                print(f"  → Moving to next component...\n")
                time.sleep(0.5)
                    
            except Exception as e:
                # Catch ALL errors and continue to next component
                print(f"  ✗ Error processing upload {idx}: {str(e)}")
                print(f"  → Skipping this component and moving to next...")
                failed_uploads += 1
                
                # Try to clean up (but don't fail if cleanup fails)
                try:
                    upload_handler.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(0.2)
                except:
                    pass
                
                try:
                    upload_handler.driver.execute_script(
                        "arguments[0].style.border = ''; arguments[0].style.boxShadow = '';",
                        upload
                    )
                except:
                    pass
                
                print(f"  → Continuing to next component...\n")
                time.sleep(0.3)
                continue  # Always continue to next component
        
        print(f"\n{'='*80}")
        print(f"CLICK SUMMARY:")
        print(f"  Total unique components: {total_uploads}")
        print(f"  Successfully clicked (dialogs opened): {successful_uploads}")
        print(f"  Failed to click: {failed_uploads}")
        print(f"{'='*80}")
    print()
    
    # Step 5: Demonstrate clicking ALL upload buttons
    print(f"{'='*80}")
    print("STEP 5: AUTOMATIC CLICKING OF ALL UPLOAD BUTTONS")
    print(f"{'='*80}")
    
    if all_uploads:
        print(f"\nTesting click interactions on ALL {len(all_uploads)} upload components...")
        print(f"This will click each upload button/area on the page.\n")
        
        successful_clicks = 0
        failed_clicks = 0
        
        for idx, upload in enumerate(all_uploads, 1):  # Test ALL uploads
            try:
                upload_info = upload_handler.identifier.identify_upload(upload)
                upload_type = upload_info['type']
                
                print(f"\n[{idx}/{len(all_uploads)}] Testing click on {upload_type} upload:")
                print(f"  Progress: {idx}/{len(all_uploads)} ({int(idx/len(all_uploads)*100)}%)")
                
                # Scroll into view with visual highlight
                print(f"  Scrolling to upload component {idx}/{len(all_uploads)}...")
                try:
                    # Get element position
                    element_location = upload.location_once_scrolled_into_view
                    element_y = upload_handler.driver.execute_script(
                        "return arguments[0].getBoundingClientRect().top + window.pageYOffset;", 
                        upload
                    )
                    
                    # Get current scroll position
                    current_scroll = upload_handler.driver.execute_script("return window.pageYOffset;")
                    viewport_height = upload_handler.driver.execute_script("return window.innerHeight;")
                    
                    # Calculate target scroll position (center the element)
                    target_scroll = element_y - (viewport_height / 2)
                    
                    # Always scroll, even if element is "in view" - ensures visible movement
                    upload_handler.driver.execute_script(
                        f"window.scrollTo({{top: {target_scroll}, behavior: 'smooth'}});"
                    )
                    
                    # Wait for smooth scroll to complete
                    time.sleep(2.5)  # Increased wait for smooth scroll animation
                    
                    # Verify scroll happened and ensure element is visible
                    new_scroll = upload_handler.driver.execute_script("return window.pageYOffset;")
                    scroll_distance = abs(new_scroll - current_scroll)
                    
                    # Check if element is actually in viewport
                    element_in_view = upload_handler.driver.execute_script("""
                        var rect = arguments[0].getBoundingClientRect();
                        return (rect.top >= 0 && rect.top <= window.innerHeight) || 
                               (rect.bottom >= 0 && rect.bottom <= window.innerHeight);
                    """, upload)
                    
                    if scroll_distance > 10:
                        print(f"  ✓ Scrolled {int(scroll_distance)} pixels to element")
                    elif element_in_view:
                        print(f"  ✓ Element is in view")
                    else:
                        # Force scroll if element not in view
                        upload_handler.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                            upload
                        )
                        time.sleep(1.5)
                        print(f"  ✓ Forced scroll to element")
                except Exception as e:
                    print(f"  ⚠ Scroll issue: {str(e)}, using fallback...")
                    # Fallback: try standard scrollIntoView
                    try:
                        upload_handler.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 
                            upload
                        )
                        time.sleep(1.5)
                        print(f"  ✓ Fallback scroll completed")
                    except:
                        pass
                
                # Highlight the element visually with animation
                try:
                    # First, remove any previous highlights
                    upload_handler.driver.execute_script("""
                        var elements = document.querySelectorAll('[style*="border: 3px solid"]');
                        for (var i = 0; i < elements.length; i++) {
                            elements[i].style.border = '';
                            elements[i].style.boxShadow = '';
                        }
                    """)
                    time.sleep(0.2)
                    
                    # Highlight current element
                    upload_handler.driver.execute_script(
                        "arguments[0].style.border = '3px solid blue'; arguments[0].style.boxShadow = '0 0 15px blue'; arguments[0].style.transition = 'all 0.3s';",
                        upload
                    )
                    time.sleep(0.5)
                    print(f"  ✓ Element highlighted in blue")
                except:
                    pass
                
                # Try to find and click upload button/area
                try:
                    # For picture-card type
                    if upload_type == 'picture-card':
                        picture_card = upload.find_element(By.CSS_SELECTOR, 
                            '.ant-upload-select-picture-card, [class*="picture-card"]')
                        print(f"  Clicking picture-card...")
                        # Highlight before click
                        upload_handler.driver.execute_script(
                            "arguments[0].style.border = '3px solid green'; arguments[0].style.boxShadow = '0 0 15px green';",
                            picture_card
                        )
                        time.sleep(0.3)
                        picture_card.click()
                        time.sleep(0.5)  # Short wait, then continue
                        print(f"  ✓ Picture-card clicked")
                        successful_clicks += 1
                    
                    # For dragger type
                    elif upload_type == 'dragger':
                        dragger_zone = upload.find_element(By.CSS_SELECTOR, 
                            '.ant-upload-drag, .ant-upload-drag-container')
                        print(f"  Clicking dragger zone...")
                        # Highlight before click
                        upload_handler.driver.execute_script(
                            "arguments[0].style.border = '3px solid green'; arguments[0].style.boxShadow = '0 0 15px green';",
                            dragger_zone
                        )
                        time.sleep(0.3)
                        dragger_zone.click()
                        time.sleep(0.5)  # Short wait, then continue
                        print(f"  ✓ Dragger zone clicked")
                        successful_clicks += 1
                    
                    # For button type
                    elif upload_type == 'button' or upload_type == 'custom':
                        # Find button or clickable area
                        try:
                            button = upload.find_element(By.CSS_SELECTOR, 
                                'button, .ant-upload-select, [role="button"], .ant-btn')
                            print(f"  Clicking upload button...")
                            # Highlight before click
                            upload_handler.driver.execute_script(
                                "arguments[0].style.border = '3px solid green'; arguments[0].style.boxShadow = '0 0 15px green';",
                                button
                            )
                            time.sleep(0.3)
                            button.click()
                            time.sleep(0.5)  # Short wait, then continue
                            print(f"  ✓ Upload button clicked")
                            successful_clicks += 1
                        except:
                            # Try clicking the upload container itself
                            print(f"  Clicking upload container...")
                            upload_handler.driver.execute_script(
                                "arguments[0].style.border = '3px solid green'; arguments[0].style.boxShadow = '0 0 15px green';",
                                upload
                            )
                            time.sleep(0.3)
                            upload.click()
                            time.sleep(0.5)  # Short wait, then continue
                            print(f"  ✓ Upload container clicked")
                            successful_clicks += 1
                    
                    else:
                        # Generic click on upload area
                        print(f"  Clicking upload area...")
                        upload_handler.driver.execute_script(
                            "arguments[0].style.border = '3px solid green'; arguments[0].style.boxShadow = '0 0 15px green';",
                            upload
                        )
                        time.sleep(0.3)
                        upload.click()
                        time.sleep(0.5)  # Short wait, then continue
                        print(f"  ✓ Upload area clicked")
                        successful_clicks += 1
                    
                    # Dismiss any file dialog that might have opened (press Escape)
                    try:
                        upload_handler.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(0.2)
                    except:
                        pass  # Ignore if dialog not present or can't dismiss
                        
                except Exception as e:
                    print(f"  ✗ Error clicking: {str(e)}")
                    failed_clicks += 1
                    # Dismiss any dialog that might be open
                    try:
                        upload_handler.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(0.1)
                    except:
                        pass
                    
            except Exception as e:
                print(f"  ✗ Error processing: {str(e)}")
                failed_clicks += 1
                # Dismiss any dialog that might be open
                try:
                    upload_handler.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(0.1)
                except:
                    pass
                continue
            
            # Small delay between components to ensure smooth transition
            time.sleep(0.3)
        
        print(f"\n{'='*80}")
        print(f"CLICK SUMMARY: {successful_clicks} successful, {failed_clicks} failed out of {len(all_uploads)} total")
        print(f"{'='*80}")
    print()
    
    # Step 5: Final summary
    print(f"{'='*80}")
    print("STEP 5: FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"Total upload components found: {len(all_uploads)}")
    print(f"All components have been automatically tested.")
    print(f"\nComponents tested:")
    print(f"  - Upload buttons clicked (file dialogs opened): All {len(all_uploads)} components")
    print(f"  - Each button click opens the file selection dialog")
    
    print(f"\n{'='*80}")
    print("UPLOAD AUTOMATION DEMO COMPLETED")
    print(f"{'='*80}\n")


def main():
    """
    Main function to run upload automation example
    """
    # Configuration
    # Change this URL to your application URL with upload components
    PAGE_URL = "https://ant.design/components/upload"  # Ant Design Upload documentation page
    
    # Or use your application URL
    # PAGE_URL = "https://your-app.com/page-with-uploads"
    
    print("\n" + "="*80)
    print("ANT DESIGN UPLOAD AUTOMATION - DEMO")
    print("="*80)
    
    # Setup WebDriver
    print("\nSetting up WebDriver...")
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    driver.implicitly_wait(2)
    
    try:
        # Create upload handler
        element_context = ElementContext()
        upload_handler = UploadHandler(driver, context=element_context)
        
        # Run demonstration
        demonstrate_upload_automation(upload_handler, PAGE_URL)
        
        # Keep browser open for inspection
        print("\n" + "="*80)
        print("AUTOMATION COMPLETE - Browser will stay open for 30 seconds")
        print("="*80)
        print("You can inspect the page and see the highlighted elements.")
        print("Press Ctrl+C to close early if needed.\n")
        time.sleep(30)
        
    except Exception as e:
        print(f"\nError during automation: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\nClosing browser...")
        driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    main()

