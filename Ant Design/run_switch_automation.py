"""
Standalone Python script to run Ant Design Switch automation
Run with: python run_switch_automation.py
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
from framework.components.switch_handler import SwitchHandler
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


def run_switch_automation_demo():
    """Run switch automation demonstration"""
    driver = None
    try:
        print("="*70)
        print("ANT DESIGN SWITCH AUTOMATION - DEMO")
        print("="*70)
        
        # Setup driver
        print("\n[1/5] Setting up WebDriver...")
        driver = setup_driver()
        print("   [OK] WebDriver initialized")
        
        # Create context and handler
        print("\n[2/5] Initializing Switch Handler...")
        element_context = ElementContext()
        switch_handler = SwitchHandler(driver, context=element_context)
        print("   [OK] Switch Handler ready")
        
        # Navigate to Ant Design Switch demo page
        print("\n[3/5] Navigating to Ant Design Switch demo page...")
        switch_page_url = "https://ant.design/components/switch"
        driver.get(switch_page_url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-switch, [role="switch"]')))
        print(f"   [OK] Page loaded: {switch_page_url}")
        time.sleep(2)  # Allow React components to fully render
        
        # Find all switches
        print("\n[4/5] Finding all switches on the page...")
        switches = switch_handler.locator.find_all_switches(timeout=3)
        print(f"   [OK] Found {len(switches)} switch(es)")
        
        if len(switches) == 0:
            print("   [WARN] No switches found on the page")
            return True
        
        # Show initial summary
        print("\n   Initial Switch States:")
        for idx, switch in enumerate(switches[:10], 1):  # Show first 10
            try:
                switch_info = switch_handler.identifier.identify_switch_type(switch)
                state = "ON" if switch_info['checked'] else "OFF"
                disabled = " (DISABLED)" if switch_info['disabled'] else ""
                loading = " (LOADING)" if switch_info['loading'] else ""
                print(f"      Switch {idx}: {state}{disabled}{loading}")
            except:
                print(f"      Switch {idx}: Unknown state")
        
        # TURN ALL SWITCHES ON using direct element toggle
        print("\n" + "="*70)
        print("TURNING ALL SWITCHES ON...")
        print("="*70)
        
        turned_on = 0
        already_on = 0
        skipped = 0
        failed = 0
        
        # Re-find switches to ensure fresh elements
        switches = switch_handler.locator.find_all_switches(timeout=3)
        
        for idx, switch in enumerate(switches, 1):
            try:
                switch_info = switch_handler.identifier.identify_switch_type(switch)
                
                # Skip disabled or loading switches
                if switch_info['disabled'] or switch_info['loading']:
                    skipped += 1
                    continue
                
                # If already ON, skip
                if switch_info['checked']:
                    already_on += 1
                    continue
                
                # Use direct element toggle (no re-finding needed)
                # Increased retry count and delay for Ant Design documentation page switches
                success = switch_handler.toggle_switch_element(switch, target_state=True, retry_count=3, retry_delay=0.5)
                
                if success:
                    turned_on += 1
                    if idx <= 10:  # Show first 10 successes
                        print(f"   [OK] Switch {idx}: Turned ON")
                else:
                    failed += 1
                    if idx <= 5:
                        print(f"   [ERROR] Switch {idx}: Failed to turn ON")
            except Exception as e:
                failed += 1
                if idx <= 5:
                    print(f"   [ERROR] Switch {idx}: Error - {str(e)[:50]}")
        
        print(f"\n   Summary: {turned_on} turned ON, {already_on} already ON, {skipped} skipped, {failed} failed")
        
        time.sleep(0.5)
        
        # TURN ALL SWITCHES OFF using direct element toggle
        print("\n" + "="*70)
        print("TURNING ALL SWITCHES OFF...")
        print("="*70)
        
        turned_off = 0
        already_off = 0
        skipped_off = 0
        failed_off = 0
        
        # Re-find switches to ensure fresh elements
        switches = switch_handler.locator.find_all_switches(timeout=3)
        
        for idx, switch in enumerate(switches, 1):
            try:
                switch_info = switch_handler.identifier.identify_switch_type(switch)
                
                # Skip disabled or loading switches
                if switch_info['disabled'] or switch_info['loading']:
                    skipped_off += 1
                    continue
                
                # If already OFF, skip
                if not switch_info['checked']:
                    already_off += 1
                    continue
                
                # Use direct element toggle (no re-finding needed)
                # Increased retry count and delay for Ant Design documentation page switches
                success = switch_handler.toggle_switch_element(switch, target_state=False, retry_count=3, retry_delay=0.5)
                
                if success:
                    turned_off += 1
                    if idx <= 10:  # Show first 10 successes
                        print(f"   [OK] Switch {idx}: Turned OFF")
                else:
                    failed_off += 1
                    if idx <= 5:
                        print(f"   [ERROR] Switch {idx}: Failed to turn OFF")
            except Exception as e:
                failed_off += 1
                if idx <= 5:
                    print(f"   [ERROR] Switch {idx}: Error - {str(e)[:50]}")
        
        print(f"\n   Summary: {turned_off} turned OFF, {already_off} already OFF, {skipped_off} skipped, {failed_off} failed")
        
        # Final summary
        print("\n" + "="*70)
        print("FINAL SWITCH SUMMARY")
        print("="*70)
        final_summary = switch_handler.get_all_switches_summary(timeout=2)
        print(f"   Total switches: {final_summary['total_count']}")
        print(f"   ON: {final_summary['on_count']}")
        print(f"   OFF: {final_summary['off_count']}")
        print(f"   Disabled: {final_summary['disabled_count']}")
        print(f"   Loading: {final_summary['loading_count']}")
        
        print("\n" + "="*70)
        print("[SUCCESS] SWITCH AUTOMATION COMPLETED SUCCESSFULLY")
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


def run_switch_automation_custom_url(url: str):
    """Run switch automation on a custom URL"""
    driver = None
    try:
        print("="*70)
        print(f"ANT DESIGN SWITCH AUTOMATION - CUSTOM URL")
        print("="*70)
        print(f"URL: {url}")
        
        # Setup driver
        print("\n[1/3] Setting up WebDriver...")
        driver = setup_driver()
        print("   [OK] WebDriver initialized")
        
        # Create context and handler
        print("\n[2/3] Initializing Switch Handler...")
        element_context = ElementContext()
        switch_handler = SwitchHandler(driver, context=element_context)
        print("   [OK] Switch Handler ready")
        
        # Navigate to custom URL
        print(f"\n[3/3] Navigating to: {url}...")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-switch, [role="switch"]')))
            print("   [OK] Page loaded with switches detected")
        except:
            print("   [WARN] No switches detected immediately, continuing...")
        
        time.sleep(1)
        
        # Find and toggle switches
        switches = switch_handler.locator.find_all_switches(timeout=3)
        print(f"\n   ✓ Found {len(switches)} switch(es)")
        
        # Turn all ON
        print("\n   Turning all switches ON...")
        for idx, switch in enumerate(switches, 1):
            try:
                switch_info = switch_handler.identifier.identify_switch_type(switch)
                if not switch_info['disabled'] and not switch_info['loading'] and not switch_info['checked']:
                    try:
                        checkbox = switch.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        driver.execute_script("arguments[0].click();", checkbox)
                    except:
                        driver.execute_script("arguments[0].click();", switch)
                    time.sleep(0.1)
            except:
                pass
        
        time.sleep(0.5)
        
        # Turn all OFF
        print("   Turning all switches OFF...")
        for idx, switch in enumerate(switches, 1):
            try:
                switch_info = switch_handler.identifier.identify_switch_type(switch)
                if not switch_info['disabled'] and not switch_info['loading'] and switch_info['checked']:
                    try:
                        checkbox = switch.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        driver.execute_script("arguments[0].click();", checkbox)
                    except:
                        driver.execute_script("arguments[0].click();", switch)
                    time.sleep(0.1)
            except:
                pass
        
        print("\n[SUCCESS] SWITCH AUTOMATION COMPLETED")
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
    print("ANT DESIGN SWITCH AUTOMATION RUNNER")
    print("="*70)
    print("\nOptions:")
    print("  1. Run demo on Ant Design Switch documentation page (default)")
    print("  2. Run on custom URL")
    print("\nUsage:")
    print("  python run_switch_automation.py              # Demo mode")
    print("  python run_switch_automation.py <URL>         # Custom URL")
    print("="*70 + "\n")
    
    if len(sys.argv) > 1:
        # Custom URL provided
        custom_url = sys.argv[1]
        if not custom_url.startswith('http'):
            print("[WARN] Warning: URL should start with http:// or https://")
            print(f"  Attempting to use: https://{custom_url}")
            custom_url = f"https://{custom_url}"
        run_switch_automation_custom_url(custom_url)
    else:
        # Run demo
        run_switch_automation_demo()
