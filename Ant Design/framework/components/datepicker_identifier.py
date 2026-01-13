"""
DatePicker Identifier - Handles analyzing and identifying Ant Design DatePicker properties
Single Responsibility: Analyze DatePicker elements and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional, List, Tuple, Union
from framework.identifiers.generic_element_identifier import GenericElementIdentifier
from datetime import datetime
import re


class DatePickerIdentifier:
    """
    Handles identifying and analyzing Ant Design DatePicker component properties
    Single Responsibility: Extract DatePicker type, state, value, and other properties
    
    Detects all DatePicker variants:
    1. Basic DatePicker
    2. DatePicker with Time Selection
    3. RangePicker
    4. WeekPicker
    5. MonthPicker
    6. QuarterPicker
    7. YearPicker
    8. Multiple DatePicker
    """
    
    # Ant Design DatePicker size classes
    SIZE_CLASSES = {
        'large': 'ant-picker-lg',
        'small': 'ant-picker-sm'
    }
    
    # DatePicker type patterns based on classes and attributes
    PICKER_TYPES = {
        'date': 'date',
        'datetime': 'datetime',
        'range': 'range',
        'week': 'week',
        'month': 'month',
        'quarter': 'quarter',
        'year': 'year',
        'multiple': 'multiple'
    }
    
    @staticmethod
    def identify_datepicker_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design DatePicker
        PRIORITY: data-attr-id is checked first to determine picker type
        
        Args:
            element: WebElement representing the DatePicker
            
        Returns:
            Dictionary containing DatePicker properties:
            {
                'picker_type': 'date'|'datetime'|'range'|'week'|'month'|'quarter'|'year'|'multiple',
                'size': 'large'|'middle'|'small',
                'disabled': bool,
                'readonly': bool,
                'open': bool,  # Calendar popup open state
                'placeholder': str|tuple,  # Single string or (start, end) for range
                'label': str,
                'value': str|dict|list,  # Current value(s)
                'format': str,  # Date format
                'has_presets': bool,
                'presets': list,
                'data_attr_id': str|None,
                'application_type': str|None,
                'metadata': dict
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        picker_info = {
            'picker_type': 'date',
            'size': 'middle',
            'disabled': False,
            'readonly': False,
            'open': False,
            'placeholder': '',
            'label': '',
            'value': None,
            'format': 'YYYY-MM-DD',
            'has_presets': False,
            'presets': [],
            'data_attr_id': generic_info.get('data_attr_id'),
            'application_type': generic_info.get('application_type'),
            'metadata': generic_info.get('metadata', {})
        }
        
        try:
            tag_name = element.tag_name.lower()
            class_attr = element.get_attribute('class') or ''
            classes = class_attr.split()
            
            # PRIORITY 1: Determine picker type from data-attr-id (if it contains type info)
            data_attr_id = picker_info['data_attr_id']
            if data_attr_id:
                data_attr_lower = data_attr_id.lower()
                if 'range' in data_attr_lower:
                    picker_info['picker_type'] = 'range'
                elif 'week' in data_attr_lower:
                    picker_info['picker_type'] = 'week'
                elif 'month' in data_attr_lower:
                    picker_info['picker_type'] = 'month'
                elif 'quarter' in data_attr_lower:
                    picker_info['picker_type'] = 'quarter'
                elif 'year' in data_attr_lower:
                    picker_info['picker_type'] = 'year'
                elif 'multiple' in data_attr_lower or 'multi' in data_attr_lower:
                    picker_info['picker_type'] = 'multiple'
                elif 'datetime' in data_attr_lower or 'time' in data_attr_lower:
                    picker_info['picker_type'] = 'datetime'
            
            # PRIORITY 2: Determine type from Ant Design classes
            if 'ant-picker-range' in class_attr:
                picker_info['picker_type'] = 'range'
            elif 'ant-picker-week-picker' in class_attr or 'picker="week"' in str(element.get_attribute('data-picker')):
                picker_info['picker_type'] = 'week'
            elif 'ant-picker-month-picker' in class_attr or 'picker="month"' in str(element.get_attribute('data-picker')):
                picker_info['picker_type'] = 'month'
            elif 'ant-picker-quarter-picker' in class_attr or 'picker="quarter"' in str(element.get_attribute('data-picker')):
                picker_info['picker_type'] = 'quarter'
            elif 'ant-picker-year-picker' in class_attr or 'picker="year"' in str(element.get_attribute('data-picker')):
                picker_info['picker_type'] = 'year'
            
            # Check for time selection (showTime)
            if 'ant-picker-time-picker' in class_attr or DatePickerIdentifier._has_time_selection(element):
                if picker_info['picker_type'] == 'date':
                    picker_info['picker_type'] = 'datetime'
            
            # Check for multiple mode
            if DatePickerIdentifier._is_multiple_mode(element):
                picker_info['picker_type'] = 'multiple'
            
            # Determine size
            if 'ant-picker-lg' in class_attr:
                picker_info['size'] = 'large'
            elif 'ant-picker-sm' in class_attr:
                picker_info['size'] = 'small'
            
            # Check disabled state
            picker_info['disabled'] = (
                'ant-picker-disabled' in class_attr or
                element.get_attribute('disabled') is not None or
                element.get_attribute('aria-disabled') == 'true'
            )
            
            # Check readonly state
            picker_info['readonly'] = (
                element.get_attribute('readonly') is not None or
                'ant-picker-readonly' in class_attr
            )
            
            # Check if calendar popup is open
            picker_info['open'] = DatePickerIdentifier._is_calendar_open(element)
            
            # Extract placeholder(s)
            picker_info['placeholder'] = DatePickerIdentifier._extract_placeholder(element, picker_info['picker_type'])
            
            # Extract label
            picker_info['label'] = DatePickerIdentifier._extract_label(element)
            
            # Extract current value(s)
            picker_info['value'] = DatePickerIdentifier._extract_value(element, picker_info['picker_type'])
            
            # Extract format
            picker_info['format'] = DatePickerIdentifier._extract_format(element)
            
            # Check for presets
            picker_info['has_presets'], picker_info['presets'] = DatePickerIdentifier._extract_presets(element)
            
        except Exception as e:
            print(f"Error identifying DatePicker: {str(e)}")
        
        return picker_info
    
    @staticmethod
    def _has_time_selection(element: WebElement) -> bool:
        """Check if DatePicker has time selection enabled"""
        try:
            # Check for time picker panel in the calendar dropdown
            # Get driver from element (using private attribute as fallback)
            try:
                driver = element._parent
            except:
                # Alternative: try to find dropdown from document root
                from selenium.webdriver.common.by import By
                # Check for showTime attribute or class first (faster)
                class_attr = element.get_attribute('class') or ''
                if 'showTime' in class_attr or 'time' in class_attr.lower():
                    return True
                return False
            
            dropdown = driver.find_element(By.CSS_SELECTOR, '.ant-picker-dropdown')
            time_panel = dropdown.find_elements(By.CSS_SELECTOR, '.ant-picker-time-panel')
            return len(time_panel) > 0
        except:
            # Check for showTime attribute or class
            class_attr = element.get_attribute('class') or ''
            return 'showTime' in class_attr or 'time' in class_attr.lower()
    
    @staticmethod
    def _is_multiple_mode(element: WebElement) -> bool:
        """Check if DatePicker is in multiple selection mode"""
        try:
            # Check for multiple class or attribute
            class_attr = element.get_attribute('class') or ''
            return 'multiple' in class_attr.lower() or element.get_attribute('mode') == 'multiple'
        except:
            return False
    
    @staticmethod
    def _is_calendar_open(element: WebElement) -> bool:
        """Check if calendar popup is currently open"""
        try:
            # Get driver from element (using private attribute)
            try:
                driver = element._parent
            except:
                # Fallback: check aria-expanded
                aria_expanded = element.get_attribute('aria-expanded')
                return aria_expanded == 'true'
            
            # Check for visible calendar dropdown
            dropdowns = driver.find_elements(By.CSS_SELECTOR, '.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)')
            if dropdowns:
                # Check if this DatePicker's dropdown is visible
                for dropdown in dropdowns:
                    if dropdown.is_displayed():
                        # Try to find connection to this element
                        try:
                            # Check if dropdown contains calendar panels
                            panels = dropdown.find_elements(By.CSS_SELECTOR, '.ant-picker-panel')
                            if panels:
                                return True
                        except:
                            pass
            return False
        except:
            # Fallback: check aria-expanded
            aria_expanded = element.get_attribute('aria-expanded')
            return aria_expanded == 'true'
    
    @staticmethod
    def _extract_placeholder(element: WebElement, picker_type: str) -> Union[str, Tuple[str, str]]:
        """Extract placeholder text(s) from DatePicker"""
        try:
            if picker_type == 'range':
                # RangePicker has two inputs
                inputs = element.find_elements(By.CSS_SELECTOR, '.ant-picker-input input')
                if len(inputs) >= 2:
                    placeholder_start = inputs[0].get_attribute('placeholder') or ''
                    placeholder_end = inputs[1].get_attribute('placeholder') or ''
                    return (placeholder_start, placeholder_end)
                else:
                    # Single placeholder for range
                    input_elem = element.find_element(By.CSS_SELECTOR, '.ant-picker-input input')
                    placeholder = input_elem.get_attribute('placeholder') or ''
                    return (placeholder, placeholder)
            else:
                # Single DatePicker
                input_elem = element.find_element(By.CSS_SELECTOR, '.ant-picker-input input')
                return input_elem.get_attribute('placeholder') or ''
        except:
            return '' if picker_type != 'range' else ('', '')
    
    @staticmethod
    def _extract_label(element: WebElement) -> str:
        """Extract associated label text"""
        try:
            # Try to find label element
            # Check for aria-label
            aria_label = element.get_attribute('aria-label')
            if aria_label:
                return aria_label
            
            # Check for associated label element
            label_id = element.get_attribute('aria-labelledby')
            if label_id:
                try:
                    driver = element._parent
                    label_elem = driver.find_element(By.ID, label_id)
                    return label_elem.text.strip()
                except:
                    pass
            
            # Check for preceding label
            try:
                # Find parent form item
                parent = element.find_element(By.XPATH, './ancestor::div[contains(@class, "ant-form-item")]')
                label = parent.find_element(By.CSS_SELECTOR, '.ant-form-item-label label')
                return label.text.strip()
            except:
                pass
            
            # Check for preceding sibling label
            try:
                label = element.find_element(By.XPATH, './preceding-sibling::label[1]')
                return label.text.strip()
            except:
                pass
            
            return ''
        except:
            return ''
    
    @staticmethod
    def _extract_value(element: WebElement, picker_type: str) -> Union[str, Dict[str, str], List[str]]:
        """Extract current value(s) from DatePicker"""
        try:
            if picker_type == 'range':
                # RangePicker: extract start and end dates
                inputs = element.find_elements(By.CSS_SELECTOR, '.ant-picker-input input')
                if len(inputs) >= 2:
                    start_value = inputs[0].get_attribute('value') or ''
                    end_value = inputs[1].get_attribute('value') or ''
                    return {'start': start_value, 'end': end_value}
                return {'start': '', 'end': ''}
            elif picker_type == 'multiple':
                # Multiple DatePicker: extract list of dates
                input_elem = element.find_element(By.CSS_SELECTOR, '.ant-picker-input input')
                value = input_elem.get_attribute('value') or ''
                # Parse multiple dates (comma-separated or in tags)
                if value:
                    # Check for tag-based display
                    tags = element.find_elements(By.CSS_SELECTOR, '.ant-picker-selection-item')
                    if tags:
                        return [tag.text.strip() for tag in tags]
                    # Otherwise, split by comma
                    return [d.strip() for d in value.split(',') if d.strip()]
                return []
            else:
                # Single DatePicker
                input_elem = element.find_element(By.CSS_SELECTOR, '.ant-picker-input input')
                return input_elem.get_attribute('value') or ''
        except:
            return '' if picker_type != 'range' and picker_type != 'multiple' else ({'start': '', 'end': ''} if picker_type == 'range' else [])
    
    @staticmethod
    def _extract_format(element: WebElement) -> str:
        """Extract date format from DatePicker"""
        try:
            # Try to get format from data-format or format attribute
            format_attr = element.get_attribute('data-format') or element.get_attribute('format')
            if format_attr:
                return format_attr
            
            # Infer from placeholder or value
            input_elem = element.find_element(By.CSS_SELECTOR, '.ant-picker-input input')
            placeholder = input_elem.get_attribute('placeholder') or ''
            value = input_elem.get_attribute('value') or ''
            
            # Common format patterns
            if 'YYYY' in placeholder or 'yyyy' in placeholder:
                if 'MM' in placeholder:
                    if 'DD' in placeholder:
                        if 'HH' in placeholder or 'hh' in placeholder:
                            return 'YYYY-MM-DD HH:mm:ss'
                        return 'YYYY-MM-DD'
                    return 'YYYY-MM'
                return 'YYYY'
            
            # Default format
            return 'YYYY-MM-DD'
        except:
            return 'YYYY-MM-DD'
    
    @staticmethod
    def _extract_presets(element: WebElement) -> Tuple[bool, List[str]]:
        """Extract preset/quick-select ranges if present"""
        try:
            # Get driver from element
            try:
                driver = element._parent
            except:
                return False, []
            
            # Check for preset panel in dropdown
            dropdowns = driver.find_elements(By.CSS_SELECTOR, '.ant-picker-dropdown')
            presets = []
            
            for dropdown in dropdowns:
                if dropdown.is_displayed():
                    preset_items = dropdown.find_elements(By.CSS_SELECTOR, '.ant-picker-preset-range, .ant-picker-ranges-item')
                    for item in preset_items:
                        preset_text = item.text.strip()
                        if preset_text:
                            presets.append(preset_text)
            
            return len(presets) > 0, presets
        except:
            return False, []
    
    @staticmethod
    def get_all_datepickers_info(elements: List[WebElement]) -> Dict[str, any]:
        """
        Get information about all DatePickers on the page
        Handles stale element references gracefully
        
        Args:
            elements: List of DatePicker WebElements
            
        Returns:
            Dictionary with summary:
            {
                'total': int,
                'by_type': dict,
                'disabled_count': int,
                'readonly_count': int,
                'open_count': int,
                'details': list
            }
        """
        summary = {
            'total': len(elements),
            'by_type': {},
            'disabled_count': 0,
            'readonly_count': 0,
            'open_count': 0,
            'details': []
        }
        
        for idx, element in enumerate(elements):
            try:
                # Try to identify, catch stale element exceptions
                try:
                    picker_info = DatePickerIdentifier.identify_datepicker_type(element)
                except Exception as e:
                    # Stale element or other error - skip this one
                    if 'stale' in str(e).lower():
                        continue
                    # Try to get basic info without full identification
                    try:
                        class_attr = element.get_attribute('class') or ''
                        picker_type = 'date'
                        if 'ant-picker-range' in class_attr:
                            picker_type = 'range'
                        picker_info = {
                            'picker_type': picker_type,
                            'size': 'middle',
                            'disabled': 'ant-picker-disabled' in class_attr,
                            'readonly': False,
                            'open': False,
                            'placeholder': '',
                            'label': '',
                            'value': None,
                            'format': 'YYYY-MM-DD',
                            'data_attr_id': None
                        }
                    except:
                        # Skip if we can't even get basic info
                        continue
                
                picker_type = picker_info.get('picker_type', 'date')
                
                # Count by type
                if picker_type not in summary['by_type']:
                    summary['by_type'][picker_type] = 0
                summary['by_type'][picker_type] += 1
                
                # Count states
                if picker_info.get('disabled', False):
                    summary['disabled_count'] += 1
                if picker_info.get('readonly', False):
                    summary['readonly_count'] += 1
                if picker_info.get('open', False):
                    summary['open_count'] += 1
                
                # Store details
                summary['details'].append({
                    'type': picker_type,
                    'size': picker_info.get('size', 'middle'),
                    'disabled': picker_info.get('disabled', False),
                    'readonly': picker_info.get('readonly', False),
                    'open': picker_info.get('open', False),
                    'placeholder': picker_info.get('placeholder', ''),
                    'label': picker_info.get('label', ''),
                    'value': picker_info.get('value'),
                    'format': picker_info.get('format', 'YYYY-MM-DD'),
                    'data_attr_id': picker_info.get('data_attr_id')
                })
            except Exception as e:
                # Skip elements that cause errors
                continue
        
        return summary
