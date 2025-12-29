"""
Simplified test script that finds and tests the actual interactive Ant Design table examples
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from framework.components.table_handler import TableHandler
from framework.context.element_context import ElementContext
import time

def main():
    """Test table framework against Ant Design table documentation"""
    print("="*80)
    print("ANT DESIGN TABLE FRAMEWORK TEST - SIMPLIFIED")
    print("="*80)
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    
    try:
        # Navigate to Ant Design table documentation
        url = "https://ant.design/components/table"
        print(f"\n>> Navigating to: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Scroll down multiple times to load all example tables
        print("   >> Scrolling to find example tables...")
        for scroll in [500, 1000, 1500, 2000, 2500]:
            driver.execute_script(f"window.scrollTo(0, {scroll});")
            time.sleep(1)
        
        time.sleep(2)
        
        # Create table handler
        element_context = ElementContext()
        table_handler = TableHandler(driver, context=element_context)
        
        # Find all tables
        print("\n" + "="*80)
        print("STEP 1: Finding all tables")
        print("="*80)
        all_tables = table_handler.locator.find_all_tables(timeout=10, context=element_context)
        print(f"   >> Found {len(all_tables)} top-level table(s)")
        
        if not all_tables:
            print("   >> ERROR: No tables found!")
            return
        
        # Find the best interactive table
        print("\n" + "="*80)
        print("STEP 2: Finding best interactive table")
        print("="*80)
        
        best_table = None
        best_info = None
        best_score = -1
        
        for i, table in enumerate(all_tables):
            try:
                # Check this table
                element_context.clear()
                table_handler.locator._store_element_in_context(table, "check", element_context)
                element_context.set_current("check")
                
                summary = table_handler.get_table_summary()
                headers = summary.get('headers', [])
                title = summary.get('title', 'No Title')
                row_count = summary.get('row_count', {}).get('visible', 0)
                sortable = summary.get('sortable_columns', [])
                has_pagination = summary.get('has_pagination', False)
                has_selection = summary.get('has_row_selection', {}).get('checkbox', False) or summary.get('has_row_selection', {}).get('radio', False)
                
                # Score this table
                score = 0
                if row_count > 0:
                    score += 5
                if row_count >= 3 and row_count <= 50:
                    score += 10
                if sortable:
                    score += 15
                    print(f"   >> Table {i}: '{title}' - {len(headers)} cols, {row_count} rows, {len(sortable)} sortable - SCORE: {score}")
                if has_pagination:
                    score += 10
                if has_selection:
                    score += 5
                if 'Age' in headers or 'Name' in headers or 'Full Name' in headers:
                    score += 10
                if 'Action' in headers or 'Actions' in headers:
                    score += 5
                
                if score > best_score:
                    best_score = score
                    best_table = table
                    best_info = {
                        'index': i,
                        'title': title,
                        'headers': headers,
                        'row_count': row_count,
                        'sortable': sortable,
                        'has_pagination': has_pagination,
                        'has_selection': has_selection,
                        'summary': summary
                    }
            except Exception as e:
                print(f"   >> Error checking table {i}: {str(e)}")
                continue
        
        if not best_table:
            print("   >> ERROR: Could not find suitable table!")
            return
        
        print(f"\n   >> ✓ BEST TABLE FOUND: Index {best_info['index']}")
        print(f"      Title: '{best_info['title']}'")
        print(f"      Headers: {', '.join(best_info['headers'][:5])}")
        print(f"      Rows: {best_info['row_count']}")
        print(f"      Sortable columns: {best_info['sortable']}")
        print(f"      Has pagination: {best_info['has_pagination']}")
        print(f"      Has selection: {best_info['has_selection']}")
        print(f"      Score: {best_score}")
        
        # Store best table
        element_context.clear()
        table_handler.locator._store_element_in_context(best_table, "selected", element_context)
        element_context.set_current("selected")
        
        # Scroll table into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", best_table)
        time.sleep(2)
        
        # Print full summary
        print("\n" + "="*80)
        print("STEP 3: Table Summary")
        print("="*80)
        table_handler.print_table_summary()
        
        # Test reading rows
        print("\n" + "="*80)
        print("STEP 4: Reading table data")
        print("="*80)
        rows = table_handler.read_all_rows()
        print(f"   >> Read {len(rows)} rows")
        if rows:
            print(f"   >> First 3 rows:")
            for i, row in enumerate(rows[:3]):
                print(f"      Row {i}: {row}")
        
        # Test sorting
        print("\n" + "="*80)
        print("STEP 5: Testing sorting")
        print("="*80)
        if best_info['sortable']:
            col = best_info['sortable'][0]
            print(f"   >> Attempting to sort by '{col}'...")
            success = table_handler.sort_by_column(col, 'asc')
            if success:
                print(f"   >> ✓ Successfully sorted by '{col}'")
                time.sleep(2)
                # Read rows after sort
                new_rows = table_handler.read_all_rows()
                print(f"   >> After sort: {len(new_rows)} rows")
                if new_rows:
                    print(f"   >> First row after sort: {new_rows[0]}")
            else:
                print(f"   >> ✗ Failed to sort by '{col}'")
        else:
            # Try to sort any column
            headers = best_info['headers']
            for col in headers:
                if col and col not in ['Action', 'Actions', 'Operations']:
                    print(f"   >> Attempting to sort by '{col}'...")
                    success = table_handler.sort_by_column(col, 'asc')
                    if success:
                        print(f"   >> ✓ Successfully sorted by '{col}'")
                        time.sleep(2)
                        break
                    else:
                        print(f"   >> ✗ Could not sort by '{col}'")
        
        # Test clicking buttons
        print("\n" + "="*80)
        print("STEP 6: Testing button clicks")
        print("="*80)
        headers = best_info['headers']
        action_col = None
        for col in ['Action', 'Actions', 'Operations']:
            if col in headers:
                action_col = col
                break
        
        if action_col and rows:
            print(f"   >> Found '{action_col}' column, clicking button in row 0...")
            success = table_handler.click_cell_button(action_col, row_index=0)
            if success:
                print(f"   >> ✓ Successfully clicked button")
                time.sleep(1)
            else:
                # Try with specific button text
                for btn_text in ['Delete', 'Edit', 'View', 'Invite']:
                    success = table_handler.click_cell_button(action_col, row_index=0, button_text=btn_text)
                    if success:
                        print(f"   >> ✓ Successfully clicked '{btn_text}' button")
                        time.sleep(1)
                        break
                if not success:
                    print(f"   >> ✗ Could not click button")
        else:
            print("   >> No Action column found")
        
        # Test pagination
        if best_info['has_pagination']:
            print("\n" + "="*80)
            print("STEP 7: Testing pagination")
            print("="*80)
            print("   >> Attempting to go to next page...")
            success = table_handler.go_to_next_page()
            if success:
                print("   >> ✓ Successfully navigated to next page")
                time.sleep(2)
                new_rows = table_handler.read_all_rows()
                print(f"   >> New page has {len(new_rows)} rows")
            else:
                print("   >> ✗ Could not navigate (may be on last page)")
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED!")
        print("="*80)
        print("\n>> Keeping browser open for 10 seconds to see results...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n>> ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n>> Closing browser...")
        driver.quit()
        print(">> Test completed!")


if __name__ == "__main__":
    main()

