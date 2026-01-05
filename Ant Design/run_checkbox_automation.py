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
        print("="*70)
        print("ANT DESIGN CHECKBOX AUTOMATION - DEMO")
        print("="*70)
        
        # Setup driver
        print("\n[1/6] Setting up WebDriver...")
        driver = setup_driver()
        print("   [OK] WebDriver initialized")
        
        # Create context and handler
        print("\n[2/6] Initializing Checkbox Handler...")
        element_context = ElementContext()
        checkbox_handler = CheckboxHandler(driver, context=element_context)
        print("   [OK] Checkbox Handler ready")
        
        # Navigate to Ant Design Checkbox demo page
        print("\n[3/6] Navigating to Ant Design Checkbox demo page...")
        checkbox_page_url = "https://ant.design/components/checkbox"
        driver.get(checkbox_page_url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-checkbox, .ant-checkbox-wrapper, input[type="checkbox"]')))
        print(f"   [OK] Page loaded: {checkbox_page_url}")
        time.sleep(2)  # Allow React components to fully render
        
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
        checkboxes = checkbox_handler.locator.find_all_checkboxes(timeout=5)
        total_checkboxes_found = len(checkboxes)
        print(f"   [RESULT] Found {total_checkboxes_found} checkbox(es) on the page")
        
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
        print("   Initial Checkbox States (showing first 15):")
        for idx, checkbox in enumerate(checkboxes[:15], 1):  # Show first 15
            try:
                print(f"      [ANALYZE] Checkbox {idx}/{min(15, len(checkboxes))}: Identifying properties...")
                checkbox_info = checkbox_handler.identifier.identify_checkbox_type(checkbox)
                state = "CHECKED" if checkbox_info['checked'] else "UNCHECKED"
                if checkbox_info['indeterminate']:
                    state = "INDETERMINATE"
                disabled = " (DISABLED)" if checkbox_info['disabled'] else ""
                label = checkbox_info.get('label_text', 'N/A')[:30]
                group = checkbox_info.get('group_name', '')
                if group:
                    print(f"      [RESULT] Checkbox {idx}: '{label}' - {state}{disabled} [Group: {group}]")
                else:
                    print(f"      [RESULT] Checkbox {idx}: '{label}' - {state}{disabled}")
            except Exception as e:
                print(f"      [ERROR] Checkbox {idx}: Failed to analyze - {str(e)[:30]}")
        
        # Count initial statistics for all checkboxes
        print("\n   [ANALYSIS] Counting initial statistics for all checkboxes...")
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
        
        # Print full summary
        print("\n" + "="*70)
        print("CHECKBOX SUMMARY")
        print("="*70)
        checkbox_handler.print_checkboxes_summary()
        
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
        
        # Group checkboxes by name attribute
        checkboxes_by_group = {}
        individual_checkboxes = []
        
        print(f"   [INFO] Analyzing {min(20, len(checkboxes))} checkboxes for grouping...")
        for idx, checkbox in enumerate(checkboxes[:20], 1):  # Process first 20 checkboxes
            try:
                print(f"      [ANALYZE] Checkbox {idx}/{min(20, len(checkboxes))}: Identifying checkbox type...")
                checkbox_info = checkbox_handler.identifier.identify_checkbox_type(checkbox)
                group_name = checkbox_info.get('group_name')
                label = checkbox_info.get('label_text', 'Unknown')
                
                if group_name:
                    if group_name not in checkboxes_by_group:
                        checkboxes_by_group[group_name] = []
                        print(f"      [GROUP] Found new group: {group_name}")
                    checkboxes_by_group[group_name].append((checkbox, checkbox_info, label))
                    print(f"      [GROUP] Added '{label}' to group '{group_name}'")
                else:
                    individual_checkboxes.append((checkbox, checkbox_info, label))
                    print(f"      [INDIVIDUAL] Found individual checkbox: '{label}'")
            except Exception as e:
                print(f"      [ERROR] Failed to analyze checkbox {idx}: {str(e)[:50]}")
        
        print(f"   [RESULT] Found {len(checkboxes_by_group)} checkbox groups and {len(individual_checkboxes)} individual checkboxes")
        
        # Process groups (check multiple in each group to demonstrate multiple selection)
        if checkboxes_by_group:
            print("\n   " + "="*65)
            print("   [SECTION] Processing Checkbox Groups")
            print("   " + "="*65)
            for group_idx, (group_name, group_checkboxes) in enumerate(list(checkboxes_by_group.items())[:5], 1):  # First 5 groups
                print(f"\n   [GROUP {group_idx}] Group: {group_name} ({len(group_checkboxes)} options)")
                print(f"      [INFO] Attempting to check multiple checkboxes from this group...")
                
                checked_in_group = 0
                for checkbox_idx, (checkbox, checkbox_info, label) in enumerate(group_checkboxes[:3], 1):  # Try first 3 in group
                    try:
                        print(f"      [CHECK] Checkbox {checkbox_idx}: '{label}'")
                        print(f"         [STATUS] Disabled: {checkbox_info['disabled']}, Checked: {checkbox_info['checked']}, Indeterminate: {checkbox_info['indeterminate']}")
                        
                        if not checkbox_info['disabled']:
                            if not checkbox_info['checked']:
                                print(f"      [ACTION] → Attempting to check: '{label}'")
                                print(f"         [STEP 1] Locating clickable checkbox element...")
                                success = checkbox_handler._check_checkbox_element(checkbox, retry_count=3, retry_delay=0.5)
                                if success:
                                    checked_count += 1
                                    checked_in_group += 1
                                    print(f"         [SUCCESS] ✓ Checkbox '{label}' checked successfully!")
                                    print(f"         [WAIT] Waiting for UI to update...")
                                    time.sleep(0.5)  # Wait for UI update
                                else:
                                    failed_count += 1
                                    print(f"         [FAILED] ✗ Failed to check checkbox '{label}'")
                            else:
                                print(f"         [SKIP] Checkbox is already checked, skipping...")
                                checked_in_group += 1
                        else:
                            print(f"         [SKIP] Checkbox is disabled, skipping...")
                    except Exception as e:
                        print(f"         [ERROR] ✗ Error checking checkbox: {str(e)[:50]}")
                
                print(f"      [COMPLETE] Group '{group_name}' - {checked_in_group} checkbox(es) checked")
        
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
                            print(f"         [STEP 1] Locating clickable checkbox element...")
                            success = checkbox_handler._check_checkbox_element(checkbox, retry_count=3, retry_delay=0.5)
                            if success:
                                checked_count += 1
                                print(f"         [SUCCESS] ✓ Individual checkbox '{label}' checked successfully!")
                                print(f"         [WAIT] Waiting for UI to update...")
                                time.sleep(0.5)
                            else:
                                failed_count += 1
                                print(f"         [FAILED] ✗ Failed to check individual checkbox '{label}'")
                        else:
                            # Try unchecking if already checked
                            print(f"      [ACTION] → Attempting to uncheck individual checkbox: '{label}'")
                            success = checkbox_handler._uncheck_checkbox_element(checkbox, retry_count=3, retry_delay=0.5)
                            if success:
                                unchecked_count += 1
                                print(f"         [SUCCESS] ✓ Individual checkbox '{label}' unchecked successfully!")
                                time.sleep(0.5)
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
        
        # Final summary
        print("\n" + "="*70)
        print("FINAL CHECKBOX SUMMARY")
        print("="*70)
        final_summary = checkbox_handler.get_all_checkboxes_summary(timeout=2)
        print(f"   Total checkboxes: {final_summary['total_count']}")
        print(f"   Total groups: {final_summary['total_groups']}")
        print(f"   Checked: {final_summary['checked_count']}")
        print(f"   Unchecked: {final_summary['total_count'] - final_summary['checked_count']}")
        print(f"   Disabled: {final_summary['disabled_count']}")
        print(f"   Indeterminate: {final_summary['indeterminate_count']}")
        
        if final_summary['groups']:
            print("\n   Group Details:")
            for group_name, group_info in list(final_summary['groups'].items())[:5]:
                print(f"      {group_name}:")
                print(f"         Options: {group_info.get('total_options', 0)}")
                print(f"         Checked: {group_info.get('checked_count', 0)}")
                if group_info.get('checked_options'):
                    print(f"         Checked Options: {', '.join(group_info['checked_options'][:3])}")
        
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
        
        # Keep browser open for 3 seconds to see results
        print("\nKeeping browser open for 3 seconds to view results...")
        time.sleep(3)
        
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
    print("\n" + "="*70)
    print("ANT DESIGN CHECKBOX AUTOMATION RUNNER")
    print("="*70)
    print("\nOptions:")
    print("  1. Run demo on Ant Design Checkbox documentation page (default)")
    print("  2. Run on custom URL")
    print("\nUsage:")
    print("  python run_checkbox_automation.py              # Demo mode")
    print("  python run_checkbox_automation.py <URL>         # Custom URL")
    print("="*70 + "\n")
    
    if len(sys.argv) > 1:
        # Custom URL provided
        custom_url = sys.argv[1]
        if not custom_url.startswith('http'):
            print("[WARN] Warning: URL should start with http:// or https://")
            print(f"  Attempting to use: https://{custom_url}")
            custom_url = f"https://{custom_url}"
        run_checkbox_automation_custom_url(custom_url)
    else:
        # Run demo
        run_checkbox_automation_demo()

