"""
Switch Identifier - Handles analyzing and identifying Ant Design Switch properties
Single Responsibility: Analyze switch elements and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class SwitchIdentifier:
    """
    Handles identifying and analyzing Ant Design Switch component properties
    Single Responsibility: Extract switch state, size, disabled, loading, and other properties
    """
    
    # Ant Design switch class patterns
    SWITCH_CLASSES = {
        'checked': 'ant-switch-checked',
        'disabled': 'ant-switch-disabled',
        'loading': 'ant-switch-loading',
        'small': 'ant-switch-small'
    }
    
    @staticmethod
    def identify_switch_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design Switch
        Integrates with GenericElementIdentifier to read custom attributes
        
        Args:
            element: WebElement representing the switch
            
        Returns:
            Dictionary containing switch properties:
            {
                'checked': bool,  # ON/OFF state
                'disabled': bool,
                'loading': bool,
                'size': 'default'|'small',
                'checked_label': str|None,  # Text shown when checked
                'unchecked_label': str|None,  # Text shown when unchecked
                'has_icon': bool,
                'data_attr_id': str|None,
                'application_type': str|None,
                'aria_checked': str|None,  # 'true'|'false'
                'aria_disabled': str|None,  # 'true'|'false'
                'role': str|None,  # Should be 'switch'
                'controlled': bool|None,  # True if controlled, False if uncontrolled, None if unknown
                'metadata': dict
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        switch_info = {
            'checked': False,
            'disabled': False,
            'loading': False,
            'size': 'default',
            'checked_label': None,
            'unchecked_label': None,
            'has_icon': False,
            'data_attr_id': generic_info.get('data_attr_id'),
            'application_type': generic_info.get('application_type'),
            'aria_checked': None,
            'aria_disabled': None,
            'role': None,
            'controlled': None,
            'metadata': generic_info.get('metadata', {})
        }
        
        try:
            # Get class attribute
            class_attr = element.get_attribute('class') or ''
            classes = class_attr.split()
            
            # Check if checked (ON state)
            switch_info['checked'] = 'ant-switch-checked' in classes
            
            # Check if disabled
            switch_info['disabled'] = 'ant-switch-disabled' in classes
            
            # Check if loading
            switch_info['loading'] = 'ant-switch-loading' in classes
            
            # Check size
            if 'ant-switch-small' in classes:
                switch_info['size'] = 'small'
            else:
                switch_info['size'] = 'default'
            
            # Get aria attributes
            switch_info['aria_checked'] = element.get_attribute('aria-checked')
            switch_info['aria_disabled'] = element.get_attribute('aria-disabled')
            switch_info['role'] = element.get_attribute('role')
            
            # Verify role is switch
            if switch_info['role'] != 'switch':
                # Try to find switch element inside if current element is wrapper
                try:
                    switch_element = element.find_element(By.CSS_SELECTOR, '[role="switch"]')
                    if switch_element:
                        switch_info['aria_checked'] = switch_element.get_attribute('aria-checked')
                        switch_info['aria_disabled'] = switch_element.get_attribute('aria-disabled')
                        switch_info['role'] = switch_element.get_attribute('role')
                except:
                    pass
            
            # Get checked/unchecked labels
            try:
                # Ant Design switches can have labels inside
                inner_elements = element.find_elements(By.CSS_SELECTOR, '.ant-switch-inner, .ant-switch-inner-checked, .ant-switch-inner-unchecked')
                if inner_elements:
                    for inner in inner_elements:
                        inner_text = inner.text.strip()
                        inner_class = inner.get_attribute('class') or ''
                        if 'checked' in inner_class and inner_text:
                            switch_info['checked_label'] = inner_text
                        elif 'unchecked' in inner_class and inner_text:
                            switch_info['unchecked_label'] = inner_text
                
                # Also check for text nodes or direct children
                if not switch_info['checked_label'] and not switch_info['unchecked_label']:
                    # Try to get text from element itself
                    element_text = element.text.strip()
                    if element_text:
                        # If checked, this might be the checked label
                        if switch_info['checked']:
                            switch_info['checked_label'] = element_text
                        else:
                            switch_info['unchecked_label'] = element_text
            except:
                pass
            
            # Check for icons
            try:
                icon_elements = element.find_elements(By.CSS_SELECTOR, '.anticon, [class*="icon"]')
                switch_info['has_icon'] = len(icon_elements) > 0
            except:
                switch_info['has_icon'] = False
            
            # Determine if controlled or uncontrolled
            # Controlled switches have explicit checked prop, uncontrolled use defaultChecked
            # We can infer this from the presence of data attributes or React props
            try:
                # Check for React props (if available via JavaScript)
                has_checked_attr = element.get_attribute('checked') is not None
                has_default_checked = element.get_attribute('defaultChecked') is not None
                
                if has_checked_attr:
                    switch_info['controlled'] = True
                elif has_default_checked:
                    switch_info['controlled'] = False
                else:
                    # Try to infer from data attributes
                    data_controlled = element.get_attribute('data-controlled')
                    if data_controlled:
                        switch_info['controlled'] = data_controlled.lower() == 'true'
            except:
                pass
            
            # If aria-checked is available, use it as source of truth for checked state
            if switch_info['aria_checked']:
                switch_info['checked'] = switch_info['aria_checked'].lower() == 'true'
            
        except Exception as e:
            print(f"Error identifying switch type: {str(e)}")
        
        return switch_info
    
    @staticmethod
    def is_switch_element(element: WebElement) -> bool:
        """
        Check if an element is an Ant Design Switch component
        
        Args:
            element: WebElement to check
            
        Returns:
            True if element is a switch, False otherwise
        """
        try:
            class_attr = element.get_attribute('class') or ''
            role = element.get_attribute('role')
            
            # Check for ant-switch class
            if 'ant-switch' in class_attr:
                return True
            
            # Check for role="switch"
            if role == 'switch':
                return True
            
            # Check if element contains a switch
            try:
                switch_child = element.find_element(By.CSS_SELECTOR, '.ant-switch, [role="switch"]')
                if switch_child:
                    return True
            except:
                pass
            
            return False
        except:
            return False




