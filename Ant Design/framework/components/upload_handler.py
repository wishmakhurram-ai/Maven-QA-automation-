"""
Upload Handler - Handles interactions with Ant Design Upload components
Single Responsibility: Upload files, interact with upload components, manage upload state
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from typing import Optional, List, Dict
from framework.base.base_page import BasePage
from framework.components.upload_locator import UploadLocator
from framework.components.upload_identifier import UploadIdentifier
from framework.context.element_context import ElementContext
import os
import time


class UploadHandler(BasePage):
    """
    Generic handler for Ant Design Upload component interactions
    Single Responsibility: Handle file uploads and upload component interactions
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Upload Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = UploadLocator(driver)
        self.identifier = UploadIdentifier()
        self.context = context
    
    def upload_file(self, upload_label: str, file_path: str, timeout: int = 10) -> bool:
        """
        Upload a single file to an upload component identified by label
        
        Args:
            upload_label: Label/identifier for upload component (e.g., "Profile Photo Upload")
            file_path: Path to file to upload
            timeout: Maximum wait time
            
        Returns:
            True if upload successful
        """
        try:
            # Find upload component
            upload = self.locator.find_upload_by_label(upload_label, timeout)
            if not upload:
                print(f"Upload component '{upload_label}' not found")
                return False
            
            # Check if disabled
            upload_info = self.identifier.identify_upload(upload)
            if upload_info['disabled']:
                print(f"Upload component '{upload_label}' is disabled")
                return False
            
            # Check max count
            if upload_info['max_count'] and upload_info['current_count'] >= upload_info['max_count']:
                print(f"Upload component '{upload_label}' has reached max count ({upload_info['max_count']})")
                return False
            
            # Verify file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            # Get absolute path
            abs_file_path = os.path.abspath(file_path)
            
            # Find file input (may be hidden, that's OK)
            try:
                file_input = upload.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            except:
                # Try to find in parent elements
                try:
                    file_input = upload.find_element(By.XPATH, './/ancestor::*//input[@type="file"]')
                except:
                    print(f"File input not found in upload component")
                    return False
            
            # Scroll upload into view first
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload)
                time.sleep(0.3)
            except:
                pass
            
            # Upload file (send_keys works even if input is hidden)
            file_input.send_keys(abs_file_path)
            
            # Wait for upload to process
            time.sleep(1.5)
            
            print(f"Uploaded file '{abs_file_path}' to '{upload_label}'")
            return True
            
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return False
    
    def upload_multiple_files(self, upload_label: str, file_paths: List[str], timeout: int = 10) -> bool:
        """
        Upload multiple files to an upload component
        
        Args:
            upload_label: Label/identifier for upload component
            file_paths: List of file paths to upload
            timeout: Maximum wait time
            
        Returns:
            True if all uploads successful
        """
        try:
            # Find upload component
            upload = self.locator.find_upload_by_label(upload_label, timeout)
            if not upload:
                print(f"Upload component '{upload_label}' not found")
                return False
            
            # Check if multiple upload is supported
            upload_info = self.identifier.identify_upload(upload)
            if not upload_info['multiple']:
                print(f"Upload component '{upload_label}' does not support multiple files")
                return False
            
            # Check max count
            if upload_info['max_count']:
                remaining = upload_info['max_count'] - upload_info['current_count']
                if len(file_paths) > remaining:
                    print(f"Too many files. Max: {upload_info['max_count']}, Current: {upload_info['current_count']}, Trying to upload: {len(file_paths)}")
                    file_paths = file_paths[:remaining]
            
            # Verify all files exist
            abs_paths = []
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    return False
                abs_paths.append(os.path.abspath(file_path))
            
            # Find file input
            file_input = upload.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            
            # Upload all files (separate by newline for multiple)
            file_input.send_keys('\n'.join(abs_paths))
            
            # Wait for uploads to process
            time.sleep(2)
            
            print(f"Uploaded {len(abs_paths)} files to '{upload_label}'")
            return True
            
        except Exception as e:
            print(f"Error uploading multiple files: {str(e)}")
            return False
    
    def drag_and_drop_upload(self, upload_label: str, file_path: str, timeout: int = 10) -> bool:
        """
        Upload file using drag and drop to dragger zone
        
        Args:
            upload_label: Label/identifier for upload component
            file_path: Path to file to upload
            timeout: Maximum wait time
            
        Returns:
            True if upload successful
        """
        try:
            # Find upload component
            upload = self.locator.find_upload_by_label(upload_label, timeout)
            if not upload:
                print(f"Upload component '{upload_label}' not found")
                return False
            
            # Check if it's a dragger
            upload_info = self.identifier.identify_upload(upload)
            if upload_info['type'] != 'dragger':
                # Fallback to regular upload
                return self.upload_file(upload_label, file_path, timeout)
            
            # Verify file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            abs_file_path = os.path.abspath(file_path)
            
            # Find dragger zone
            dragger_zone = upload.find_element(By.CSS_SELECTOR, 
                '.ant-upload-drag, .ant-upload-drag-container')
            
            # Find file input
            file_input = upload.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            
            # Simulate drag and drop
            actions = ActionChains(self.driver)
            
            # Drag enter
            actions.move_to_element(dragger_zone)
            actions.pause(0.2)
            
            # Drag over
            actions.move_to_element(dragger_zone)
            actions.pause(0.2)
            
            # Drop (send keys to file input)
            actions.move_to_element(file_input)
            actions.pause(0.2)
            
            actions.perform()
            
            # Send file to input
            file_input.send_keys(abs_file_path)
            
            # Wait for upload
            time.sleep(1)
            
            print(f"Drag and drop uploaded file '{abs_file_path}' to '{upload_label}'")
            return True
            
        except Exception as e:
            print(f"Error in drag and drop upload: {str(e)}")
            return False
    
    def click_picture_card_upload(self, upload_label: str, timeout: int = 10) -> Optional[WebElement]:
        """
        Click picture-card upload to open file selection
        
        Args:
            upload_label: Label/identifier for upload component
            timeout: Maximum wait time
            
        Returns:
            Picture card element if found
        """
        try:
            # Find upload component
            upload = self.locator.find_upload_by_label(upload_label, timeout)
            if not upload:
                print(f"Upload component '{upload_label}' not found")
                return None
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload)
            time.sleep(0.3)
            
            # Find picture card
            try:
                picture_card = upload.find_element(By.CSS_SELECTOR, 
                    '.ant-upload-select-picture-card, [class*="picture-card"]')
            except:
                # Try finding by upload text or icon
                picture_card = upload.find_element(By.CSS_SELECTOR, 
                    '.ant-upload-select, button, [role="button"]')
            
            # Click it
            try:
                picture_card.click()
            except:
                # Use JavaScript click if normal click fails
                self.driver.execute_script("arguments[0].click();", picture_card)
            
            time.sleep(0.5)
            print(f"Clicked picture-card upload '{upload_label}'")
            return picture_card
            
        except Exception as e:
            print(f"Error clicking picture-card: {str(e)}")
            return None
    
    def click_upload_button(self, upload_element: WebElement) -> bool:
        """
        Click any upload button/area to open file selection
        
        Args:
            upload_element: Upload container WebElement
            
        Returns:
            True if clicked successfully
        """
        try:
            upload_info = self.identifier.identify_upload(upload_element)
            upload_type = upload_info['type']
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_element)
            time.sleep(0.3)
            
            # Click based on upload type
            if upload_type == 'picture-card':
                try:
                    picture_card = upload_element.find_element(By.CSS_SELECTOR, 
                        '.ant-upload-select-picture-card, [class*="picture-card"]')
                    picture_card.click()
                    return True
                except:
                    pass
            
            elif upload_type == 'dragger':
                try:
                    dragger_zone = upload_element.find_element(By.CSS_SELECTOR, 
                        '.ant-upload-drag, .ant-upload-drag-container')
                    dragger_zone.click()
                    return True
                except:
                    pass
            
            # Try to find and click button
            try:
                button = upload_element.find_element(By.CSS_SELECTOR, 
                    'button, .ant-upload-select, [role="button"], .ant-btn, .ant-upload-btn')
                button.click()
                return True
            except:
                pass
            
            # Last resort: click the upload container itself
            try:
                upload_element.click()
                return True
            except:
                # Use JavaScript click
                self.driver.execute_script("arguments[0].click();", upload_element)
                return True
                
        except Exception as e:
            return False
    
    def delete_uploaded_file(self, upload_label: str, file_name: str, timeout: int = 10) -> bool:
        """
        Delete an uploaded file from upload list
        
        Args:
            upload_label: Label/identifier for upload component
            file_name: Name of file to delete
            timeout: Maximum wait time
            
        Returns:
            True if deletion successful
        """
        try:
            # Find upload component
            upload = self.locator.find_upload_by_label(upload_label, timeout)
            if not upload:
                print(f"Upload component '{upload_label}' not found")
                return False
            
            # Get uploaded items
            upload_info = self.identifier.identify_upload(upload)
            items = upload_info['uploaded_items']
            
            # Find item with matching file name
            target_item = None
            for item in items:
                if file_name.lower() in item['name'].lower() or item['name'].lower() in file_name.lower():
                    target_item = item
                    break
            
            if not target_item:
                print(f"File '{file_name}' not found in upload list")
                return False
            
            # Find delete button
            try:
                delete_btn = target_item['element'].find_element(By.CSS_SELECTOR, 
                    '.ant-upload-list-item-card-actions-btn, [class*="delete"], [aria-label*="delete" i]')
                delete_btn.click()
                time.sleep(0.5)
                print(f"Deleted file '{file_name}' from '{upload_label}'")
                return True
            except:
                print(f"Delete button not found for file '{file_name}'")
                return False
                
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    def get_uploaded_files(self, upload_label: str, timeout: int = 10) -> List[str]:
        """
        Get list of uploaded file names
        
        Args:
            upload_label: Label/identifier for upload component
            timeout: Maximum wait time
            
        Returns:
            List of file names
        """
        try:
            # Find upload component
            upload = self.locator.find_upload_by_label(upload_label, timeout)
            if not upload:
                return []
            
            # Get uploaded items
            upload_info = self.identifier.identify_upload(upload)
            return [item['name'] for item in upload_info['uploaded_items']]
            
        except Exception as e:
            print(f"Error getting uploaded files: {str(e)}")
            return []
    
    def get_upload_count(self, upload_label: str, timeout: int = 10) -> int:
        """
        Get current number of uploaded files
        
        Args:
            upload_label: Label/identifier for upload component
            timeout: Maximum wait time
            
        Returns:
            Number of uploaded files
        """
        try:
            # Find upload component
            upload = self.locator.find_upload_by_label(upload_label, timeout)
            if not upload:
                return 0
            
            # Get upload info
            upload_info = self.identifier.identify_upload(upload)
            return upload_info['current_count']
            
        except Exception as e:
            return 0
    
    def print_upload_summary(self, upload_label: Optional[str] = None) -> None:
        """
        Print summary of upload component(s)
        
        Args:
            upload_label: Optional specific upload label, or None for all uploads
        """
        if upload_label:
            uploads = [self.locator.find_upload_by_label(upload_label)]
            uploads = [u for u in uploads if u is not None]
        else:
            uploads = self.locator.find_all_uploads()
        
        print(f"\n{'='*80}")
        print(f"UPLOAD COMPONENT SUMMARY")
        print(f"{'='*80}")
        print(f"Found {len(uploads)} upload component(s)\n")
        
        for idx, upload in enumerate(uploads, 1):
            try:
                info = self.identifier.identify_upload(upload)
                
                print(f"[{idx}] Upload Component")
                print(f"  Type: {info['type']}")
                print(f"  List Type: {info['list_type']}")
                print(f"  Multiple: {info['multiple']}")
                print(f"  Directory: {info['directory']}")
                print(f"  Disabled: {info['disabled']}")
                print(f"  Max Count: {info['max_count'] or 'Unlimited'}")
                print(f"  Current Count: {info['current_count']}")
                print(f"  Custom Button: {info['has_custom_button']}")
                print(f"  Icon Only: {info['has_icon_only']}")
                print(f"  Upload Text: {info['upload_text']}")
                print(f"  Data-attr-id: {info['data_attr_id'] or 'None'}")
                print(f"  Aria-label: {info['aria_label'] or 'None'}")
                
                if info['uploaded_items']:
                    print(f"  Uploaded Files ({len(info['uploaded_items'])}):")
                    for item in info['uploaded_items']:
                        print(f"    - {item['name']}")
                
                print()
                
            except Exception as e:
                print(f"[{idx}] Error analyzing upload: {str(e)}\n")
        
        print(f"{'='*80}\n")

