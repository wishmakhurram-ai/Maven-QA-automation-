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
    def identify_checkbox_type(element: WebElement, fast_mode: bool = False) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design Checkbox
        Optimized version with fast mode for bulk operations
        
        Args:
            element: WebElement representing the checkbox
            fast_mode: If True, skip expensive operations (group info, check all detection)
            
        Returns:
            Dictionary containing checkbox properties
        """
        checkbox_info = {
            'type': 'basic',
            'checked': False,
            'disabled': False,
            'indeterminate': False,
            'label_text': None,
            'data_attr_id': None,
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
            'metadata': {}
        }
        
        try:
            # Fast path: Use JavaScript to batch read all attributes at once
            try:
                # Get driver from element (optimized - single attempt)
                driver = getattr(element, '_parent', None)
                if not driver or not hasattr(driver, 'execute_script'):
                    driver = None
                
                if driver:
                    # Optimized batch read attributes via JavaScript (single execution, all data)
                    attrs = driver.execute_script("""
                        var e=arguments[0],i=e;
                        if(e.tagName!=='INPUT'||e.type!=='checkbox'){
                            i=e.querySelector('input[type="checkbox"]')||e.closest('.ant-checkbox-wrapper')?.querySelector('input[type="checkbox"]')||e;
                        }
                        var w=e.closest('.ant-checkbox-wrapper')||e,ec=e.className||'',wc=w.className||'',c=ec+' '+wc;
                        var g=e.closest('.ant-checkbox-group'),gi=null;
                        if(g){
                            var gc=g.className||'',p=g.parentElement,pc=p?p.className||'':'';
                            gi={exists:true,isGrid:gc.includes('ant-col')||gc.toLowerCase().includes('grid')||pc.includes('ant-row')||pc.includes('ant-col')||g.querySelector('.ant-col,.ant-row')!==null,totalInGroup:(g.querySelectorAll('input[type="checkbox"]')||[]).length,groupId:g.getAttribute('data-attr-id')||g.getAttribute('data-atr-id')||''};
                        }
                        var t=(w!==e?(w.innerText||w.textContent||''):(e.innerText||e.textContent||'')).trim();
                        return {tagName:e.tagName.toLowerCase(),isInput:e.tagName==='INPUT'&&e.type==='checkbox',hasInput:i&&i.tagName==='INPUT',classes:c,checked:i?i.checked:false,disabled:i?(i.disabled||i.hasAttribute('disabled')):false,indeterminate:i?i.indeterminate:false,value:i?(i.value||''):'',name:i?(i.name||''):'',ariaChecked:i?(i.getAttribute('aria-checked')||''):'',ariaDisabled:i?(i.getAttribute('aria-disabled')||''):'',ariaLabel:i?(i.getAttribute('aria-label')||''):(e.getAttribute('aria-label')||''),dataAttrId:e.getAttribute('data-attr-id')||e.getAttribute('data-atr-id')||'',text:t,group:gi};
                    """, element)
                    
                    # Populate from JavaScript results (fast) - with comprehensive null safety
                    if not isinstance(attrs, dict):
                        raise ValueError("JavaScript returned invalid data")
                    
                    # Safe class extraction
                    classes_str = attrs.get('classes', '') or ''
                    classes = classes_str.split() if isinstance(classes_str, str) and classes_str else []
                    
                    # Safe boolean extraction with defaults
                    checkbox_info['checked'] = bool(attrs.get('checked', False))
                    checkbox_info['disabled'] = bool(attrs.get('disabled', False))
                    checkbox_info['indeterminate'] = bool(attrs.get('indeterminate', False))
                    
                    # Safe attribute extraction (only set if value exists and is not empty)
                    value = attrs.get('value', '')
                    checkbox_info['value'] = value if value else None
                    
                    name = attrs.get('name', '')
                    checkbox_info['name'] = name if name else None
                    
                    aria_checked = attrs.get('ariaChecked', '')
                    checkbox_info['aria_checked'] = aria_checked if aria_checked else None
                    
                    aria_disabled = attrs.get('ariaDisabled', '')
                    checkbox_info['aria_disabled'] = aria_disabled if aria_disabled else None
                    
                    aria_label = attrs.get('ariaLabel', '')
                    checkbox_info['aria_label'] = aria_label if aria_label else None
                    
                    data_attr_id = attrs.get('dataAttrId', '')
                    checkbox_info['data_attr_id'] = data_attr_id if data_attr_id else None
                    
                    # Improved label extraction from text - optimized
                    text = attrs.get('text', '') if attrs else ''
                    if text and isinstance(text, str) and text.strip():
                        # Clean up text - remove checkbox-related words and whitespace
                        cleaned_text = text.replace('Checkbox', '').replace('checkbox', '').strip()
                        # Remove empty strings and very short meaningless text
                        if cleaned_text and 0 < len(cleaned_text) < 100:
                            # Remove common prefixes/suffixes
                            cleaned_text = cleaned_text.strip(' -•·')
                            if cleaned_text:
                                checkbox_info['label_text'] = cleaned_text
                    
                    # Fallback to aria-label if text extraction failed
                    if not checkbox_info['label_text'] and checkbox_info.get('aria_label'):
                        checkbox_info['label_text'] = checkbox_info['aria_label']
                    
                    # Final fallback to value if available
                    if not checkbox_info['label_text'] and checkbox_info.get('value'):
                        checkbox_info['label_text'] = checkbox_info['value']
                    
                    # Check classes for state
                    if 'ant-checkbox-checked' in classes:
                        checkbox_info['checked'] = True
                    if 'ant-checkbox-disabled' in classes:
                        checkbox_info['disabled'] = True
                    if 'ant-checkbox-indeterminate' in classes:
                        checkbox_info['indeterminate'] = True
                    
                    # Use aria-checked as source of truth
                    if checkbox_info['aria_checked']:
                        aria_checked = checkbox_info['aria_checked'].lower()
                        if aria_checked == 'true':
                            checkbox_info['checked'] = True
                        elif aria_checked == 'false':
                            checkbox_info['checked'] = False
                        elif aria_checked == 'mixed':
                            checkbox_info['indeterminate'] = True
                            checkbox_info['checked'] = False
                    
                    # Quick check for "Check All" from label
                    if checkbox_info['label_text']:
                        label_lower = checkbox_info['label_text'].lower()
                        if any(kw in label_lower for kw in ['check all', 'select all', 'all', '全选']):
                            checkbox_info['has_check_all'] = True
                    
                    # Determine type quickly
                    if checkbox_info['indeterminate']:
                        checkbox_info['type'] = 'indeterminate'
                    elif checkbox_info['disabled']:
                        checkbox_info['type'] = 'disabled'
                    elif checkbox_info['has_check_all']:
                        checkbox_info['type'] = 'check_all'
                    elif checkbox_info['name']:
                        checkbox_info['type'] = 'group'
                        checkbox_info['group_name'] = checkbox_info['name']
                    else:
                        checkbox_info['type'] = 'basic'
                    
                    # Use group info from JavaScript (already computed) - with safe extraction
                    group_info = attrs.get('group')
                    if group_info and isinstance(group_info, dict) and group_info.get('exists'):
                        group_id = group_info.get('groupId', '')
                        checkbox_info['group_id'] = group_id if group_id else None
                        
                        total_in_group = group_info.get('totalInGroup')
                        if total_in_group is not None:
                            try:
                                checkbox_info['total_in_group'] = int(total_in_group)
                            except (ValueError, TypeError):
                                checkbox_info['total_in_group'] = None
                        else:
                            checkbox_info['total_in_group'] = None
                        
                        # Mark as group or grid_layout
                        if group_info.get('isGrid'):
                            checkbox_info['type'] = 'grid_layout'
                        elif checkbox_info['name'] or checkbox_info['group_id']:
                            checkbox_info['type'] = 'group'
                        
                        # Use a generic group identifier if not already set
                        if not checkbox_info['group_name']:
                            checkbox_info['group_name'] = checkbox_info['name'] or 'checkbox-group'
                    
                    # Skip expensive operations in fast mode
                    if not fast_mode:
                        # Only do expensive operations if needed
                        if checkbox_info['name']:
                            # Quick group name from name attribute
                            checkbox_info['group_name'] = checkbox_info['name']
                        
                        # Try to get better label if not found
                        if not checkbox_info['label_text']:
                            checkbox_info['label_text'] = checkbox_info.get('aria_label')
                    
            except Exception as js_error:
                # Fallback to original method if JavaScript fails
                # Get class attribute
                class_attr = element.get_attribute('class') or ''
                classes = class_attr.split()
                
                # Quick data-attr-id
                checkbox_info['data_attr_id'] = element.get_attribute('data-attr-id') or element.get_attribute('data-atr-id')
                
                # Find the actual checkbox input element (simplified)
                checkbox_input = None
                try:
                    if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'checkbox':
                        checkbox_input = element
                    else:
                        checkbox_input = element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                except:
                    pass
                
                if checkbox_input:
                    checkbox_info['checked'] = checkbox_input.is_selected()
                    checkbox_info['disabled'] = not checkbox_input.is_enabled()
                    checkbox_info['value'] = checkbox_input.get_attribute('value')
                    checkbox_info['name'] = checkbox_input.get_attribute('name')
                    checkbox_info['aria_checked'] = checkbox_input.get_attribute('aria-checked')
                    checkbox_info['aria_label'] = checkbox_input.get_attribute('aria-label')
                    
                    # Quick indeterminate check
                    try:
                        if checkbox_input.get_property('indeterminate'):
                            checkbox_info['indeterminate'] = True
                    except:
                        pass
                
                # Check classes
                if 'ant-checkbox-checked' in classes:
                    checkbox_info['checked'] = True
                if 'ant-checkbox-disabled' in classes:
                    checkbox_info['disabled'] = True
                if 'ant-checkbox-indeterminate' in classes:
                    checkbox_info['indeterminate'] = True
                
                # Quick label from text - optimized
                try:
                    text = element.text.strip()
                    if text and 0 < len(text) < 100:
                        # Clean up text
                        cleaned = text.replace('Checkbox', '').replace('checkbox', '').strip(' -•·')
                        if cleaned:
                            checkbox_info['label_text'] = cleaned
                except:
                    pass
                
                # Fallback chain: aria-label -> value -> None
                if not checkbox_info['label_text']:
                    checkbox_info['label_text'] = checkbox_info.get('aria_label') or checkbox_info.get('value')
                
                # Determine type
                if checkbox_info['indeterminate']:
                    checkbox_info['type'] = 'indeterminate'
                elif checkbox_info['disabled']:
                    checkbox_info['type'] = 'disabled'
                elif checkbox_info['name']:
                    checkbox_info['type'] = 'group'
                    checkbox_info['group_name'] = checkbox_info['name']
                else:
                    checkbox_info['type'] = 'basic'
            
        except Exception as e:
            # Silent fail - return basic info
            pass
        
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

