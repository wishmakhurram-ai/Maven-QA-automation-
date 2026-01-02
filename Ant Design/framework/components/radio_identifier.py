"""
Radio Identifier - Handles analyzing and identifying Ant Design Radio properties
Single Responsibility: Analyze radio elements and extract their properties
Detects all Ant Design radio types: Basic, Disabled, Controlled, Radio Group, Radio Button Style, Radio with Options/Grid Layout
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional, List
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class RadioIdentifier:
    """
    Handles identifying and analyzing Ant Design Radio component properties
    Single Responsibility: Extract radio state, disabled, label, group info, and other properties
    """
    
    # Ant Design radio class patterns
    RADIO_CLASSES = {
        'radio': 'ant-radio',
        'wrapper': 'ant-radio-wrapper',
        'group': 'ant-radio-group',
        'button_wrapper': 'ant-radio-button-wrapper',
        'disabled': 'ant-radio-disabled',
        'checked': 'ant-radio-checked',
        'button': 'ant-radio-button'
    }
    
    @staticmethod
    def identify_radio_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design Radio
        Integrates with GenericElementIdentifier to read custom attributes
        
        Args:
            element: WebElement representing the radio
            
        Returns:
            Dictionary containing radio properties:
            {
                'type': 'basic'|'disabled'|'controlled'|'group'|'button_style'|'grid_layout',
                'selected': bool,  # Selected/unselected state
                'disabled': bool,
                'label_text': str|None,
                'data_attr_id': str|None,
                'group_name': str|None,  # Radio group name (name attribute)
                'group_id': str|None,  # Radio group identifier
                'total_in_group': int|None,  # Total options in group
                'selected_in_group': str|None,  # Currently selected option in group
                'is_button_style': bool,
                'aria_checked': str|None,  # 'true'|'false'
                'aria_disabled': str|None,  # 'true'|'false'
                'aria_label': str|None,
                'value': str|None,  # Radio value
                'name': str|None,  # Radio name (for grouping)
                'controlled': bool|None,  # True if controlled, False if uncontrolled
                'metadata': dict
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        radio_info = {
            'type': 'basic',
            'selected': False,
            'disabled': False,
            'label_text': None,
            'data_attr_id': generic_info.get('data_attr_id'),
            'group_name': None,
            'group_id': None,
            'total_in_group': None,
            'selected_in_group': None,
            'is_button_style': False,
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
            
            # Check if this is a radio button style
            radio_info['is_button_style'] = (
                'ant-radio-button' in classes or
                'ant-radio-button-wrapper' in classes
            )
            
            # Find the actual radio input element
            radio_input = RadioIdentifier._find_radio_input(element)
            if not radio_input:
                # If element itself is input[type="radio"]
                if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'radio':
                    radio_input = element
                else:
                    # Try to find wrapper and then input
                    wrapper = RadioIdentifier._find_radio_wrapper(element)
                    if wrapper:
                        try:
                            radio_input = wrapper.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                        except:
                            pass
            
            if radio_input:
                # Get radio input properties
                radio_info['selected'] = radio_input.is_selected()
                radio_info['disabled'] = not radio_input.is_enabled() or radio_input.get_attribute('disabled') is not None
                radio_info['value'] = radio_input.get_attribute('value')
                radio_info['name'] = radio_input.get_attribute('name')
                radio_info['aria_checked'] = radio_input.get_attribute('aria-checked')
                radio_info['aria_disabled'] = radio_input.get_attribute('aria-disabled')
                radio_info['aria_label'] = radio_input.get_attribute('aria-label')
                
                # Check for checked state via class
                if 'ant-radio-checked' in classes:
                    radio_info['selected'] = True
                
                # Use aria-checked as source of truth if available
                if radio_info['aria_checked']:
                    radio_info['selected'] = radio_info['aria_checked'].lower() == 'true'
            
            # Check if disabled via class
            if 'ant-radio-disabled' in classes:
                radio_info['disabled'] = True
            
            # Get label text
            radio_info['label_text'] = RadioIdentifier._extract_label_text(element, radio_input)
            
            # Determine radio type
            radio_info['type'] = RadioIdentifier._determine_radio_type(element, classes, radio_info)
            
            # Get group information
            group_info = RadioIdentifier._get_group_info(element, radio_input)
            radio_info.update(group_info)
            
            # Determine if controlled
            if radio_input:
                has_checked_attr = radio_input.get_attribute('checked') is not None
                has_default_checked = radio_input.get_attribute('defaultChecked') is not None
                
                if has_checked_attr:
                    radio_info['controlled'] = True
                elif has_default_checked:
                    radio_info['controlled'] = False
                else:
                    # Try to infer from data attributes
                    data_controlled = element.get_attribute('data-controlled')
                    if data_controlled:
                        radio_info['controlled'] = data_controlled.lower() == 'true'
            
        except Exception as e:
            print(f"Error identifying radio type: {str(e)}")
        
        return radio_info
    
    @staticmethod
    def _find_radio_input(element: WebElement) -> Optional[WebElement]:
        """Find the actual radio input element"""
        try:
            # If element is already input[type="radio"]
            if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'radio':
                return element
            
            # Try to find input inside
            try:
                radio_input = element.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                return radio_input
            except:
                pass
            
            # Try to find in wrapper
            try:
                wrapper = element.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-radio-wrapper")][1]')
                radio_input = wrapper.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                return radio_input
            except:
                pass
            
        except:
            pass
        return None
    
    @staticmethod
    def _find_radio_wrapper(element: WebElement) -> Optional[WebElement]:
        """Find the radio wrapper element"""
        try:
            # Check if element itself is wrapper
            class_attr = element.get_attribute('class') or ''
            if 'ant-radio-wrapper' in class_attr:
                return element
            
            # Try to find wrapper ancestor
            try:
                wrapper = element.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-radio-wrapper")][1]')
                return wrapper
            except:
                pass
            
            # Try to find wrapper parent
            try:
                parent = element.find_element(By.XPATH, './..')
                parent_class = parent.get_attribute('class') or ''
                if 'ant-radio-wrapper' in parent_class:
                    return parent
            except:
                pass
            
        except:
            pass
        return None
    
    @staticmethod
    def _extract_label_text(element: WebElement, radio_input: Optional[WebElement] = None) -> Optional[str]:
        """Extract label text from radio element"""
        try:
            # Try to find label element
            if radio_input:
                try:
                    # Find associated label via 'for' attribute
                    radio_id = radio_input.get_attribute('id')
                    if radio_id:
                        from selenium.webdriver.common.by import By
                        label = element.find_element(By.XPATH, f'//label[@for="{radio_id}"]')
                        if label:
                            return label.text.strip()
                except:
                    pass
            
            # Try to find label in wrapper
            wrapper = RadioIdentifier._find_radio_wrapper(element)
            if wrapper:
                try:
                    # Label is usually a sibling or child
                    label = wrapper.find_element(By.CSS_SELECTOR, 'label, span.ant-radio + span, span:not(.ant-radio)')
                    if label:
                        label_text = label.text.strip()
                        if label_text:
                            return label_text
                except:
                    pass
                
                # Get text from wrapper (excluding radio input text)
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
            
            if radio_input:
                aria_label = radio_input.get_attribute('aria-label')
                if aria_label:
                    return aria_label
            
        except:
            pass
        return None
    
    @staticmethod
    def _determine_radio_type(element: WebElement, classes: List[str], radio_info: Dict) -> str:
        """Determine the radio type"""
        try:
            # Check for button style
            if radio_info['is_button_style']:
                return 'button_style'
            
            # Check for disabled
            if radio_info['disabled']:
                return 'disabled'
            
            # Check for controlled (if we can determine)
            if radio_info['controlled'] is True:
                return 'controlled'
            
            # Check if part of a group
            if radio_info['group_name'] or radio_info['group_id']:
                # Check if grid layout (radio group with grid class)
                try:
                    group = RadioIdentifier._find_radio_group(element)
                    if group:
                        group_class = group.get_attribute('class') or ''
                        if 'ant-radio-group' in group_class:
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
    def _get_group_info(element: WebElement, radio_input: Optional[WebElement] = None) -> Dict[str, any]:
        """Get radio group information"""
        group_info = {
            'group_name': None,
            'group_id': None,
            'total_in_group': None,
            'selected_in_group': None
        }
        
        try:
            # Get name from radio input
            if radio_input:
                group_name = radio_input.get_attribute('name')
                if group_name:
                    group_info['group_name'] = group_name
            
            # Find radio group container
            group = RadioIdentifier._find_radio_group(element)
            if group:
                # Get group identifier
                group_id_attr = group.get_attribute('data-attr-id') or group.get_attribute('data-atr-id')
                if group_id_attr:
                    group_info['group_id'] = group_id_attr
                
                # Count total radios in group
                try:
                    radios_in_group = group.find_elements(By.CSS_SELECTOR, 'input[type="radio"], .ant-radio-wrapper input[type="radio"]')
                    group_info['total_in_group'] = len(radios_in_group)
                except:
                    pass
                
                # Find selected radio in group
                try:
                    selected_radio = group.find_element(By.CSS_SELECTOR, 'input[type="radio"]:checked, .ant-radio-checked input[type="radio"]')
                    if selected_radio:
                        # Get label of selected radio
                        selected_wrapper = selected_radio.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-radio-wrapper")][1]')
                        if selected_wrapper:
                            label_text = RadioIdentifier._extract_label_text(selected_wrapper, selected_radio)
                            if label_text:
                                group_info['selected_in_group'] = label_text
                            else:
                                group_info['selected_in_group'] = selected_radio.get_attribute('value') or 'Selected'
                except:
                    pass
            
        except:
            pass
        
        return group_info
    
    @staticmethod
    def _find_radio_group(element: WebElement) -> Optional[WebElement]:
        """Find the radio group container"""
        try:
            # Check if element itself is group
            class_attr = element.get_attribute('class') or ''
            if 'ant-radio-group' in class_attr:
                return element
            
            # Try to find group ancestor
            try:
                group = element.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-radio-group")][1]')
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
    def is_radio_element(element: WebElement) -> bool:
        """
        Check if an element is an Ant Design Radio component
        
        Args:
            element: WebElement to check
            
        Returns:
            True if element is a radio, False otherwise
        """
        try:
            # Check if it's an input[type="radio"]
            if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'radio':
                return True
            
            class_attr = element.get_attribute('class') or ''
            
            # Check for ant-radio classes
            if any(cls in class_attr for cls in ['ant-radio', 'ant-radio-wrapper', 'ant-radio-group', 'ant-radio-button']):
                return True
            
            # Check if element contains a radio
            try:
                radio_child = element.find_element(By.CSS_SELECTOR, 'input[type="radio"], .ant-radio, .ant-radio-wrapper')
                if radio_child:
                    return True
            except:
                pass
            
            return False
        except:
            return False

