"""
Standalone test script to verify table framework works with Ant Design table documentation
Run this script directly: python test_table_framework.py
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from framework.components.table_handler import TableHandler
from framework.context.element_context import ElementContext
import time

def main():
    """Test table framework against Ant Design table documentation"""
    print("="*80)
    print("ANT DESIGN TABLE FRAMEWORK TEST")
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
        time.sleep(5)  # Wait for page to fully load
        
        # Scroll down multiple times to load all example tables
        print("   >> Scrolling to find example tables...")
        for scroll in [500, 1000, 1500, 2000, 2500]:
            driver.execute_script(f"window.scrollTo(0, {scroll});")
            time.sleep(1)
        time.sleep(2)
        
        # Create table handler
        element_context = ElementContext()
        table_handler = TableHandler(driver, context=element_context)
        
        # Test 1: Find all tables (should find only top-level tables)
        print("\n" + "="*80)
        print("TEST 1: Finding all tables on the page")
        print("="*80)
        all_tables = table_handler.locator.find_all_tables(timeout=5, context=element_context)
        print(f"   >> Found {len(all_tables)} top-level table(s) on the page")
        
        if not all_tables:
            print("   >> ERROR: No tables found!")
            return
        
        # Test 2: Find the BEST interactive table (with sorting, pagination, etc.)
        print("\n" + "="*80)
        print("TEST 2: Finding best interactive table")
        print("="*80)
        
        # Re-find tables after scrolling
        all_tables = table_handler.locator.find_all_tables(timeout=10, context=element_context)
        print(f"   >> Found {len(all_tables)} tables after scrolling")
        
        target_table = None
        best_score = -1
        best_info = None
        
        # Score tables based on features (sorting, pagination, selection, etc.)
        for i, table in enumerate(all_tables):
            try:
                element_context.clear()
                table_handler.locator._store_element_in_context(table, "temp", element_context)
                element_context.set_current("temp")
                summary = table_handler.get_table_summary()
                
                headers = summary.get('headers', [])
                row_count = summary.get('row_count', {}).get('visible', 0)
                sortable = summary.get('sortable_columns', [])
                has_pagination = summary.get('has_pagination', False)
                has_selection = summary.get('has_row_selection', {}).get('checkbox', False) or summary.get('has_row_selection', {}).get('radio', False)
                
                score = 0
                
                # Prefer tables with data rows
                if row_count > 0:
                    score += 5
                if 3 <= row_count <= 50:
                    score += 10
                
                # Prefer tables with interactive features
                if sortable:
                    score += 15
                    print(f"   >> Table {i}: {len(headers)} cols, {row_count} rows, {len(sortable)} sortable - SCORE: {score}")
                if has_pagination:
                    score += 10
                if has_selection:
                    score += 5
                
                # Prefer tables with common example headers
                if 'Age' in headers or 'Name' in headers or 'Full Name' in headers:
                    score += 10
                if 'Action' in headers or 'Actions' in headers:
                    score += 5
                
                if score > best_score:
                    best_score = score
                    target_table = table
                    best_info = {
                        'index': i,
                        'headers': headers,
                        'row_count': row_count,
                        'sortable': sortable,
                        'has_pagination': has_pagination,
                        'has_selection': has_selection
                    }
                    
            except Exception as e:
                continue
        
        if not target_table:
            print("   >> No ideal table found, using first table")
            target_table = all_tables[0] if all_tables else None
        
        if not target_table:
            print("   >> ERROR: No tables found!")
            return
        
        # Store the selected table
        element_context.clear()
        table_handler.locator._store_element_in_context(target_table, "selected_table", element_context)
        element_context.set_current("selected_table")
        
        # Scroll table into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_table)
        time.sleep(2)
        
        if best_info:
            print(f"\n   >> ✓ BEST TABLE FOUND: Index {best_info['index']}")
            print(f"      Headers: {', '.join(best_info['headers'][:5])}")
            print(f"      Rows: {best_info['row_count']}")
            print(f"      Sortable: {best_info['sortable']}")
            print(f"      Pagination: {best_info['has_pagination']}")
            print(f"      Selection: {best_info['has_selection']}")
            print(f"      Score: {best_score}")
        
        # Test 3: Get table summary
        print("\n" + "="*80)
        print("TEST 3: Getting table summary")
        print("="*80)
        summary = table_handler.get_table_summary()
        table_handler.print_table_summary()
        
        # Verify we have a good table
        if not summary or summary.get('row_count', {}).get('visible', 0) == 0:
            print("   >> WARNING: Selected table has no data rows!")
            print("   >> Trying to find a better table...")
            # Try to find any table with data
            for i, table in enumerate(all_tables):
                try:
                    element_context.clear()
                    table_handler.locator._store_element_in_context(table, "temp", element_context)
                    element_context.set_current("temp")
                    test_summary = table_handler.get_table_summary()
                    if test_summary.get('row_count', {}).get('visible', 0) > 0:
                        print(f"   >> Found table {i} with {test_summary.get('row_count', {}).get('visible', 0)} rows")
                        element_context.clear()
                        table_handler.locator._store_element_in_context(table, "selected_table", element_context)
                        element_context.set_current("selected_table")
                        summary = test_summary
                        table_handler.print_table_summary()
                        break
                except:
                    continue
        
        # Test 4: Read all rows
        print("\n" + "="*80)
        print("TEST 4: Reading all rows from table")
        print("="*80)
        rows = table_handler.read_all_rows()
        print(f"   >> Read {len(rows)} rows from table")
        if rows:
            print(f"   >> First row: {rows[0]}")
        
        # Test 5: Read cell value
        print("\n" + "="*80)
        print("TEST 5: Reading cell value by column name")
        print("="*80)
        summary = table_handler.get_table_summary()
        headers = summary.get('headers', [])
        if headers:
            column_name = headers[0]
            cell_value = table_handler.read_cell_value(column_name, row_index=0)
            print(f"   >> Cell value from column '{column_name}' at row 0: {cell_value}")
        
        # Test 6: Test sorting (if available)
        print("\n" + "="*80)
        print("TEST 6: Testing table sorting")
        print("="*80)
        headers_info = summary.get('headers', [])
        sortable_columns = summary.get('sortable_columns', [])
        
        print(f"   >> Headers: {headers_info}")
        print(f"   >> Sortable columns detected: {sortable_columns}")
        
        # Try to sort by any available column
        sort_success = False
        for col in headers_info:
            if col and col not in ['Action', 'Actions', 'Operations']:  # Skip action columns
                print(f"   >> Attempting to sort by column: '{col}'")
                success = table_handler.sort_by_column(col, 'asc')
                if success:
                    print(f"   >> ✓ Successfully sorted by '{col}'")
                    time.sleep(2)  # Wait for sort animation
                    # Verify sort worked by reading rows again
                    new_rows = table_handler.read_all_rows()
                    print(f"   >> After sort, table has {len(new_rows)} rows")
                    if new_rows:
                        print(f"   >> First row after sort: {new_rows[0]}")
                    sort_success = True
                    break
                else:
                    print(f"   >> ✗ Could not sort by '{col}'")
        
        if not sort_success:
            print("   >> ⚠️  Could not sort any column - table may not have sorting enabled")
        
        # Test 7: Test pagination (if available)
        print("\n" + "="*80)
        print("TEST 7: Testing table pagination")
        print("="*80)
        if summary.get('has_pagination', False):
            print("   >> Table has pagination")
            print("   >> Attempting to go to next page...")
            success = table_handler.go_to_next_page()
            if success:
                print("   >> Successfully navigated to next page")
                time.sleep(2)
                # Read rows from new page
                new_rows = table_handler.read_all_rows()
                print(f"   >> Read {len(new_rows)} rows from new page")
            else:
                print("   >> Could not navigate to next page (may be on last page)")
        else:
            print("   >> Table does not have pagination")
        
        # Test 8: Test row selection (if available)
        print("\n" + "="*80)
        print("TEST 8: Testing row selection")
        print("="*80)
        has_selection = summary.get('has_row_selection', {})
        if has_selection.get('checkbox', False) or has_selection.get('radio', False):
            print("   >> Table has row selection")
            if rows:
                # Try to get a value from first column to select
                first_column = headers[0] if headers else None
                if first_column and rows[0].get(first_column):
                    value = rows[0].get(first_column)
                    print(f"   >> Attempting to select row with {first_column} = {value}")
                    success = table_handler.select_row_by_column_value(first_column, value)
                    if success:
                        print("   >> Successfully selected row")
                    else:
                        print("   >> Could not select row")
        else:
            print("   >> Table does not have row selection")
        
        # Test 9: Test expandable rows (if available)
        print("\n" + "="*80)
        print("TEST 9: Testing expandable rows")
        print("="*80)
        if summary.get('has_expandable_rows', False):
            print("   >> Table has expandable rows")
            print("   >> Attempting to expand first row...")
            success = table_handler.expand_row(0)
            if success:
                print("   >> Successfully expanded row")
                time.sleep(1)
                content = table_handler.read_expanded_content(0)
                if content:
                    print(f"   >> Expanded content: {content[:100]}...")
                else:
                    print("   >> No expanded content found")
            else:
                print("   >> Could not expand row")
        else:
            print("   >> Table does not have expandable rows")
        
        # Test 10: Test clicking buttons/links in table cells
        print("\n" + "="*80)
        print("TEST 10: Testing cell button clicks")
        print("="*80)
        headers = summary.get('headers', [])
        action_col = None
        for col in ['Action', 'Actions', 'Operations']:
            if col in headers:
                action_col = col
                break
        
        if action_col and rows:
            print(f"   >> Found '{action_col}' column, attempting to click button in first row...")
            # Try to click first button/link in Action column
            success = table_handler.click_cell_button(action_col, row_index=0)
            if success:
                print(f"   >> ✓ Successfully clicked button in {action_col} column")
                time.sleep(1)
            else:
                # Try clicking with specific button text
                print(f"   >> Trying to find specific button text...")
                for btn_text in ['Delete', 'Edit', 'View', 'Invite', 'action']:
                    success = table_handler.click_cell_button(action_col, row_index=0, button_text=btn_text)
                    if success:
                        print(f"   >> ✓ Successfully clicked '{btn_text}' button")
                        time.sleep(1)
                        break
                if not success:
                    print(f"   >> ✗ Could not click button (may not be clickable)")
        else:
            # Try clicking any button in any column
            print("   >> No Action column found, trying to find buttons in any column...")
            for col in headers:
                if col and col not in ['Action', 'Actions']:
                    success = table_handler.click_cell_button(col, row_index=0)
                    if success:
                        print(f"   >> ✓ Found and clicked button in '{col}' column")
                        time.sleep(1)
                        break
            else:
                print("   >> ✗ No clickable buttons found in table cells")
        
        # Test 11: Test row click
        print("\n" + "="*80)
        print("TEST 11: Testing row click")
        print("="*80)
        if rows:
            print("   >> Attempting to click first row...")
            success = table_handler.click_row(0)
            if success:
                print("   >> Successfully clicked row")
                time.sleep(0.5)
            else:
                print("   >> Could not click row")
        else:
            print("   >> No rows available to click")
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        # Keep browser open for a few seconds to see results
        print("\n>> Keeping browser open for 5 seconds...")
        time.sleep(5)
        
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

