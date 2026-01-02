"""
Standalone Python script to run Ant Design Radio automation
Run with: python run_radio_automation.py
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
from framework.components.radio_handler import RadioHandler
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


def run_radio_automation_demo():
    """Run radio automation demonstration"""
    driver = None
    try:
        print("="*70)
        print("ANT DESIGN RADIO AUTOMATION - DEMO")
        print("="*70)
        
        # Setup driver
        print("\n[1/6] Setting up WebDriver...")
        driver = setup_driver()
        print("   [OK] WebDriver initialized")
        
        # Create context and handler
        print("\n[2/6] Initializing Radio Handler...")
        element_context = ElementContext()
        radio_handler = RadioHandler(driver, context=element_context)
        print("   [OK] Radio Handler ready")
        
        # Navigate to Ant Design Radio demo page
        print("\n[3/6] Navigating to Ant Design Radio demo page...")
        radio_page_url = "https://ant.design/components/radio"
        driver.get(radio_page_url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-radio, .ant-radio-wrapper, input[type="radio"]')))
        print(f"   [OK] Page loaded: {radio_page_url}")
        time.sleep(2)  # Allow React components to fully render
        
        # Scroll to load all content
        print("\n[4/6] Scrolling to load all radio components...")
        for scroll_position in [500, 1000, 1500, 2000, 2500, 3000]:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Find all radios
        print("\n[5/6] Finding all radios on the page...")
        print("   [STEP] Scanning page for Ant Design radio components...")
        print("   [INFO] Using locator-less detection (Ant Design classes, ARIA attributes)...")
        radios = radio_handler.locator.find_all_radios(timeout=5)
        total_radios_found = len(radios)
        print(f"   [RESULT] Found {total_radios_found} radio(s) on the page")
        
        if total_radios_found == 0:
            print("   [WARN] No radios found on the page")
            return True
        
        # Track initial statistics
        initial_disabled_count = 0
        initial_selected_count = 0
        
        # Show initial summary and track initial statistics
        print("\n   [ANALYSIS] Analyzing initial radio states...")
        print("   " + "-"*65)
        print("   Initial Radio States (showing first 15):")
        for idx, radio in enumerate(radios[:15], 1):  # Show first 15
            try:
                print(f"      [ANALYZE] Radio {idx}/{min(15, len(radios))}: Identifying properties...")
                radio_info = radio_handler.identifier.identify_radio_type(radio)
                state = "SELECTED" if radio_info['selected'] else "UNSELECTED"
                disabled = " (DISABLED)" if radio_info['disabled'] else ""
                label = radio_info.get('label_text', 'N/A')[:30]
                group = radio_info.get('group_name', '')
                if group:
                    print(f"      [RESULT] Radio {idx}: '{label}' - {state}{disabled} [Group: {group}]")
                else:
                    print(f"      [RESULT] Radio {idx}: '{label}' - {state}{disabled}")
            except Exception as e:
                print(f"      [ERROR] Radio {idx}: Failed to analyze - {str(e)[:30]}")
        
        # Count initial statistics for all radios
        print("\n   [ANALYSIS] Counting initial statistics for all radios...")
        for radio in radios:
            try:
                radio_info = radio_handler.identifier.identify_radio_type(radio)
                if radio_info['disabled']:
                    initial_disabled_count += 1
                if radio_info['selected']:
                    initial_selected_count += 1
            except:
                pass
        
        # Print full summary
        print("\n" + "="*70)
        print("RADIO SUMMARY")
        print("="*70)
        radio_handler.print_radios_summary()
        
        # Test selecting radios - work directly with found radios
        print("\n" + "="*70)
        print("SELECTING RADIOS - DEMO")
        print("="*70)
        
        selected_count = 0
        failed_count = 0
        
        # Process radios directly (more reliable than using summary)
        print("\n   [STEP] Processing Radios Directly...")
        print("   [INFO] Analyzing radio elements and grouping them...")
        
        # Group radios by name attribute
        radios_by_group = {}
        individual_radios = []
        
        print(f"   [INFO] Analyzing {min(20, len(radios))} radios for grouping...")
        for idx, radio in enumerate(radios[:20], 1):  # Process first 20 radios
            try:
                print(f"      [ANALYZE] Radio {idx}/{min(20, len(radios))}: Identifying radio type...")
                radio_info = radio_handler.identifier.identify_radio_type(radio)
                group_name = radio_info.get('group_name')
                label = radio_info.get('label_text', 'Unknown')
                
                if group_name:
                    if group_name not in radios_by_group:
                        radios_by_group[group_name] = []
                        print(f"      [GROUP] Found new group: {group_name}")
                    radios_by_group[group_name].append((radio, radio_info, label))
                    print(f"      [GROUP] Added '{label}' to group '{group_name}'")
                else:
                    individual_radios.append((radio, radio_info, label))
                    print(f"      [INDIVIDUAL] Found individual radio: '{label}'")
            except Exception as e:
                print(f"      [ERROR] Failed to analyze radio {idx}: {str(e)[:50]}")
        
        print(f"   [RESULT] Found {len(radios_by_group)} radio groups and {len(individual_radios)} individual radios")
        
        # Select from groups (one per group)
        if radios_by_group:
            print("\n   " + "="*65)
            print("   [SECTION] Processing Radio Groups")
            print("   " + "="*65)
            for group_idx, (group_name, group_radios) in enumerate(list(radios_by_group.items())[:5], 1):  # First 5 groups
                print(f"\n   [GROUP {group_idx}] Group: {group_name} ({len(group_radios)} options)")
                print(f"      [INFO] Attempting to select one radio from this group...")
                
                for radio_idx, (radio, radio_info, label) in enumerate(group_radios[:3], 1):  # Try first 3 in group
                    try:
                        print(f"      [CHECK] Radio {radio_idx}: '{label}'")
                        print(f"         [STATUS] Disabled: {radio_info['disabled']}, Selected: {radio_info['selected']}")
                        
                        if not radio_info['disabled'] and not radio_info['selected']:
                            print(f"      [ACTION] → Attempting to select: '{label}'")
                            print(f"         [STEP 1] Locating clickable radio element...")
                            # Use direct element selection for better reliability
                            success = radio_handler._select_radio_element(radio, retry_count=3, retry_delay=0.5)
                            if success:
                                selected_count += 1
                                print(f"         [SUCCESS] ✓ Radio '{label}' selected successfully!")
                                print(f"         [WAIT] Waiting for UI to update...")
                                time.sleep(0.8)  # Wait for UI update
                                print(f"      [COMPLETE] Group '{group_name}' - Selection complete")
                                break  # Only select one per group
                            else:
                                failed_count += 1
                                print(f"         [FAILED] ✗ Failed to select radio '{label}'")
                        else:
                            if radio_info['disabled']:
                                print(f"         [SKIP] Radio is disabled, skipping...")
                            elif radio_info['selected']:
                                print(f"         [SKIP] Radio is already selected, skipping...")
                    except Exception as e:
                        print(f"         [ERROR] ✗ Error selecting radio: {str(e)[:50]}")
        
        # Select individual radios
        if individual_radios:
            print("\n   " + "="*65)
            print("   [SECTION] Processing Individual Radios (Not in Groups)")
            print("   " + "="*65)
            for radio_idx, (radio, radio_info, label) in enumerate(individual_radios[:5], 1):  # First 5 individual
                try:
                    print(f"\n   [INDIVIDUAL RADIO {radio_idx}] '{label}'")
                    print(f"      [CHECK] Status check...")
                    print(f"         [STATUS] Disabled: {radio_info['disabled']}, Selected: {radio_info['selected']}")
                    
                    if not radio_info['disabled'] and not radio_info['selected']:
                        print(f"      [ACTION] → Attempting to select individual radio: '{label}'")
                        print(f"         [STEP 1] Locating clickable radio element...")
                        success = radio_handler._select_radio_element(radio, retry_count=3, retry_delay=0.5)
                        if success:
                            selected_count += 1
                            print(f"         [SUCCESS] ✓ Individual radio '{label}' selected successfully!")
                            print(f"         [WAIT] Waiting for UI to update...")
                            time.sleep(0.8)
                        else:
                            failed_count += 1
                            print(f"         [FAILED] ✗ Failed to select individual radio '{label}'")
                    else:
                        if radio_info['disabled']:
                            print(f"      [SKIP] Radio is disabled, skipping...")
                        elif radio_info['selected']:
                            print(f"      [SKIP] Radio is already selected, skipping...")
                except Exception as e:
                    print(f"      [ERROR] ✗ Error: {str(e)[:50]}")
        
        print("\n   " + "="*65)
        print(f"   [SUMMARY] Selection Summary")
        print("   " + "="*65)
        print(f"      ✓ Successfully selected: {selected_count} radio(s)")
        print(f"      ✗ Failed to select: {failed_count} radio(s)")
        print(f"      [SUCCESS RATE] {int((selected_count / (selected_count + failed_count)) * 100) if (selected_count + failed_count) > 0 else 0}%")
        
        # Final summary
        print("\n" + "="*70)
        print("FINAL RADIO SUMMARY")
        print("="*70)
        final_summary = radio_handler.get_all_radios_summary(timeout=2)
        print(f"   Total radios: {final_summary['total_count']}")
        print(f"   Total groups: {final_summary['total_groups']}")
        print(f"   Selected: {final_summary['selected_count']}")
        print(f"   Disabled: {final_summary['disabled_count']}")
        
        if final_summary['groups']:
            print("\n   Group Details:")
            for group_name, group_info in list(final_summary['groups'].items())[:5]:
                print(f"      {group_name}:")
                print(f"         Options: {group_info.get('total_options', 0)}")
                if group_info.get('selected_option'):
                    print(f"         Selected: {group_info['selected_option']}")
                else:
                    print(f"         Selected: None")
        
        # Get final statistics
        print("\n" + "="*70)
        print("GENERATING FINAL STATISTICS...")
        print("="*70)
        final_summary = radio_handler.get_all_radios_summary(timeout=2)
        final_selected_count = final_summary['selected_count']
        final_disabled_count = final_summary['disabled_count']
        
        # Generate comprehensive summary for manager
        print("\n" + "="*70)
        print("EXECUTION SUMMARY REPORT")
        print("="*70)
        print("\n📊 RADIO COMPONENT STATISTICS")
        print("-" * 70)
        print(f"  Total Radio Components Found:     {total_radios_found}")
        print(f"  Total Radios Clicked:             {selected_count}")
        print(f"  Total Radios Disabled:            {final_disabled_count}")
        print(f"  Total Radios Selected (Final):    {final_selected_count}")
        print("-" * 70)
        print("\n📈 ADDITIONAL METRICS")
        print("-" * 70)
        print(f"  Initial Selected Count:           {initial_selected_count}")
        print(f"  Initial Disabled Count:           {initial_disabled_count}")
        print(f"  Newly Selected:                   {selected_count}")
        print(f"  Selection Success Rate:           {int((selected_count / (selected_count + failed_count)) * 100) if (selected_count + failed_count) > 0 else 0}%")
        print(f"  Total Radio Groups:               {final_summary['total_groups']}")
        print("-" * 70)
        print("\n" + "="*70)
        print("[SUCCESS] RADIO AUTOMATION COMPLETED SUCCESSFULLY")
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


def run_radio_automation_custom_url(url: str):
    """Run radio automation on a custom URL"""
    driver = None
    try:
        print("="*70)
        print(f"ANT DESIGN RADIO AUTOMATION - CUSTOM URL")
        print("="*70)
        print(f"URL: {url}")
        
        # Setup driver
        print("\n[1/4] Setting up WebDriver...")
        driver = setup_driver()
        print("   [OK] WebDriver initialized")
        
        # Create context and handler
        print("\n[2/4] Initializing Radio Handler...")
        element_context = ElementContext()
        radio_handler = RadioHandler(driver, context=element_context)
        print("   [OK] Radio Handler ready")
        
        # Navigate to custom URL
        print(f"\n[3/4] Navigating to: {url}...")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-radio, .ant-radio-wrapper, input[type="radio"]')))
            print("   [OK] Page loaded with radios detected")
        except:
            print("   [WARN] No radios detected immediately, continuing...")
        
        time.sleep(2)
        
        # Scroll to load content
        for scroll_position in [500, 1000, 1500]:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Find and analyze radios
        print("\n[4/4] Finding and analyzing radios...")
        radios = radio_handler.locator.find_all_radios(timeout=5)
        total_radios_found = len(radios)
        print(f"   ✓ Found {total_radios_found} radio(s)")
        
        # Track statistics
        initial_disabled_count = 0
        initial_selected_count = 0
        clicked_count = 0
        failed_count = 0
        
        if radios:
            # Count initial statistics
            print("\n   Analyzing initial radio states...")
            for radio in radios:
                try:
                    radio_info = radio_handler.identifier.identify_radio_type(radio)
                    if radio_info['disabled']:
                        initial_disabled_count += 1
                    if radio_info['selected']:
                        initial_selected_count += 1
                except:
                    pass
            
            # Print summary
            radio_handler.print_radios_summary()
            
            # Try to select first few radios
            print("\n   Attempting to select radios...")
            for idx, radio in enumerate(radios[:5], 1):
                try:
                    radio_info = radio_handler.identifier.identify_radio_type(radio)
                    if not radio_info['disabled'] and not radio_info['selected']:
                        label = radio_info.get('label_text', f'Radio {idx}')
                        print(f"      → Selecting: {label}")
                        success = radio_handler.select_radio(
                            label,
                            identifier_type='auto',
                            retry_count=2,
                            retry_delay=0.3
                        )
                        if success:
                            clicked_count += 1
                            print(f"         ✓ Selected")
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
        final_summary = radio_handler.get_all_radios_summary(timeout=2)
        final_selected_count = final_summary['selected_count']
        final_disabled_count = final_summary['disabled_count']
        
        # Generate comprehensive summary for manager
        print("\n" + "="*70)
        print("EXECUTION SUMMARY REPORT")
        print("="*70)
        print("\n📊 RADIO COMPONENT STATISTICS")
        print("-" * 70)
        print(f"  Total Radio Components Found:     {total_radios_found}")
        print(f"  Total Radios Clicked:             {clicked_count}")
        print(f"  Total Radios Disabled:            {final_disabled_count}")
        print(f"  Total Radios Selected (Final):    {final_selected_count}")
        print("-" * 70)
        print("\n📈 ADDITIONAL METRICS")
        print("-" * 70)
        print(f"  Initial Selected Count:           {initial_selected_count}")
        print(f"  Initial Disabled Count:           {initial_disabled_count}")
        print(f"  Newly Selected:                   {clicked_count}")
        print(f"  Selection Success Rate:           {int((clicked_count / (clicked_count + failed_count)) * 100) if (clicked_count + failed_count) > 0 else 0}%")
        print(f"  Total Radio Groups:               {final_summary['total_groups']}")
        print("-" * 70)
        print("\n" + "="*70)
        print("[SUCCESS] RADIO AUTOMATION COMPLETED")
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
    print("ANT DESIGN RADIO AUTOMATION RUNNER")
    print("="*70)
    print("\nOptions:")
    print("  1. Run demo on Ant Design Radio documentation page (default)")
    print("  2. Run on custom URL")
    print("\nUsage:")
    print("  python run_radio_automation.py              # Demo mode")
    print("  python run_radio_automation.py <URL>         # Custom URL")
    print("="*70 + "\n")
    
    if len(sys.argv) > 1:
        # Custom URL provided
        custom_url = sys.argv[1]
        if not custom_url.startswith('http'):
            print("[WARN] Warning: URL should start with http:// or https://")
            print(f"  Attempting to use: https://{custom_url}")
            custom_url = f"https://{custom_url}"
        run_radio_automation_custom_url(custom_url)
    else:
        # Run demo
        run_radio_automation_demo()

