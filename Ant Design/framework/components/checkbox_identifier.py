"""
Checkbox Identifier - Handles analyzing and identifying Ant Design Checkbox properties
Single Responsibility: Analyze checkbox elements and extract their properties
Detects all Ant Design checkbox types: Basic, Disabled, Controlled, Checkbox Group, Check All, Indeterminate, Grid Layout
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional, List
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class CheckboxIdentifier:
    """
    Handles identifying and analyzing Ant Design Checkbox component properties
    Single Responsibility: Extract checkbox state, disabled, label, group info, indeterminate, and other properties
    """
    
    # Ant Design checkbox class patterns
    CHECKBOX_CLASSES = {
        'checkbox': 'ant-checkbox',
        'wrapper': 'ant-checkbox-wrapper',
        'group': 'ant-checkbox-group',
        'disabled': 'ant-checkbox-disabled',
        'checked': 'ant-checkbox-checked',
        'indeterminate': 'ant-checkbox-indeterminate'
    }
    
    @staticmethod
    def identify_checkbox_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design Checkbox
        Integrates with GenericElementIdentifier to read custom attributes
        
        Args:
            element: WebElement representing the checkbox
            
        Returns:
            Dictionary containing checkbox properties:
            {
                'type': 'basic'|'disabled'|'controlled'|'group'|'check_all'|'indeterminate'|'grid_layout',
                'checked': bool,  # Checked/unchecked state
                'disabled': bool,
                'indeterminate': bool,  # Indeterminate state (true/false)
                'label_text': str|None,
                'data_attr_id': str|None,
                'group_name': str|None,  # Checkbox group name
                'group_id': str|None,  # Checkbox group identifier
                'total_in_group': int|None,  # Total checkboxes in group
                'checked_in_group': List[str]|None,  # List of checked options in group
                'has_check_all': bool,  # True if has "Check All" behavior
                'aria_checked': str|None,  # 'true'|'false'|'mixed' (for indeterminate)
                'aria_disabled': str|None,  # 'true'|'false'
                'aria_label': str|None,
                'value': str|None,  # Checkbox value
                'name': str|None,  # Checkbox name (for grouping)
                'controlled': bool|None,  # True if controlled, False if uncontrolled
                'metadata': dict
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        checkbox_info = {
            'type': 'basic',
            'checked': False,
            'disabled': False,
            'indeterminate': False,
            'label_text': None,
            'data_attr_id': generic_info.get('data_attr_id'),
            'group_name': None,
            'group_id': None,
            'total_in_group': None,
            'checked_in_group': None,
            'has_check_all': False,
            'aria_checked': None,
            'aria_disabled': None,
            'aria_label': None,
            'value': None,
            'name': None,
            'controlled': None,
            'metadata': generic_info.get('metadata', {})
        }
        
        try:
            # Get class attribute
            class_attr = element.get_attribute('class') or ''
            classes = class_attr.split()
            
            # Find the actual checkbox input element
            checkbox_input = CheckboxIdentifier._find_checkbox_input(element)
            if not checkbox_input:
                # If element itself is input[type="checkbox"]
                if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'checkbox':
                    checkbox_input = element
                else:
                    # Try to find wrapper and then input
                    wrapper = CheckboxIdentifier._find_checkbox_wrapper(element)
                    if wrapper:
                        try:
                            checkbox_input = wrapper.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        except:
                            pass
            
            if checkbox_input:
                # Get checkbox input properties
                checkbox_info['checked'] = checkbox_input.is_selected()
                checkbox_info['disabled'] = not checkbox_input.is_enabled() or checkbox_input.get_attribute('disabled') is not None
                checkbox_info['value'] = checkbox_input.get_attribute('value')
                checkbox_info['name'] = checkbox_input.get_attribute('name')
                checkbox_info['aria_checked'] = checkbox_input.get_attribute('aria-checked')
                checkbox_info['aria_disabled'] = checkbox_input.get_attribute('aria-disabled')
                checkbox_info['aria_label'] = checkbox_input.get_attribute('aria-label')
                
                # Check for indeterminate state via JavaScript (more reliable)
                try:
                    is_indeterminate = checkbox_input.get_property('indeterminate')
                    if is_indeterminate:
                        checkbox_info['indeterminate'] = True
                except:
                    pass
                
                # Check for checked state via class
                if 'ant-checkbox-checked' in classes:
                    checkbox_info['checked'] = True
                
                # Check for indeterminate state via class
                if 'ant-checkbox-indeterminate' in classes:
                    checkbox_info['indeterminate'] = True
                
                # Use aria-checked as source of truth if available
                if checkbox_info['aria_checked']:
                    aria_checked = checkbox_info['aria_checked'].lower()
                    if aria_checked == 'true':
                        checkbox_info['checked'] = True
                    elif aria_checked == 'false':
                        checkbox_info['checked'] = False
                    elif aria_checked == 'mixed':
                        checkbox_info['indeterminate'] = True
                        checkbox_info['checked'] = False  # Indeterminate is neither checked nor unchecked
            
            # Check if disabled via class
            if 'ant-checkbox-disabled' in classes:
                checkbox_info['disabled'] = True
            
            # Get label text
            checkbox_info['label_text'] = CheckboxIdentifier._extract_label_text(element, checkbox_input)
            
            # Get group information
            group_info = CheckboxIdentifier._get_group_info(element, checkbox_input)
            checkbox_info.update(group_info)
            
            # Check for "Check All" behavior
            checkbox_info['has_check_all'] = CheckboxIdentifier._has_check_all_behavior(element, checkbox_info)
            
            # Determine checkbox type
            checkbox_info['type'] = CheckboxIdentifier._determine_checkbox_type(element, classes, checkbox_info)
            
            # Determine if controlled
            if checkbox_input:
                has_checked_attr = checkbox_input.get_attribute('checked') is not None
                has_default_checked = checkbox_input.get_attribute('defaultChecked') is not None
                
                if has_checked_attr:
                    checkbox_info['controlled'] = True
                elif has_default_checked:
                    checkbox_info['controlled'] = False
                else:
                    # Try to infer from data attributes
                    data_controlled = element.get_attribute('data-controlled')
                    if data_controlled:
                        checkbox_info['controlled'] = data_controlled.lower() == 'true'
            
        except Exception as e:
            print(f"Error identifying checkbox type: {str(e)}")
        
        return checkbox_info
    
    @staticmethod
    def _find_checkbox_input(element: WebElement) -> Optional[WebElement]:
        """Find the actual checkbox input element"""
        try:
            # If element is already input[type="checkbox"]
            if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'checkbox':
                return element
            
            # Try to find input inside
            try:
                checkbox_input = element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                return checkbox_input
            except:
                pass
            
            # Try to find in wrapper
            try:
                wrapper = element.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-wrapper")][1]')
                checkbox_input = wrapper.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                return checkbox_input
            except:
                pass
            
        except:
            pass
        return None
    
    @staticmethod
    def _find_checkbox_wrapper(element: WebElement) -> Optional[WebElement]:
        """Find the checkbox wrapper element"""
        try:
            # Check if element itself is wrapper
            class_attr = element.get_attribute('class') or ''
            if 'ant-checkbox-wrapper' in class_attr:
                return element
            
            # Try to find wrapper ancestor
            try:
                wrapper = element.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-wrapper")][1]')
                return wrapper
            except:
                pass
            
            # Try to find wrapper parent
            try:
                parent = element.find_element(By.XPATH, './..')
                parent_class = parent.get_attribute('class') or ''
                if 'ant-checkbox-wrapper' in parent_class:
                    return parent
            except:
                pass
            
        except:
            pass
        return None
    
    @staticmethod
    def _extract_label_text(element: WebElement, checkbox_input: Optional[WebElement] = None) -> Optional[str]:
        """Extract label text from checkbox element"""
        try:
            # Try to find label element
            if checkbox_input:
                try:
                    # Find associated label via 'for' attribute
                    checkbox_id = checkbox_input.get_attribute('id')
                    if checkbox_id:
                        from selenium.webdriver.common.by import By
                        label = element.find_element(By.XPATH, f'//label[@for="{checkbox_id}"]')
                        if label:
                            return label.text.strip()
                except:
                    pass
            
            # Try to find label in wrapper
            wrapper = CheckboxIdentifier._find_checkbox_wrapper(element)
            if wrapper:
                try:
                    # Label is usually a sibling or child
                    label = wrapper.find_element(By.CSS_SELECTOR, 'label, span:not(.ant-checkbox), span.ant-checkbox-wrapper + span')
                    if label:
                        label_text = label.text.strip()
                        if label_text:
                            return label_text
                except:
                    pass
                
                # Get text from wrapper (excluding checkbox input text)
                wrapper_text = wrapper.text.strip()
                if wrapper_text:
                    return wrapper_text
            
            # Get text from element itself
            element_text = element.text.strip()
            if element_text:
                return element_text
            
            # Try aria-label
            aria_label = element.get_attribute('aria-label')
            if aria_label:
                return aria_label
            
            if checkbox_input:
                aria_label = checkbox_input.get_attribute('aria-label')
                if aria_label:
                    return aria_label
            
        except:
            pass
        return None
    
    @staticmethod
    def _determine_checkbox_type(element: WebElement, classes: List[str], checkbox_info: Dict) -> str:
        """Determine the checkbox type"""
        try:
            # Check for indeterminate
            if checkbox_info['indeterminate']:
                return 'indeterminate'
            
            # Check for disabled
            if checkbox_info['disabled']:
                return 'disabled'
            
            # Check for controlled (if we can determine)
            if checkbox_info['controlled'] is True:
                return 'controlled'
            
            # Check for "Check All" behavior
            if checkbox_info['has_check_all']:
                return 'check_all'
            
            # Check if part of a group
            if checkbox_info['group_name'] or checkbox_info['group_id']:
                # Check if grid layout (checkbox group with grid class)
                try:
                    group = CheckboxIdentifier._find_checkbox_group(element)
                    if group:
                        group_class = group.get_attribute('class') or ''
                        if 'ant-checkbox-group' in group_class:
                            # Check for grid layout indicators
                            if 'grid' in group_class.lower() or 'ant-col' in group_class:
                                return 'grid_layout'
                            return 'group'
                except:
                    pass
                return 'group'
            
            # Default to basic
            return 'basic'
            
        except:
            return 'basic'
    
    @staticmethod
    def _get_group_info(element: WebElement, checkbox_input: Optional[WebElement] = None) -> Dict[str, any]:
        """Get checkbox group information"""
        group_info = {
            'group_name': None,
            'group_id': None,
            'total_in_group': None,
            'checked_in_group': None
        }
        
        try:
            # Get name from checkbox input
            if checkbox_input:
                group_name = checkbox_input.get_attribute('name')
                if group_name:
                    group_info['group_name'] = group_name
            
            # Find checkbox group container
            group = CheckboxIdentifier._find_checkbox_group(element)
            if group:
                # Get group identifier
                group_id_attr = group.get_attribute('data-attr-id') or group.get_attribute('data-atr-id')
                if group_id_attr:
                    group_info['group_id'] = group_id_attr
                
                # Count total checkboxes in group
                try:
                    checkboxes_in_group = group.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"], .ant-checkbox-wrapper input[type="checkbox"]')
                    group_info['total_in_group'] = len(checkboxes_in_group)
                except:
                    pass
                
                # Find checked checkboxes in group
                try:
                    checked_checkboxes = group.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]:checked, .ant-checkbox-checked input[type="checkbox"]')
                    checked_labels = []
                    for checked_cb in checked_checkboxes:
                        try:
                            checked_wrapper = checked_cb.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-wrapper")][1]')
                            label_text = CheckboxIdentifier._extract_label_text(checked_wrapper, checked_cb)
                            if label_text:
                                checked_labels.append(label_text)
                            else:
                                checked_labels.append(checked_cb.get_attribute('value') or 'Checked')
                        except:
                            pass
                    if checked_labels:
                        group_info['checked_in_group'] = checked_labels
                except:
                    pass
            
        except:
            pass
        
        return group_info
    
    @staticmethod
    def _find_checkbox_group(element: WebElement) -> Optional[WebElement]:
        """Find the checkbox group container"""
        try:
            # Check if element itself is group
            class_attr = element.get_attribute('class') or ''
            if 'ant-checkbox-group' in class_attr:
                return element
            
            # Try to find group ancestor
            try:
                group = element.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-group")][1]')
                return group
            except:
                pass
            
            # Try to find via fieldset
            try:
                fieldset = element.find_element(By.XPATH, './ancestor::fieldset[1]')
                if fieldset:
                    return fieldset
            except:
                pass
            
        except:
            pass
        return None
    
    @staticmethod
    def _has_check_all_behavior(element: WebElement, checkbox_info: Dict) -> bool:
        """Check if checkbox has "Check All" behavior"""
        try:
            # Check label text for "Check All", "Select All", etc.
            label_text = checkbox_info.get('label_text', '').lower()
            check_all_keywords = ['check all', 'select all', 'all', '全选']
            if any(keyword in label_text for keyword in check_all_keywords):
                return True
            
            # Check if checkbox is in a group and has special behavior
            group = CheckboxIdentifier._find_checkbox_group(element)
            if group:
                # Check if this checkbox controls all others in the group
                try:
                    # Find all checkboxes in group
                    all_checkboxes = group.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
                    if len(all_checkboxes) > 1:
                        # Check if this is the first checkbox and has special attributes
                        checkbox_input = CheckboxIdentifier._find_checkbox_input(element)
                        if checkbox_input and checkbox_input == all_checkboxes[0]:
                            # Check for data attributes or classes indicating "Check All"
                            data_check_all = element.get_attribute('data-check-all')
                            if data_check_all and data_check_all.lower() == 'true':
                                return True
                except:
                    pass
            
        except:
            pass
        return False
    
    @staticmethod
    def is_checkbox_element(element: WebElement) -> bool:
        """
        Check if an element is an Ant Design Checkbox component
        
        Args:
            element: WebElement to check
            
        Returns:
            True if element is a checkbox, False otherwise
        """
        try:
            # Check if it's an input[type="checkbox"]
            if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'checkbox':
                return True
            
            class_attr = element.get_attribute('class') or ''
            
            # Check for ant-checkbox classes
            if any(cls in class_attr for cls in ['ant-checkbox', 'ant-checkbox-wrapper', 'ant-checkbox-group']):
                return True
            
            # Check if element contains a checkbox
            try:
                checkbox_child = element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"], .ant-checkbox, .ant-checkbox-wrapper')
                if checkbox_child:
                    return True
            except:
                pass
            
            return False
        except:
            return False

