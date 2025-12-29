"""
Upload Identifier - Analyzes Ant Design Upload component properties
Single Responsibility: Extract and identify upload component properties and state
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional, List


class UploadIdentifier:
    """
    Identifies and analyzes Ant Design Upload component properties
    Extracts upload type, state, configuration, and behavior
    """
    
    def identify_upload(self, upload_element: WebElement) -> Dict:
        """
        Identify all properties of an upload component
        
        Args:
            upload_element: Upload container WebElement
            
        Returns:
            Dictionary with upload properties
        """
        try:
            # Get basic attributes
            class_attr = upload_element.get_attribute('class') or ''
            data_attr_id = upload_element.get_attribute('data-attr-id') or ''
            aria_label = upload_element.get_attribute('aria-label') or ''
            
            # Find file input
            file_input = None
            try:
                file_input = upload_element.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            except:
                pass
            
            # Determine upload type
            upload_type = self._identify_upload_type(upload_element, class_attr)
            
            # Check for multiple files
            is_multiple = self._is_multiple_upload(upload_element, file_input)
            
            # Check for directory upload
            is_directory = self._is_directory_upload(upload_element, file_input)
            
            # Determine list type
            list_type = self._identify_list_type(upload_element, class_attr)
            
            # Check disabled state
            is_disabled = self._is_disabled(upload_element, class_attr)
            
            # Get max count
            max_count = self._get_max_count(upload_element)
            
            # Get current file count
            current_count = self._get_current_file_count(upload_element)
            
            # Check for custom button
            has_custom_button = self._has_custom_button(upload_element)
            
            # Check for icon-only button
            has_icon_only = self._has_icon_only_button(upload_element)
            
            # Check drag-over state
            is_drag_over = 'ant-upload-drag-hover' in class_attr
            
            # Get upload text/instructions
            upload_text = self._get_upload_text(upload_element)
            
            # Get uploaded items
            uploaded_items = self._get_uploaded_items(upload_element)
            
            return {
                'type': upload_type,
                'list_type': list_type,
                'multiple': is_multiple,
                'directory': is_directory,
                'disabled': is_disabled,
                'max_count': max_count,
                'current_count': current_count,
                'has_custom_button': has_custom_button,
                'has_icon_only': has_icon_only,
                'is_drag_over': is_drag_over,
                'upload_text': upload_text,
                'data_attr_id': data_attr_id,
                'aria_label': aria_label,
                'class': class_attr,
                'uploaded_items': uploaded_items,
                'file_input': file_input is not None
            }
        except Exception as e:
            return {
                'type': 'unknown',
                'list_type': 'text',
                'multiple': False,
                'directory': False,
                'disabled': False,
                'max_count': None,
                'current_count': 0,
                'has_custom_button': False,
                'has_icon_only': False,
                'is_drag_over': False,
                'upload_text': '',
                'data_attr_id': '',
                'aria_label': '',
                'class': '',
                'uploaded_items': [],
                'file_input': False
            }
    
    def _identify_upload_type(self, upload: WebElement, class_attr: str) -> str:
        """
        Identify the type of upload component
        
        Returns:
            'button', 'dragger', 'picture-card', 'picture-list', 'custom', 'unknown'
        """
        try:
            # Check for dragger
            if 'ant-upload-drag' in class_attr or 'ant-upload-drag-container' in class_attr:
                return 'dragger'
            
            # Check for picture-card
            if 'ant-upload-select-picture-card' in class_attr:
                return 'picture-card'
            
            # Check for picture list
            if 'ant-upload-list-picture' in class_attr or 'ant-upload-list-picture-card' in class_attr:
                return 'picture-list'
            
            # Check for button
            if 'ant-upload-select' in class_attr:
                return 'button'
            
            # Check for custom button
            button_elements = upload.find_elements(By.CSS_SELECTOR, 
                'button, [role="button"], .ant-btn')
            if button_elements:
                return 'custom'
            
            return 'unknown'
        except:
            return 'unknown'
    
    def _identify_list_type(self, upload: WebElement, class_attr: str) -> str:
        """
        Identify the list type of upload
        
        Returns:
            'text', 'picture', 'picture-card'
        """
        try:
            if 'ant-upload-list-picture-card' in class_attr:
                return 'picture-card'
            elif 'ant-upload-list-picture' in class_attr:
                return 'picture'
            else:
                return 'text'
        except:
            return 'text'
    
    def _is_multiple_upload(self, upload: WebElement, file_input: Optional[WebElement]) -> bool:
        """Check if upload supports multiple files"""
        try:
            if file_input:
                multiple_attr = file_input.get_attribute('multiple')
                if multiple_attr is not None:
                    return True
            
            # Check class for multiple indicator
            class_attr = upload.get_attribute('class') or ''
            if 'multiple' in class_attr.lower():
                return True
            
            return False
        except:
            return False
    
    def _is_directory_upload(self, upload: WebElement, file_input: Optional[WebElement]) -> bool:
        """Check if upload supports directory upload"""
        try:
            if file_input:
                webkitdirectory = file_input.get_attribute('webkitdirectory')
                directory = file_input.get_attribute('directory')
                if webkitdirectory is not None or directory is not None:
                    return True
            
            class_attr = upload.get_attribute('class') or ''
            if 'directory' in class_attr.lower():
                return True
            
            return False
        except:
            return False
    
    def _is_disabled(self, upload: WebElement, class_attr: str) -> bool:
        """Check if upload is disabled"""
        try:
            if 'ant-upload-disabled' in class_attr:
                return True
            
            # Check file input
            try:
                file_input = upload.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                if not file_input.is_enabled():
                    return True
            except:
                pass
            
            # Check button
            try:
                button = upload.find_element(By.CSS_SELECTOR, 'button, [role="button"]')
                if 'disabled' in button.get_attribute('class') or '':
                    return True
            except:
                pass
            
            return False
        except:
            return False
    
    def _get_max_count(self, upload: WebElement) -> Optional[int]:
        """Get maximum file count from upload component"""
        try:
            # Check data attributes
            max_count_attr = upload.get_attribute('data-max-count')
            if max_count_attr:
                return int(max_count_attr)
            
            # Check aria attributes
            aria_max = upload.get_attribute('aria-max')
            if aria_max:
                return int(aria_max)
            
            # Check for maxCount in nearby elements
            try:
                parent = upload.find_element(By.XPATH, './..')
                max_count_attr = parent.get_attribute('data-max-count')
                if max_count_attr:
                    return int(max_count_attr)
            except:
                pass
            
            return None
        except:
            return None
    
    def _get_current_file_count(self, upload: WebElement) -> int:
        """Get current number of uploaded files"""
        try:
            items = self._get_uploaded_items(upload)
            return len(items)
        except:
            return 0
    
    def _has_custom_button(self, upload: WebElement) -> bool:
        """Check if upload has custom button"""
        try:
            buttons = upload.find_elements(By.CSS_SELECTOR, 
                'button, [role="button"], .ant-btn')
            if buttons:
                # Check if button is not the default ant-upload-select
                for button in buttons:
                    class_attr = button.get_attribute('class') or ''
                    if 'ant-upload-select' not in class_attr:
                        return True
            return False
        except:
            return False
    
    def _has_icon_only_button(self, upload: WebElement) -> bool:
        """Check if upload button is icon-only"""
        try:
            buttons = upload.find_elements(By.CSS_SELECTOR, 
                'button, [role="button"], .ant-upload-select')
            for button in buttons:
                text = button.text.strip()
                # Check for icons
                icons = button.find_elements(By.CSS_SELECTOR, 
                    '.anticon, [class*="icon"], svg')
                if icons and not text:
                    return True
            return False
        except:
            return False
    
    def _get_upload_text(self, upload: WebElement) -> str:
        """Get upload instruction text"""
        try:
            # Get text from upload area
            text_elements = upload.find_elements(By.CSS_SELECTOR, 
                '.ant-upload-text, .ant-upload-drag-text, .ant-upload-hint')
            if text_elements:
                return text_elements[0].text.strip()
            
            # Get text from button
            try:
                button = upload.find_element(By.CSS_SELECTOR, 
                    'button, [role="button"], .ant-upload-select')
                text = button.text.strip()
                if text:
                    return text
            except:
                pass
            
            # Get all text content
            text = upload.text.strip()
            return text
        except:
            return ''
    
    def _get_uploaded_items(self, upload: WebElement) -> List[Dict]:
        """Get list of uploaded file items"""
        items = []
        try:
            # Find upload list items
            list_items = upload.find_elements(By.CSS_SELECTOR, 
                '.ant-upload-list-item, [class*="ant-upload-list-item"]')
            
            for item in list_items:
                try:
                    # Get file name
                    name_elem = item.find_element(By.CSS_SELECTOR, 
                        '.ant-upload-list-item-name, [class*="name"]')
                    file_name = name_elem.text.strip()
                except:
                    file_name = item.text.strip()
                
                # Check for delete button
                try:
                    delete_btn = item.find_element(By.CSS_SELECTOR, 
                        '.ant-upload-list-item-card-actions-btn, [class*="delete"], [aria-label*="delete" i]')
                    has_delete = True
                except:
                    has_delete = False
                
                # Check for preview
                try:
                    preview_btn = item.find_element(By.CSS_SELECTOR, 
                        '[class*="preview"], [aria-label*="preview" i]')
                    has_preview = True
                except:
                    has_preview = False
                
                items.append({
                    'name': file_name,
                    'element': item,
                    'has_delete': has_delete,
                    'has_preview': has_preview
                })
        except:
            pass
        
        return items



