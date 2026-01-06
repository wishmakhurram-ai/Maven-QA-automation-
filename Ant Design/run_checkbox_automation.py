"""
Standalone Python script to run Ant Design Checkbox automation
Run with: python run_checkbox_automation.py
"""
import sys
import os
import time

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Import framework components
from framework.components.checkbox_handler import CheckboxHandler
from framework.context.element_context import ElementContext


def setup_driver():
    """Setup and configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(2)
    return driver


def run_checkbox_automation_demo():
    """Run checkbox automation demonstration"""
    driver = None
    try:
        print("="*70, flush=True)
        print("ANT DESIGN CHECKBOX AUTOMATION - DEMO", flush=True)
        print("="*70, flush=True)
        
        # Setup driver
        print("\n[1/6] Setting up WebDriver...", flush=True)
        try:
            driver = setup_driver()
            print("   [OK] WebDriver initialized", flush=True)
        except Exception as e:
            print(f"   [ERROR] Failed to initialize WebDriver: {str(e)}", flush=True)
            print("   [INFO] Make sure ChromeDriver is installed and in PATH", flush=True)
            return False
        
        # Create context and handler
        print("\n[2/6] Initializing Checkbox Handler...", flush=True)
        try:
            element_context = ElementContext()
            checkbox_handler = CheckboxHandler(driver, context=element_context)
            print("   [OK] Checkbox Handler ready", flush=True)
        except Exception as e:
            print(f"   [ERROR] Failed to initialize Checkbox Handler: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            return False
        
        # Navigate to Ant Design Checkbox demo page
        print("\n[3/6] Navigating to Ant Design Checkbox demo page...")
        checkbox_page_url = "https://ant.design/components/checkbox"
        print(f"   [INFO] Loading URL: {checkbox_page_url}")
        driver.get(checkbox_page_url)
        print(f"   [INFO] Page navigation complete, waiting for content...")
        
        # Wait for page to load with timeout protection
        try:
            wait = WebDriverWait(driver, 10)  # Reduced timeout
            print(f"   [INFO] Waiting for checkboxes to appear...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-checkbox, .ant-checkbox-wrapper, input[type="checkbox"]')))
            print(f"   [OK] Page loaded: {checkbox_page_url}")
        except Exception as e:
            print(f"   [WARN] Timeout waiting for checkboxes, continuing anyway: {str(e)[:50]}")
            print(f"   [INFO] Page may still be loading, will try to find checkboxes anyway...")
        
        print(f"   [INFO] Waiting for React components to render...")
        time.sleep(3)  # Allow React components to fully render
        print(f"   [OK] Ready to scan for checkboxes")
        
        # Scroll to load all content
        print("\n[4/6] Scrolling to load all checkbox components...")
        for scroll_position in [500, 1000, 1500, 2000, 2500, 3000]:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Find all checkboxes
        print("\n[5/6] Finding all checkboxes on the page...")
        print("   [STEP] Scanning page for Ant Design checkbox components...")
        print("   [INFO] Using locator-less detection (Ant Design classes, ARIA attributes)...")
        print("   [INFO] This may take a few seconds...")
        
        try:
            # Add timeout protection
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Checkbox finding operation timed out")
            
            # Use a simpler approach with direct timeout
            start_find_time = time.time()
            checkboxes = []
            
            try:
                checkboxes = checkbox_handler.locator.find_all_checkboxes(timeout=10)
            except Exception as e:
                print(f"   [WARN] Error during checkbox finding: {str(e)[:50]}")
                # Try fallback: direct find
                print(f"   [INFO] Trying fallback method...")
                try:
                    from selenium.webdriver.common.by import By
                    direct_checkboxes = driver.find_elements(By.CSS_SELECTOR, '.ant-checkbox-wrapper, input[type="checkbox"]')
                    checkboxes = direct_checkboxes[:50]  # Limit to first 50 to avoid hanging
                    print(f"   [INFO] Fallback found {len(checkboxes)} elements")
                except:
                    pass
            
            elapsed = time.time() - start_find_time
            total_checkboxes_found = len(checkboxes)
            print(f"   [RESULT] Found {total_checkboxes_found} checkbox(es) on the page (took {elapsed:.2f}s)")
            
        except Exception as e:
            print(f"   [ERROR] Failed to find checkboxes: {str(e)}")
            import traceback
            traceback.print_exc()
            checkboxes = []
            total_checkboxes_found = 0
        
        if total_checkboxes_found == 0:
            print("   [WARN] No checkboxes found on the page")
            return True
        
        # Track initial statistics
        initial_disabled_count = 0
        initial_checked_count = 0
        initial_indeterminate_count = 0
        
        # Show initial summary and track initial statistics
        print("\n   [ANALYSIS] Analyzing initial checkbox states...")
        print("   " + "-"*65)
        print("   Initial Checkbox States (showing first 10):")
        
        # Limit analysis to avoid hanging
        max_checkboxes_to_analyze = min(10, len(checkboxes))
        for idx, checkbox in enumerate(checkboxes[:max_checkboxes_to_analyze], 1):
            try:
                print(f"      [ANALYZE] Checkbox {idx}/{max_checkboxes_to_analyze}: Identifying properties...", flush=True)
                # Add timeout protection for each identification
                start_identify = time.time()
                checkbox_info = checkbox_handler.identifier.identify_checkbox_type(checkbox)
                elapsed_identify = time.time() - start_identify
                
                if elapsed_identify > 2:
                    print(f"         [WARN] Identification took {elapsed_identify:.2f}s (slow)")
                
                state = "CHECKED" if checkbox_info['checked'] else "UNCHECKED"
                if checkbox_info.get('indeterminate'):
                    state = "INDETERMINATE"
                disabled = " (DISABLED)" if checkbox_info.get('disabled') else ""
                label = checkbox_info.get('label_text', 'N/A')[:30] or 'N/A'
                group = checkbox_info.get('group_name', '')
                if group:
                    print(f"      [RESULT] Checkbox {idx}: '{label}' - {state}{disabled} [Group: {group}]")
                else:
                    print(f"      [RESULT] Checkbox {idx}: '{label}' - {state}{disabled}")
            except Exception as e:
                print(f"      [ERROR] Checkbox {idx}: Failed to analyze - {str(e)[:50]}")
                continue
        
        # Count initial statistics for all checkboxes (with limit to avoid hanging)
        print("\n   [ANALYSIS] Counting initial statistics for checkboxes...")
        print(f"   [INFO] Analyzing up to {min(50, len(checkboxes))} checkboxes to avoid timeout...")
        max_stats_checkboxes = min(50, len(checkboxes))  # Limit to avoid hanging
        for idx, checkbox in enumerate(checkboxes[:max_stats_checkboxes], 1):
            try:
                if idx % 10 == 0:
                    print(f"      [PROGRESS] Analyzed {idx}/{max_stats_checkboxes} checkboxes...", flush=True)
                checkbox_info = checkbox_handler.identifier.identify_checkbox_type(checkbox)
                if checkbox_info.get('disabled'):
                    initial_disabled_count += 1
                if checkbox_info.get('checked'):
                    initial_checked_count += 1
                if checkbox_info.get('indeterminate'):
                    initial_indeterminate_count += 1
            except Exception as e:
                # Silently skip errors to continue processing
                continue
        print(f"   [OK] Statistics collected from {max_stats_checkboxes} checkboxes")
        
        # Print full summary (with timeout protection)
        print("\n" + "="*70)
        print("CHECKBOX SUMMARY")
        print("="*70)
        try:
            # Limit summary to avoid hanging
            print("   [INFO] Generating summary (this may take a moment)...")
            checkbox_handler.print_checkboxes_summary()
        except Exception as e:
            print(f"   [WARN] Error generating full summary: {str(e)[:50]}")
            print(f"   [INFO] Showing basic statistics instead...")
            print(f"   Total checkboxes found: {total_checkboxes_found}")
            print(f"   Checked: {initial_checked_count}")
            print(f"   Disabled: {initial_disabled_count}")
            print(f"   Indeterminate: {initial_indeterminate_count}")
        
        # Test checking/unchecking checkboxes
        print("\n" + "="*70)
        print("CHECKING/UNCHECKING CHECKBOXES - DEMO")
        print("="*70)
        
        checked_count = 0
        unchecked_count = 0
        failed_count = 0
        
        # Process checkboxes directly
        print("\n   [STEP] Processing Checkboxes Directly...")
        print("   [INFO] Analyzing checkbox elements and grouping them...")
        
        # First, find all checkbox groups on the page
        print("   [INFO] Detecting checkbox groups by finding .ant-checkbox-group containers...")
        from selenium.webdriver.common.by import By
        try:
            group_containers = driver.find_elements(By.CSS_SELECTOR, '.ant-checkbox-group')
            print(f"   [RESULT] Found {len(group_containers)} checkbox group container(s)")
        except:
            group_containers = []
            print(f"   [WARN] Could not find group containers")
        
        # Group checkboxes by their container group
        checkboxes_by_group = {}
        individual_checkboxes = []
        processed_checkbox_ids = set()
        
        # Process groups first - optimized
        for group_idx, group_container in enumerate(group_containers, 1):
            try:
                # Optimized: Get group identifier and type in one JavaScript call
                group_data = driver.execute_script("""
                    var g=arguments[0];
                    var gc=g.className||'';
                    var p=g.parentElement,pc=p?p.className||'':'';
                    var isGrid=gc.includes('ant-col')||gc.toLowerCase().includes('grid')||pc.includes('ant-row')||pc.includes('ant-col')||g.querySelector('.ant-col,.ant-row')!==null;
                    var wrappers=g.querySelectorAll('.ant-checkbox-wrapper');
                    return {
                        groupId:g.getAttribute('data-attr-id')||g.getAttribute('data-atr-id')||'',
                        isGrid:isGrid,
                        wrapperCount:wrappers?wrappers.length:0
                    };
                """, group_container)
                
                group_id = group_data.get('groupId') or f'group-{group_idx}'
                group_type = 'Grid Layout' if group_data.get('isGrid') else 'Checkbox Group'
                
                print(f"   [GROUP {group_idx}] Found {group_type}: {group_id}")
                
                # Find all checkbox wrappers in this group
                group_wrappers = group_container.find_elements(By.CSS_SELECTOR, '.ant-checkbox-wrapper')
                print(f"      [INFO] Found {len(group_wrappers)} checkbox wrapper(s) in this group")
                
                if group_id not in checkboxes_by_group:
                    checkboxes_by_group[group_id] = {
                        'type': group_type,
                        'checkboxes': []
                    }
                
                # Batch process wrappers with cached info
                seen_labels = {}
                for wrapper in group_wrappers:
                    try:
                        elem_id = id(wrapper)
                        if elem_id not in processed_checkbox_ids:
                            processed_checkbox_ids.add(elem_id)
                            checkbox_info = checkbox_handler.identifier.identify_checkbox_type(wrapper, fast_mode=True)
                            label = (checkbox_info.get('label_text') or 
                                    checkbox_info.get('aria_label') or 
                                    checkbox_info.get('value') or 
                                    'Unknown')
                            
                            # Handle duplicate labels efficiently
                            if label in seen_labels:
                                seen_labels[label] += 1
                                label = f"{label} ({seen_labels[label]})"
                            else:
                                seen_labels[label] = 1
                            
                            checkboxes_by_group[group_id]['checkboxes'].append((wrapper, checkbox_info, label))
                            print(f"      [ADDED] '{label}' to {group_type}")
                    except:
                        continue
            except Exception as e:
                print(f"   [ERROR] Error processing group {group_idx}: {str(e)[:50]}")
                continue
        
        # Process individual checkboxes (not in groups)
        print(f"\n   [INFO] Finding individual checkboxes (not in groups)...")
        max_checkboxes_to_process = min(30, len(checkboxes))
        for idx, checkbox in enumerate(checkboxes[:max_checkboxes_to_process], 1):
            try:
                elem_id = id(checkbox)
                if elem_id not in processed_checkbox_ids:
                    processed_checkbox_ids.add(elem_id)
                    checkbox_info = checkbox_handler.identifier.identify_checkbox_type(checkbox, fast_mode=True)
                    label = checkbox_info.get('label_text', 'Unknown') or 'Unknown'
                    
                    # Check if it's actually in a group (might have been missed)
                    if checkbox_info.get('group_name') or checkbox_info.get('group_id'):
                        # Try to find which group it belongs to
                        try:
                            group_container = checkbox.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-group")][1]')
                            group_id = group_container.get_attribute('data-attr-id') or group_container.get_attribute('data-atr-id') or f'group-{len(checkboxes_by_group) + 1}'
                            if group_id not in checkboxes_by_group:
                                checkboxes_by_group[group_id] = {
                                    'type': 'Checkbox Group',
                                    'checkboxes': []
                                }
                            checkboxes_by_group[group_id]['checkboxes'].append((checkbox, checkbox_info, label))
                        except:
                            individual_checkboxes.append((checkbox, checkbox_info, label))
                    else:
                        individual_checkboxes.append((checkbox, checkbox_info, label))
            except Exception as e:
                continue
        
        print(f"   [RESULT] Found {len(checkboxes_by_group)} checkbox groups and {len(individual_checkboxes)} individual checkboxes")
        
        # Process groups (check multiple in each group to demonstrate multiple selection)
        if checkboxes_by_group:
            print("\n   " + "="*65)
            print("   [SECTION] Processing Checkbox Groups and Grid Layouts")
            print("   " + "="*65)
            for group_idx, (group_id, group_data) in enumerate(list(checkboxes_by_group.items())[:10], 1):  # Process up to 10 groups
                group_type = group_data.get('type', 'Checkbox Group')
                group_checkboxes = group_data.get('checkboxes', [])
                
                print(f"\n   [GROUP {group_idx}] {group_type}: {group_id} ({len(group_checkboxes)} options)")
                print(f"      [INFO] Attempting to interact with checkboxes in this {group_type.lower()}...")
                
                checked_in_group = 0
                unchecked_in_group = 0
                
                # Process all checkboxes in the group - optimized with cached info
                for checkbox_idx, (checkbox, checkbox_info, label) in enumerate(group_checkboxes, 1):
                    try:
                        print(f"      [CHECK {checkbox_idx}/{len(group_checkboxes)}] '{label}'")
                        status_disabled = checkbox_info.get('disabled', False)
                        status_checked = checkbox_info.get('checked', False)
                        status_indeterminate = checkbox_info.get('indeterminate', False)
                        print(f"         [STATUS] Disabled: {status_disabled}, Checked: {status_checked}, Indeterminate: {status_indeterminate}")
                        
                        if not status_disabled:
                            if not status_checked and not status_indeterminate:
                                print(f"         [ACTION] → Checking: '{label}'")
                                # Pass cached info to avoid redundant identification
                                success = checkbox_handler._check_checkbox_element(checkbox, retry_count=2, retry_delay=0.3, cached_info=checkbox_info)
                                if success:
                                    checked_count += 1
                                    checked_in_group += 1
                                    print(f"         [SUCCESS] ✓ Checked!")
                                    time.sleep(0.2)  # Reduced wait time
                                else:
                                    failed_count += 1
                                    print(f"         [FAILED] ✗ Failed to check")
                            elif status_checked:
                                # For groups, keep some checked and uncheck a few to show toggle
                                if group_type == 'Grid Layout' or checkbox_idx <= 2:  # Uncheck first 2 in regular groups, or any in grid
                                    print(f"         [ACTION] → Unchecking: '{label}' (demonstrating toggle)")
                                    success = checkbox_handler._uncheck_checkbox_element(checkbox, retry_count=2, retry_delay=0.3, cached_info=checkbox_info)
                                    if success:
                                        unchecked_count += 1
                                        unchecked_in_group += 1
                                        print(f"         [SUCCESS] ✓ Unchecked!")
                                        time.sleep(0.2)  # Reduced wait time
                                    else:
                                        failed_count += 1
                                        print(f"         [FAILED] ✗ Failed to uncheck")
                                else:
                                    print(f"         [SKIP] Already checked, keeping checked")
                                    checked_in_group += 1
                            elif status_indeterminate:
                                # Check indeterminate checkboxes
                                print(f"         [ACTION] → Checking indeterminate: '{label}'")
                                success = checkbox_handler._check_checkbox_element(checkbox, retry_count=2, retry_delay=0.3, cached_info=checkbox_info)
                                if success:
                                    checked_count += 1
                                    checked_in_group += 1
                                    print(f"         [SUCCESS] ✓ Checked!")
                                    time.sleep(0.2)  # Reduced wait time
                                else:
                                    failed_count += 1
                                    print(f"         [FAILED] ✗ Failed to check")
                        else:
                            print(f"         [SKIP] Disabled, skipping...")
                    except Exception as e:
                        print(f"         [ERROR] ✗ Error: {str(e)[:50]}")
                        failed_count += 1
                
                print(f"      [COMPLETE] {group_type} '{group_id}' - {checked_in_group} checked, {unchecked_in_group} unchecked")
        
        # Process individual checkboxes
        if individual_checkboxes:
            print("\n   " + "="*65)
            print("   [SECTION] Processing Individual Checkboxes (Not in Groups)")
            print("   " + "="*65)
            for checkbox_idx, (checkbox, checkbox_info, label) in enumerate(individual_checkboxes[:5], 1):  # First 5 individual
                try:
                    print(f"\n   [INDIVIDUAL CHECKBOX {checkbox_idx}] '{label}'")
                    print(f"      [CHECK] Status check...")
                    print(f"         [STATUS] Disabled: {checkbox_info['disabled']}, Checked: {checkbox_info['checked']}, Indeterminate: {checkbox_info['indeterminate']}")
                    
                    if not checkbox_info['disabled']:
                        if not checkbox_info['checked']:
                            print(f"      [ACTION] → Attempting to check individual checkbox: '{label}'")
                            # Use cached info for better performance
                            success = checkbox_handler._check_checkbox_element(checkbox, retry_count=2, retry_delay=0.3, cached_info=checkbox_info)
                            if success:
                                checked_count += 1
                                print(f"         [SUCCESS] ✓ Individual checkbox '{label}' checked successfully!")
                                time.sleep(0.2)  # Reduced wait time
                            else:
                                failed_count += 1
                                print(f"         [FAILED] ✗ Failed to check individual checkbox '{label}'")
                        else:
                            # Try unchecking if already checked
                            print(f"      [ACTION] → Attempting to uncheck individual checkbox: '{label}'")
                            success = checkbox_handler._uncheck_checkbox_element(checkbox, retry_count=2, retry_delay=0.3, cached_info=checkbox_info)
                            if success:
                                unchecked_count += 1
                                print(f"         [SUCCESS] ✓ Individual checkbox '{label}' unchecked successfully!")
                                time.sleep(0.2)  # Reduced wait time
                            else:
                                failed_count += 1
                                print(f"         [FAILED] ✗ Failed to uncheck individual checkbox '{label}'")
                    else:
                        print(f"      [SKIP] Checkbox is disabled, skipping...")
                except Exception as e:
                    print(f"      [ERROR] ✗ Error: {str(e)[:50]}")
        
        print("\n   " + "="*65)
        print(f"   [SUMMARY] Selection Summary")
        print("   " + "="*65)
        print(f"      ✓ Successfully checked: {checked_count} checkbox(es)")
        print(f"      ✓ Successfully unchecked: {unchecked_count} checkbox(es)")
        print(f"      ✗ Failed operations: {failed_count} checkbox(es)")
        total_operations = checked_count + unchecked_count + failed_count
        if total_operations > 0:
            success_rate = int(((checked_count + unchecked_count) / total_operations) * 100)
            print(f"      [SUCCESS RATE] {success_rate}%")
        
        # Final summary (with timeout protection)
        print("\n" + "="*70)
        print("FINAL CHECKBOX SUMMARY")
        print("="*70)
        try:
            print("   [INFO] Generating final summary (this may take a moment)...")
            final_summary = checkbox_handler.get_all_checkboxes_summary(timeout=3)
            print(f"   Total checkboxes: {final_summary['total_count']}")
            print(f"   Total groups: {final_summary['total_groups']}")
            print(f"   Checked: {final_summary['checked_count']}")
            print(f"   Unchecked: {final_summary['total_count'] - final_summary['checked_count']}")
            print(f"   Disabled: {final_summary['disabled_count']}")
            print(f"   Indeterminate: {final_summary['indeterminate_count']}")
            
            if final_summary.get('groups'):
                print("\n   Group Details:")
                for group_name, group_info in list(final_summary['groups'].items())[:5]:
                    print(f"      {group_name}:")
                    print(f"         Options: {group_info.get('total_options', 0)}")
                    print(f"         Checked: {group_info.get('checked_count', 0)}")
                    if group_info.get('checked_options'):
                        print(f"         Checked Options: {', '.join(group_info['checked_options'][:3])}")
        except Exception as e:
            print(f"   [WARN] Error generating final summary: {str(e)[:50]}")
            print(f"   [INFO] Using basic statistics instead...")
            final_summary = {
                'total_count': total_checkboxes_found,
                'total_groups': len(checkboxes_by_group),
                'checked_count': initial_checked_count,
                'disabled_count': initial_disabled_count,
                'indeterminate_count': initial_indeterminate_count
            }
        
        # Get final statistics (reuse if already got)
        print("\n" + "="*70)
        print("GENERATING FINAL STATISTICS...")
        print("="*70)
        if 'final_summary' not in locals():
            try:
                final_summary = checkbox_handler.get_all_checkboxes_summary(timeout=2)
            except:
                final_summary = {
                    'total_count': total_checkboxes_found,
                    'total_groups': 0,
                    'checked_count': initial_checked_count,
                    'disabled_count': initial_disabled_count,
                    'indeterminate_count': initial_indeterminate_count
                }
        final_checked_count = final_summary['checked_count']
        final_disabled_count = final_summary['disabled_count']
        final_indeterminate_count = final_summary['indeterminate_count']
        
        # Generate comprehensive summary for manager
        print("\n" + "="*70)
        print("EXECUTION SUMMARY REPORT")
        print("="*70)
        print("\n📊 CHECKBOX COMPONENT STATISTICS")
        print("-" * 70)
        print(f"  Total Checkbox Components Found:     {total_checkboxes_found}")
        print(f"  Total Checkboxes Checked:             {checked_count}")
        print(f"  Total Checkboxes Unchecked:           {unchecked_count}")
        print(f"  Total Checkboxes Disabled:            {final_disabled_count}")
        print(f"  Total Checkboxes Checked (Final):    {final_checked_count}")
        print(f"  Total Checkboxes Indeterminate:       {final_indeterminate_count}")
        print("-" * 70)
        print("\n📈 ADDITIONAL METRICS")
        print("-" * 70)
        print(f"  Initial Checked Count:                {initial_checked_count}")
        print(f"  Initial Disabled Count:               {initial_disabled_count}")
        print(f"  Initial Indeterminate Count:          {initial_indeterminate_count}")
        print(f"  Newly Checked:                         {checked_count}")
        print(f"  Newly Unchecked:                      {unchecked_count}")
        total_operations = checked_count + unchecked_count + failed_count
        if total_operations > 0:
            success_rate = int(((checked_count + unchecked_count) / total_operations) * 100)
            print(f"  Operation Success Rate:              {success_rate}%")
        print(f"  Total Checkbox Groups:                {final_summary['total_groups']}")
        print("-" * 70)
        print("\n" + "="*70)
        print("[SUCCESS] CHECKBOX AUTOMATION COMPLETED SUCCESSFULLY")
        print("="*70)
        
        # Keep browser open for 5 seconds to see results
        print("\nKeeping browser open for 5 seconds to view results...")
        time.sleep(5)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()
            print("[OK] Browser closed")
    
    return True


def run_checkbox_automation_custom_url(url: str):
    """Run checkbox automation on a custom URL"""
    driver = None
    try:
        print("="*70)
        print(f"ANT DESIGN CHECKBOX AUTOMATION - CUSTOM URL")
        print("="*70)
        print(f"URL: {url}")
        
        # Setup driver
        print("\n[1/4] Setting up WebDriver...")
        driver = setup_driver()
        print("   [OK] WebDriver initialized")
        
        # Create context and handler
        print("\n[2/4] Initializing Checkbox Handler...")
        element_context = ElementContext()
        checkbox_handler = CheckboxHandler(driver, context=element_context)
        print("   [OK] Checkbox Handler ready")
        
        # Navigate to custom URL
        print(f"\n[3/4] Navigating to: {url}...")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-checkbox, .ant-checkbox-wrapper, input[type="checkbox"]')))
            print("   [OK] Page loaded with checkboxes detected")
        except:
            print("   [WARN] No checkboxes detected immediately, continuing...")
        
        time.sleep(2)
        
        # Scroll to load content
        for scroll_position in [500, 1000, 1500]:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Find and analyze checkboxes
        print("\n[4/4] Finding and analyzing checkboxes...")
        checkboxes = checkbox_handler.locator.find_all_checkboxes(timeout=5)
        total_checkboxes_found = len(checkboxes)
        print(f"   ✓ Found {total_checkboxes_found} checkbox(es)")
        
        # Track statistics
        initial_disabled_count = 0
        initial_checked_count = 0
        initial_indeterminate_count = 0
        checked_count = 0
        unchecked_count = 0
        failed_count = 0
        
        if checkboxes:
            # Count initial statistics
            print("\n   Analyzing initial checkbox states...")
            for checkbox in checkboxes:
                try:
                    checkbox_info = checkbox_handler.identifier.identify_checkbox_type(checkbox)
                    if checkbox_info['disabled']:
                        initial_disabled_count += 1
                    if checkbox_info['checked']:
                        initial_checked_count += 1
                    if checkbox_info['indeterminate']:
                        initial_indeterminate_count += 1
                except:
                    pass
            
            # Print summary
            checkbox_handler.print_checkboxes_summary()
            
            # Try to check/uncheck first few checkboxes
            print("\n   Attempting to check/uncheck checkboxes...")
            for idx, checkbox in enumerate(checkboxes[:5], 1):
                try:
                    checkbox_info = checkbox_handler.identifier.identify_checkbox_type(checkbox)
                    if not checkbox_info['disabled']:
                        label = checkbox_info.get('label_text', f'Checkbox {idx}')
                        if not checkbox_info['checked']:
                            print(f"      → Checking: {label}")
                            success = checkbox_handler.check_checkbox(
                                label,
                                identifier_type='auto',
                                retry_count=2,
                                retry_delay=0.3
                            )
                            if success:
                                checked_count += 1
                                print(f"         ✓ Checked")
                            else:
                                failed_count += 1
                                print(f"         ✗ Failed")
                        else:
                            print(f"      → Unchecking: {label}")
                            success = checkbox_handler.uncheck_checkbox(
                                label,
                                identifier_type='auto',
                                retry_count=2,
                                retry_delay=0.3
                            )
                            if success:
                                unchecked_count += 1
                                print(f"         ✓ Unchecked")
                            else:
                                failed_count += 1
                                print(f"         ✗ Failed")
                        time.sleep(0.5)
                except Exception as e:
                    failed_count += 1
                    print(f"      ✗ Error: {str(e)[:50]}")
        
        # Get final statistics
        print("\n" + "="*70)
        print("GENERATING FINAL STATISTICS...")
        print("="*70)
        final_summary = checkbox_handler.get_all_checkboxes_summary(timeout=2)
        final_checked_count = final_summary['checked_count']
        final_disabled_count = final_summary['disabled_count']
        final_indeterminate_count = final_summary['indeterminate_count']
        
        # Generate comprehensive summary for manager
        print("\n" + "="*70)
        print("EXECUTION SUMMARY REPORT")
        print("="*70)
        print("\n📊 CHECKBOX COMPONENT STATISTICS")
        print("-" * 70)
        print(f"  Total Checkbox Components Found:     {total_checkboxes_found}")
        print(f"  Total Checkboxes Checked:             {checked_count}")
        print(f"  Total Checkboxes Unchecked:           {unchecked_count}")
        print(f"  Total Checkboxes Disabled:            {final_disabled_count}")
        print(f"  Total Checkboxes Checked (Final):     {final_checked_count}")
        print(f"  Total Checkboxes Indeterminate:       {final_indeterminate_count}")
        print("-" * 70)
        print("\n📈 ADDITIONAL METRICS")
        print("-" * 70)
        print(f"  Initial Checked Count:                {initial_checked_count}")
        print(f"  Initial Disabled Count:               {initial_disabled_count}")
        print(f"  Initial Indeterminate Count:          {initial_indeterminate_count}")
        print(f"  Newly Checked:                         {checked_count}")
        print(f"  Newly Unchecked:                      {unchecked_count}")
        total_operations = checked_count + unchecked_count + failed_count
        if total_operations > 0:
            success_rate = int(((checked_count + unchecked_count) / total_operations) * 100)
            print(f"  Operation Success Rate:              {success_rate}%")
        print(f"  Total Checkbox Groups:                {final_summary['total_groups']}")
        print("-" * 70)
        print("\n" + "="*70)
        print("[SUCCESS] CHECKBOX AUTOMATION COMPLETED")
        print("="*70)
        print("\nKeeping browser open for 5 seconds...")
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()
            print("[OK] Browser closed")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*70, flush=True)
    print("ANT DESIGN CHECKBOX AUTOMATION RUNNER", flush=True)
    print("="*70, flush=True)
    print("\nOptions:", flush=True)
    print("  1. Run demo on Ant Design Checkbox documentation page (default)", flush=True)
    print("  2. Run on custom URL", flush=True)
    print("\nUsage:", flush=True)
    print("  python run_checkbox_automation.py              # Demo mode", flush=True)
    print("  python run_checkbox_automation.py <URL>         # Custom URL", flush=True)
    print("="*70 + "\n", flush=True)
    
    # Add quick test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("[TEST MODE] Quick test - checking imports and basic setup...", flush=True)
        try:
            from framework.components.checkbox_handler import CheckboxHandler
            from framework.context.element_context import ElementContext
            print("[OK] Imports successful", flush=True)
            print("[OK] Ready to run full automation", flush=True)
        except Exception as e:
            print(f"[ERROR] Import failed: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
        sys.exit(0)
    
    if len(sys.argv) > 1:
        # Custom URL provided
        custom_url = sys.argv[1]
        if not custom_url.startswith('http'):
            print("[WARN] Warning: URL should start with http:// or https://", flush=True)
            print(f"  Attempting to use: https://{custom_url}", flush=True)
            custom_url = f"https://{custom_url}"
        run_checkbox_automation_custom_url(custom_url)
    else:
        # Run demo
        print("[INFO] Starting automation...", flush=True)
        print("[INFO] This may take 30-60 seconds depending on page load...", flush=True)
        run_checkbox_automation_demo()

