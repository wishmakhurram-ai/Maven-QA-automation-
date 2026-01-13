"""
Generic Ant Design DatePicker Handler
Handles DatePicker interactions (selecting dates, clearing, opening, closing, etc.)
Uses DatePickerLocator for finding DatePickers and DatePickerIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
from typing import Optional, Dict, List, Tuple
from framework.base.base_page import BasePage
from framework.components.datepicker_locator import DatePickerLocator
from framework.components.datepicker_identifier import DatePickerIdentifier
from framework.context.element_context import ElementContext, ElementInfo
from datetime import datetime, timedelta
import time
import re


class DatePickerHandler(BasePage):
    """
    Generic handler for Ant Design DatePicker interactions
    Single Responsibility: Handle DatePicker interactions (selecting, clearing, opening, closing, etc.)
    Uses DatePickerLocator to find DatePickers and DatePickerIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize DatePicker Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = DatePickerLocator(driver)
        self.identifier = DatePickerIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr_id',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a DatePicker and store it in context
        
        Args:
            identifier: Value to identify the DatePicker (data-attr-id, label, or type)
            identifier_type: Type of identifier ('data_attr_id', 'label', 'type', 'position')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if DatePicker was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_datepicker_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label':
                element = self.locator.find_datepicker_by_label(identifier, exact_match=False, timeout=timeout, context=self.context)
            elif identifier_type == 'type':
                elements = self.locator.find_datepicker_by_type(identifier, timeout, self.context)
                if elements:
                    element = elements[0]
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_datepicker_by_position(position, timeout=timeout, context=self.context)
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"DatePicker identified and stored in context: {identifier}")
                return True
            else:
                print(f"DatePicker not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying DatePicker: {str(e)}")
            return False
    
    def open_datepicker(self, identifier: str, identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Open a DatePicker calendar popup
        
        Args:
            identifier: Value to identify the DatePicker
            identifier_type: Type of identifier ('data_attr_id', 'label', 'type', 'position', 'auto')
            timeout: Maximum wait time in seconds
            
        Returns:
            True if DatePicker was opened successfully, False otherwise
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Check if already open
            picker_info = self.identifier.identify_datepicker_type(element)
            if picker_info.get('open', False):
                print("DatePicker is already open")
                return True
            
            # Scroll into view
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", element)
            
            # Click on the input to open calendar
            input_elem = element.find_element(By.CSS_SELECTOR, '.ant-picker-input input')
            input_elem.click()
            
            # Wait for calendar to open
            self._wait_for_calendar_open(timeout=5)
            
            print(f"DatePicker opened successfully")
            return True
            
        except Exception as e:
            print(f"Error opening DatePicker: {str(e)}")
            return False
    
    def close_datepicker(self, identifier: str, identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Close a DatePicker calendar popup
        
        Args:
            identifier: Value to identify the DatePicker
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if DatePicker was closed successfully, False otherwise
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Press Escape key or click outside
            input_elem = element.find_element(By.CSS_SELECTOR, '.ant-picker-input input')
            input_elem.send_keys(Keys.ESCAPE)
            
            # Wait for calendar to close
            time.sleep(0.5)
            
            print(f"DatePicker closed successfully")
            return True
            
        except Exception as e:
            print(f"Error closing DatePicker: {str(e)}")
            return False
    
    def select_date(self, identifier: str, date_str: str, identifier_type: str = 'auto', 
                    timeout: int = 10) -> bool:
        """
        Select a single date in a DatePicker
        
        Args:
            identifier: Value to identify the DatePicker
            date_str: Date string in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:mm:ss' for datetime
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if date was selected successfully, False otherwise
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            picker_info = self.identifier.identify_datepicker_type(element)
            picker_type = picker_info.get('picker_type', 'date')
            
            # Open DatePicker if not open
            if not picker_info.get('open', False):
                self.open_datepicker(identifier, identifier_type, timeout)
            
            # Parse date
            date_obj = self._parse_date(date_str)
            if not date_obj:
                print(f"Invalid date format: {date_str}")
                return False
            
            # Navigate to the correct month/year
            self._navigate_to_date(date_obj)
            
            # Select the date
            if picker_type == 'datetime':
                # Select date first, then time
                self._select_date_cell(date_obj)
                time.sleep(0.5)
                self._select_time(date_obj)
            elif picker_type == 'week':
                self._select_week(date_obj)
            elif picker_type == 'month':
                self._select_month(date_obj)
            elif picker_type == 'quarter':
                self._select_quarter(date_obj)
            elif picker_type == 'year':
                self._select_year(date_obj)
            else:
                self._select_date_cell(date_obj)
            
            print(f"Date selected successfully: {date_str}")
            return True
            
        except Exception as e:
            print(f"Error selecting date: {str(e)}")
            return False
    
    def select_date_range(self, identifier: str, start_date: str, end_date: str,
                          identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Select a date range in a RangePicker
        
        Args:
            identifier: Value to identify the RangePicker
            start_date: Start date string in format 'YYYY-MM-DD'
            end_date: End date string in format 'YYYY-MM-DD'
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if date range was selected successfully, False otherwise
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            picker_info = self.identifier.identify_datepicker_type(element)
            if picker_info.get('picker_type') != 'range':
                print("DatePicker is not a RangePicker")
                return False
            
            # Open DatePicker if not open
            if not picker_info.get('open', False):
                self.open_datepicker(identifier, identifier_type, timeout)
            
            # Parse dates
            start_obj = self._parse_date(start_date)
            end_obj = self._parse_date(end_date)
            if not start_obj or not end_obj:
                print(f"Invalid date format: {start_date} or {end_date}")
                return False
            
            # Navigate to start date month
            self._navigate_to_date(start_obj)
            
            # Select start date
            self._select_date_cell(start_obj)
            time.sleep(0.5)
            
            # Navigate to end date month if needed
            if start_obj.month != end_obj.month or start_obj.year != end_obj.year:
                self._navigate_to_date(end_obj)
            
            # Select end date
            self._select_date_cell(end_obj)
            
            print(f"Date range selected successfully: {start_date} to {end_date}")
            return True
            
        except Exception as e:
            print(f"Error selecting date range: {str(e)}")
            return False
    
    def select_multiple_dates(self, identifier: str, dates: List[str],
                              identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Select multiple dates in a Multiple DatePicker
        
        Args:
            identifier: Value to identify the DatePicker
            dates: List of date strings in format 'YYYY-MM-DD'
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if all dates were selected successfully, False otherwise
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            picker_info = self.identifier.identify_datepicker_type(element)
            if picker_info.get('picker_type') != 'multiple':
                print("DatePicker is not a Multiple DatePicker")
                return False
            
            # Open DatePicker if not open
            if not picker_info.get('open', False):
                self.open_datepicker(identifier, identifier_type, timeout)
            
            # Select each date
            for date_str in dates:
                date_obj = self._parse_date(date_str)
                if not date_obj:
                    print(f"Invalid date format: {date_str}")
                    continue
                
                self._navigate_to_date(date_obj)
                self._select_date_cell(date_obj)
                time.sleep(0.3)
            
            print(f"Multiple dates selected successfully: {len(dates)} dates")
            return True
            
        except Exception as e:
            print(f"Error selecting multiple dates: {str(e)}")
            return False
    
    def clear_datepicker(self, identifier: str, identifier_type: str = 'auto',
                        timeout: int = 10) -> bool:
        """
        Clear selected value(s) from a DatePicker
        
        Args:
            identifier: Value to identify the DatePicker
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if DatePicker was cleared successfully, False otherwise
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Try to find and click clear button
            try:
                clear_btn = element.find_element(By.CSS_SELECTOR, '.ant-picker-clear')
                clear_btn.click()
                print("DatePicker cleared using clear button")
                return True
            except:
                pass
            
            # Fallback: clear input value
            inputs = element.find_elements(By.CSS_SELECTOR, '.ant-picker-input input')
            for input_elem in inputs:
                input_elem.clear()
                # Trigger change event
                self.execute_js("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", input_elem)
            
            print("DatePicker cleared successfully")
            return True
            
        except Exception as e:
            print(f"Error clearing DatePicker: {str(e)}")
            return False
    
    def select_preset(self, identifier: str, preset_text: str,
                     identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Select a preset/quick-select range
        
        Args:
            identifier: Value to identify the DatePicker
            preset_text: Text of the preset to select (e.g., "Today", "Last 7 Days")
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if preset was selected successfully, False otherwise
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Open DatePicker if not open
            picker_info = self.identifier.identify_datepicker_type(element)
            if not picker_info.get('open', False):
                self.open_datepicker(identifier, identifier_type, timeout)
            
            # Find preset button
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
            
            # Find preset item
            preset_items = dropdown.find_elements(By.CSS_SELECTOR, '.ant-picker-preset-range, .ant-picker-ranges-item')
            for item in preset_items:
                if preset_text.lower() in item.text.lower():
                    item.click()
                    print(f"Preset selected: {preset_text}")
                    return True
            
            print(f"Preset not found: {preset_text}")
            return False
            
        except Exception as e:
            print(f"Error selecting preset: {str(e)}")
            return False
    
    def get_datepicker_value(self, identifier: str, identifier_type: str = 'auto',
                            timeout: int = 10) -> Optional[str | Dict[str, str] | List[str]]:
        """
        Get current value(s) from a DatePicker
        
        Args:
            identifier: Value to identify the DatePicker
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            Current value(s) - string for single, dict for range, list for multiple
        """
        element = self._find_datepicker(identifier, identifier_type, timeout)
        if not element:
            return None
        
        try:
            picker_info = self.identifier.identify_datepicker_type(element)
            return picker_info.get('value')
        except Exception as e:
            print(f"Error getting DatePicker value: {str(e)}")
            return None
    
    def _find_datepicker(self, identifier: str, identifier_type: str, timeout: int) -> Optional[WebElement]:
        """Internal helper to find DatePicker by identifier"""
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_datepicker_by_data_attr(identifier, timeout)
            elif identifier_type == 'label':
                element = self.locator.find_datepicker_by_semantic_label(identifier, timeout)
            elif identifier_type == 'type':
                elements = self.locator.find_datepicker_by_type(identifier, timeout)
                if elements:
                    element = elements[0]
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_datepicker_by_position(position, timeout)
            elif identifier_type == 'auto':
                # Try semantic label first (most common in Gherkin)
                element = self.locator.find_datepicker_by_semantic_label(identifier, timeout=3)
                if not element:
                    # Try data-attr-id
                    element = self.locator.find_datepicker_by_data_attr(identifier, timeout=3)
                if not element:
                    # Try label
                    element = self.locator.find_datepicker_by_label(identifier, timeout=3)
            
            return element
        except:
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        try:
            # Try common formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y/%m/%d',
                '%d/%m/%Y',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            
            return None
        except:
            return None
    
    def _navigate_to_date(self, target_date: datetime) -> None:
        """Navigate calendar to target month/year"""
        try:
            wait = WebDriverWait(self.driver, 5)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
            
            # Get current displayed month/year
            current_header = dropdown.find_element(By.CSS_SELECTOR, '.ant-picker-header-view')
            current_text = current_header.text
            
            # Navigate to target year if needed
            target_year = target_date.year
            current_year = datetime.now().year  # Default, will be updated
            
            # Extract year from current text
            year_match = re.search(r'\d{4}', current_text)
            if year_match:
                current_year = int(year_match.group())
            
            # Navigate years if needed
            if target_year < current_year:
                for _ in range(current_year - target_year):
                    prev_btn = dropdown.find_element(By.CSS_SELECTOR, '.ant-picker-header-prev-btn')
                    prev_btn.click()
                    time.sleep(0.2)
            elif target_year > current_year:
                for _ in range(target_year - current_year):
                    next_btn = dropdown.find_element(By.CSS_SELECTOR, '.ant-picker-header-next-btn')
                    next_btn.click()
                    time.sleep(0.2)
            
            # Navigate months if needed
            target_month = target_date.month
            current_month = datetime.now().month  # Default
            
            # Extract month from current text
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for i, month_name in enumerate(month_names, 1):
                if month_name in current_text:
                    current_month = i
                    break
            
            if target_month < current_month:
                for _ in range(current_month - target_month):
                    prev_btn = dropdown.find_element(By.CSS_SELECTOR, '.ant-picker-header-prev-btn')
                    prev_btn.click()
                    time.sleep(0.2)
            elif target_month > current_month:
                for _ in range(target_month - current_month):
                    next_btn = dropdown.find_element(By.CSS_SELECTOR, '.ant-picker-header-next-btn')
                    next_btn.click()
                    time.sleep(0.2)
            
        except Exception as e:
            print(f"Error navigating to date: {str(e)}")
    
    def _select_date_cell(self, date_obj: datetime) -> None:
        """Select a date cell in the calendar"""
        try:
            wait = WebDriverWait(self.driver, 5)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
            
            # Find the date cell
            day = date_obj.day
            cell = dropdown.find_element(By.XPATH, f"//td[@title='{day}' or contains(@class, 'ant-picker-cell')]//div[text()='{day}']")
            cell.click()
            time.sleep(0.3)
            
        except Exception as e:
            print(f"Error selecting date cell: {str(e)}")
    
    def _select_time(self, date_obj: datetime) -> None:
        """Select time in datetime picker"""
        try:
            wait = WebDriverWait(self.driver, 5)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
            
            # Find time picker panel
            time_panel = dropdown.find_element(By.CSS_SELECTOR, '.ant-picker-time-panel')
            
            # Select hour
            hour = date_obj.hour
            hour_cells = time_panel.find_elements(By.CSS_SELECTOR, '.ant-picker-time-panel-column:first-child .ant-picker-time-panel-cell')
            for cell in hour_cells:
                if str(hour) in cell.text:
                    cell.click()
                    break
            
            time.sleep(0.2)
            
            # Select minute
            minute = date_obj.minute
            minute_cells = time_panel.find_elements(By.CSS_SELECTOR, '.ant-picker-time-panel-column:nth-child(2) .ant-picker-time-panel-cell')
            for cell in minute_cells:
                if str(minute) in cell.text:
                    cell.click()
                    break
            
            time.sleep(0.2)
            
            # Click OK button if present
            try:
                ok_btn = dropdown.find_element(By.CSS_SELECTOR, '.ant-picker-ok')
                ok_btn.click()
            except:
                pass
            
        except Exception as e:
            print(f"Error selecting time: {str(e)}")
    
    def _select_week(self, date_obj: datetime) -> None:
        """Select a week"""
        # For week picker, select any day in the week
        self._select_date_cell(date_obj)
    
    def _select_month(self, date_obj: datetime) -> None:
        """Select a month"""
        try:
            wait = WebDriverWait(self.driver, 5)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
            
            month = date_obj.month
            month_cell = dropdown.find_element(By.XPATH, f"//div[contains(@class, 'ant-picker-month-panel-cell')]//div[text()='{month}']")
            month_cell.click()
            time.sleep(0.3)
            
        except Exception as e:
            print(f"Error selecting month: {str(e)}")
    
    def _select_quarter(self, date_obj: datetime) -> None:
        """Select a quarter"""
        try:
            wait = WebDriverWait(self.driver, 5)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
            
            quarter = (date_obj.month - 1) // 3 + 1
            quarter_cell = dropdown.find_element(By.XPATH, f"//div[contains(@class, 'ant-picker-quarter-panel-cell')]//div[text()='Q{quarter}']")
            quarter_cell.click()
            time.sleep(0.3)
            
        except Exception as e:
            print(f"Error selecting quarter: {str(e)}")
    
    def _select_year(self, date_obj: datetime) -> None:
        """Select a year"""
        try:
            wait = WebDriverWait(self.driver, 5)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
            
            year = date_obj.year
            year_cell = dropdown.find_element(By.XPATH, f"//div[contains(@class, 'ant-picker-year-panel-cell')]//div[text()='{year}']")
            year_cell.click()
            time.sleep(0.3)
            
        except Exception as e:
            print(f"Error selecting year: {str(e)}")
    
    def _wait_for_calendar_open(self, timeout: int = 5) -> None:
        """Wait for calendar dropdown to open"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')))
        except:
            pass
    
    def get_all_datepickers_summary(self) -> Dict[str, any]:
        """
        Get a summary of all detected DatePickers on the page
        
        Returns:
            Dictionary with DatePicker counts and details by type
        """
        try:
            all_datepickers = self.locator.find_all_ant_datepickers()
            return self.identifier.get_all_datepickers_info(all_datepickers)
        except Exception as e:
            print(f"Error getting DatePickers summary: {str(e)}")
            return {'total': 0, 'by_type': {}, 'disabled_count': 0, 'readonly_count': 0, 'open_count': 0, 'details': []}
    
    def print_datepickers_summary(self) -> None:
        """Print a readable summary of all detected DatePickers"""
        summary = self.get_all_datepickers_summary()
        
        print(f"\n{'='*70}")
        print(f"DATEPICKER COMPONENTS SUMMARY")
        print(f"{'='*70}")
        print(f"Total DatePickers detected: {summary['total']}")
        print(f"\nBy Type:")
        for picker_type, count in summary['by_type'].items():
            print(f"  - {picker_type}: {count}")
        
        print(f"\nStates:")
        print(f"  - Disabled: {summary['disabled_count']}")
        print(f"  - Read-only: {summary['readonly_count']}")
        print(f"  - Open: {summary['open_count']}")
        
        if summary['details']:
            print(f"\nDetails:")
            for idx, detail in enumerate(summary['details'], 1):
                print(f"\n  DatePicker #{idx}:")
                print(f"    Type: {detail['type']}")
                print(f"    Size: {detail['size']}")
                print(f"    Disabled: {detail['disabled']}")
                print(f"    Read-only: {detail['readonly']}")
                print(f"    Open: {detail['open']}")
                if detail['placeholder']:
                    print(f"    Placeholder: '{detail['placeholder']}'")
                if detail['label']:
                    print(f"    Label: '{detail['label']}'")
                if detail['value']:
                    print(f"    Value: {detail['value']}")
                if detail['data_attr_id']:
                    print(f"    Data-attr-id: '{detail['data_attr_id']}'")
        print(f"{'='*70}\n")
