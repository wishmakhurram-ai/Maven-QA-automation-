"""
Example script demonstrating Ant Design Menu automation
This script shows how to use the menu framework to interact with ALL menus on the page
"""
from framework.utils.driver_setup import DriverSetup
from framework.components.menu_handler import MenuHandler
from framework.context.element_context import ElementContext
from selenium.webdriver.common.by import By
import time


def navigate_sidebar_menu_systematically(menu_handler, sidebar_menu):
    """
    Navigate through the sidebar menu systematically, clicking all items in order
    Only processes sidebar menu items, not top navbar
    
    Args:
        menu_handler: MenuHandler instance
        sidebar_menu: Sidebar menu WebElement
    """
    print(f"\n{'='*70}")
    print("SIDEBAR MENU SYSTEMATIC NAVIGATION")
    print(f"{'='*70}")
    
    # Scroll sidebar into view
    try:
        menu_handler.execute_js("arguments[0].scrollIntoView({block: 'start'});", sidebar_menu)
        time.sleep(1)
    except:
        pass
    
    # Get all top-level menu items directly from sidebar (not submenu items)
    # Note: When searching within an element, don't use leading '>' combinator
    try:
        all_items = sidebar_menu.find_elements(By.CSS_SELECTOR, 
            'ul > li > .ant-menu-item, ul > li > .ant-menu-submenu-title')
    except Exception as e:
        # Fallback: try simpler selector
        print(f"  Warning: Primary selector failed, trying fallback: {str(e)}")
        try:
    all_items = sidebar_menu.find_elements(By.CSS_SELECTOR, 
                '.ant-menu-item, .ant-menu-submenu-title')
        except Exception as e2:
            # Last resort: find all li elements and filter
            print(f"  Warning: Fallback selector failed, using XPath: {str(e2)}")
            all_items = sidebar_menu.find_elements(By.XPATH, 
                './/li[.//span[contains(@class, "ant-menu-title-content")] or .//span[contains(@class, "ant-menu-item-icon")]]')
    
    print(f"Found {len(all_items)} top-level items in sidebar menu")
    
    clicked_items = []
    expanded_submenus = []
    
    # Process each top-level item sequentially
    for item_idx, item in enumerate(all_items, 1):
        try:
            item_info = menu_handler.identifier.identify_menu_item(item)
            item_text = item_info.get('text', '').strip()
            item_type = item_info.get('type')
            is_disabled = item_info.get('disabled', False)
            has_children = item_info.get('has_children', False)
            is_expanded = item_info.get('expanded', False)
            
            # Skip empty or disabled items
            if not item_text or is_disabled:
                continue
            
            print(f"\n[{item_idx}] Processing: '{item_text}'")
            
            # Scroll item into view
            try:
                menu_handler.execute_js("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", item)
                time.sleep(0.5)
            except:
                pass
            
            # Handle submenu titles (like "Ant Design", "Global Styles", etc.)
            if item_type == 'submenu-title' or has_children:
                print(f"  📁 Submenu: '{item_text}'")
                
                # Expand if not already expanded
                if not is_expanded:
                    try:
                        item.click()
                        time.sleep(1.5)  # Wait for submenu to expand
                        expanded_submenus.append(item_text)
                        print(f"    ✓ Expanded '{item_text}'")
                    except:
                        try:
                            menu_handler.execute_js("arguments[0].click();", item)
                            time.sleep(1.5)
                            expanded_submenus.append(item_text)
                            print(f"    ✓ Expanded '{item_text}' (via JS)")
                        except Exception as e:
                            print(f"    ✗ Failed to expand '{item_text}': {str(e)}")
                            continue
                else:
                    print(f"    → Already expanded")
                
                # Now click ALL items within this submenu sequentially
                try:
                    # Find the submenu container (parent <li>)
                    submenu_container = item.find_element(By.XPATH, 
                        './ancestor::li[contains(@class, "ant-menu-submenu")]')
                    
                    # Wait for submenu to render
                    time.sleep(1.0)
                    
                    # Get submenu items (direct children only)
                    try:
                    submenu_items = submenu_container.find_elements(By.CSS_SELECTOR, 
                        'ul.ant-menu-sub > li > .ant-menu-item, ul.ant-menu-sub > li > .ant-menu-submenu-title')
                    except:
                        # Try alternative selector
                        try:
                        submenu_items = submenu_container.find_elements(By.CSS_SELECTOR, 
                            '.ant-menu-submenu .ant-menu-item, .ant-menu-submenu .ant-menu-submenu-title')
                        except:
                            # Last resort: use XPath
                            submenu_items = submenu_container.find_elements(By.XPATH, 
                                './/ul[contains(@class, "ant-menu-sub")]//li//span[contains(@class, "ant-menu-title-content")]/ancestor::*[contains(@class, "ant-menu-item") or contains(@class, "ant-menu-submenu-title")]')
                    
                    print(f"    Found {len(submenu_items)} items in '{item_text}' submenu")
                    
                    # Click each item in the submenu sequentially
                    for sub_idx, sub_item in enumerate(submenu_items, 1):
                        try:
                            sub_item_info = menu_handler.identifier.identify_menu_item(sub_item)
                            sub_item_text = sub_item_info.get('text', '').strip()
                            sub_item_type = sub_item_info.get('type')
                            sub_is_disabled = sub_item_info.get('disabled', False)
                            sub_has_children = sub_item_info.get('has_children', False)
                            
                            if not sub_item_text or sub_is_disabled:
                                continue
                            
                            # Scroll into view
                            try:
                                menu_handler.execute_js("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", sub_item)
                                time.sleep(0.3)
                            except:
                                pass
                            
                            # If it's another nested submenu, expand and click items inside
                            if sub_item_type == 'submenu-title' or sub_has_children:
                                print(f"      [{sub_idx}] 📁 Nested Submenu: '{sub_item_text}'")
                                
                                sub_is_expanded = sub_item_info.get('expanded', False)
                                if not sub_is_expanded:
                                    try:
                                        sub_item.click()
                                        time.sleep(1.0)
                                        print(f"        ✓ Expanded '{sub_item_text}'")
                                    except:
                                        menu_handler.execute_js("arguments[0].click();", sub_item)
                                        time.sleep(1.0)
                                        print(f"        ✓ Expanded '{sub_item_text}' (via JS)")
                                
                                # Click nested items
                                try:
                                    nested_container = sub_item.find_element(By.XPATH, 
                                        './ancestor::li[contains(@class, "ant-menu-submenu")]')
                                    try:
                                    nested_items = nested_container.find_elements(By.CSS_SELECTOR, 
                                        'ul.ant-menu-sub > li > .ant-menu-item')
                                    except:
                                        # Fallback to XPath
                                        nested_items = nested_container.find_elements(By.XPATH, 
                                            './/ul[contains(@class, "ant-menu-sub")]//li//span[contains(@class, "ant-menu-title-content")]/ancestor::*[contains(@class, "ant-menu-item")]')
                                    
                                    for nested_item in nested_items:
                                        try:
                                            nested_text = nested_item.text.strip()
                                            if nested_text:
                                                menu_handler.execute_js("arguments[0].scrollIntoView({block: 'center'});", nested_item)
                                                time.sleep(0.3)
                                                nested_item.click()
                                                time.sleep(0.8)
                                                clicked_items.append(f"{item_text} > {sub_item_text} > {nested_text}")
                                                print(f"          ✓ Clicked '{nested_text}'")
                                        except:
                                            continue
                                except:
                                    pass
                            else:
                                # Regular menu item - click it sequentially
                                print(f"      [{sub_idx}] 📄 Clicking: '{sub_item_text}'")
                                try:
                                    sub_item.click()
                                    time.sleep(0.8)  # Wait after each click
                                    clicked_items.append(f"{item_text} > {sub_item_text}")
                                    print(f"        ✓ Clicked '{sub_item_text}'")
                                except:
                                    menu_handler.execute_js("arguments[0].click();", sub_item)
                                    time.sleep(0.8)
                                    clicked_items.append(f"{item_text} > {sub_item_text}")
                                    print(f"        ✓ Clicked '{sub_item_text}' (via JS)")
                        except Exception as e:
                            continue
                except Exception as e:
                    print(f"    ✗ Error processing submenu items: {str(e)}")
            
            # Handle regular top-level menu items (no submenu)
            elif item_type == 'menu-item':
                print(f"  📄 Clicking: '{item_text}'")
                try:
                    item.click()
                    time.sleep(0.8)
                    clicked_items.append(item_text)
                    print(f"    ✓ Clicked '{item_text}'")
                except:
                    menu_handler.execute_js("arguments[0].click();", item)
                    time.sleep(0.8)
                    clicked_items.append(item_text)
                    print(f"    ✓ Clicked '{item_text}' (via JS)")
        
        except Exception as e:
            print(f"  ✗ Error processing item: {str(e)}")
            continue
    
    # Summary
    print(f"\n{'='*70}")
    print("NAVIGATION SUMMARY")
    print(f"{'='*70}")
    print(f"✓ Expanded {len(expanded_submenus)} submenu(s)")
    print(f"✓ Clicked {len(clicked_items)} item(s)")
    if expanded_submenus:
        print(f"\nExpanded submenus: {', '.join(expanded_submenus[:10])}")
    if clicked_items:
        print(f"\nClicked items (first 10):")
        for item in clicked_items[:10]:
            print(f"  - {item}")
        if len(clicked_items) > 10:
            print(f"  ... and {len(clicked_items) - 10} more")
    print(f"{'='*70}\n")


def main():
    """Main function to demonstrate menu automation for ALL menus on the page"""
    # Setup driver
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    
    try:
        # Create context and handler
        context = ElementContext()
        menu_handler = MenuHandler(driver, context=context)
        
        # Navigate to Ant Design menu page
        print("\n" + "="*70)
        print("ANT DESIGN MENU AUTOMATION - FULL PAGE DEMO")
        print("="*70)
        print("\nNavigating to Ant Design Menu documentation page...")
        driver.get("https://ant.design/components/menu")
        
        # Wait for page to fully load
        print("Waiting for page to load...")
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(3)  # Additional wait for dynamic content
        
        # Scroll down to load all content (including example menus)
        print("Scrolling page to load all content...")
        for scroll_pos in [500, 1000, 1500, 2000, 2500, 3000, 3500]:
            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(0.5)
        
        # Scroll back to top to see sidebar
        print("Scrolling back to top...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Find the sidebar menu specifically (left navigation) - EXCLUDE top navbar
        print("\n" + "="*70)
        print("FINDING SIDEBAR MENU (EXCLUDING TOP NAVBAR)")
        print("="*70)
        
        sidebar_menu = None
        
        # Strategy 1: Find all menus and filter out navbar (navbar is usually horizontal and at top)
        all_menus = menu_handler.locator.find_all_menus(timeout=15)
        print(f"Found {len(all_menus)} menu(s) on the page")
        
        for menu in all_menus:
            try:
                menu_type = menu_handler.identifier.identify_menu_type(menu)
                location = menu.location
                size = menu.size
                
                # Exclude horizontal menus (these are usually navbars at the top)
                if menu_type == 'horizontal':
                    print(f"  Skipping horizontal menu at y={location['y']} (likely navbar)")
                    continue
                
                # Sidebar is usually vertical/inline and on the left side
                if menu_type in ['vertical', 'inline', 'default']:
                    # Check if it's on the left side (x < 400) and below the header (y > 100)
                    if location['x'] < 400 and location['y'] > 100 and size['height'] > 200:
                        sidebar_menu = menu
                        print(f"✓ Found sidebar menu (type: {menu_type}, x={location['x']}, y={location['y']}, height={size['height']})")
                        break
            except:
                continue
        
        if not sidebar_menu:
            print("✗ Could not find sidebar menu!")
            return
        
        # Print sidebar menu info
        menu_type = menu_handler.identifier.identify_menu_type(sidebar_menu)
        is_collapsed = menu_handler.identifier.is_menu_collapsed(sidebar_menu)
        items = menu_handler.locator.find_all_menu_items(sidebar_menu, include_submenus=True)
        print(f"\nSidebar Menu Info:")
        print(f"  Type: {menu_type}")
        print(f"  Collapsed: {is_collapsed}")
        print(f"  Total items: {len(items)}")
        
        # Navigate through sidebar menu systematically
        if sidebar_menu:
            print("\n" + "="*70)
            print("SIDEBAR MENU NAVIGATION")
            print("="*70)
            print("This will navigate through the entire sidebar menu structure:")
            print("  - Components Overview")
            print("  - General > Button, FloatButton, Icon, Typography")
            print("  - Layout > Divider, Flex, Grid, etc.")
            print("  - Navigation > Anchor, Breadcrumb, Dropdown, Menu, etc.")
            print("  - Data Entry > AutoComplete, Cascader, Checkbox, etc.")
            print("  - Data Display > Avatar, Badge, Calendar, etc.")
            print("  - Feedback > Alert, Drawer, Message, etc.")
            print("  - Other > Affix, App, ConfigProvider, etc.")
            print("="*70)
            
            navigate_sidebar_menu_systematically(menu_handler, sidebar_menu)
        else:
            print("⚠ Could not find sidebar menu, but will continue with example menus")
        
        # Also interact with example menus on the page (if any)
        print("\n" + "="*70)
        print("FINDING AND INTERACTING WITH EXAMPLE MENUS")
        print("="*70)
        
        all_menus = menu_handler.locator.find_all_menus(timeout=15)
        example_menus = [m for m in all_menus if m != sidebar_menu]
        
        if example_menus:
            print(f"Found {len(example_menus)} example menu(s) on the page")
            
            for idx, menu in enumerate(example_menus[:5], 1):  # Limit to first 5 example menus
                try:
                    menu_type = menu_handler.identifier.identify_menu_type(menu)
                    items = menu_handler.locator.find_all_menu_items(menu, include_submenus=True)
                    
                    print(f"\nExample Menu {idx}: {menu_type} - {len(items)} items")
                    
                    # Scroll to menu
                    menu_handler.execute_js("arguments[0].scrollIntoView({block: 'center'});", menu)
                    time.sleep(0.5)
                    
                    # Click a few items
                    for item in items[:3]:
                        try:
                            item_info = menu_handler.identifier.identify_menu_item(item)
                            item_text = item_info.get('text', '').strip()
                            
                            if item_text and not item_info.get('disabled'):
                                menu_handler.execute_js("arguments[0].scrollIntoView({block: 'center'});", item)
                                time.sleep(0.2)
                                item.click()
                                time.sleep(0.5)
                                print(f"  ✓ Clicked '{item_text}'")
                        except:
                            continue
                except Exception as e:
                    print(f"  ✗ Error with example menu {idx}: {str(e)}")
                    continue
        
        # Final summary
        print("\n" + "="*70)
        print("AUTOMATION COMPLETE")
        print("="*70)
        print(f"✓ Navigated through sidebar menu systematically")
        print(f"✓ Interacted with example menus on the page")
        print("="*70)
        
        # Keep browser open to see results
        print("\nKeeping browser open for 10 seconds to view results...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close browser
        print("\nClosing browser...")
        driver.quit()


if __name__ == "__main__":
    main()

