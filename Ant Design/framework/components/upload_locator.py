"""
Upload Locator - Automatically finds Ant Design Upload components on any page
Single Responsibility: Locate upload components using structural signals, no hardcoded selectors
Uses PatternDiscovery to identify data-attr-id patterns
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Optional, Dict
from framework.utils.pattern_discovery import PatternDiscovery
import re


class UploadLocator:
    """
    Automatically locates Ant Design Upload components without hardcoded selectors
    Uses structural signals, data-attr-id, aria-labels, and DOM traversal
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Upload Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_all_uploads(self, timeout: int = 5) -> List[WebElement]:
        """
        Find all Ant Design Upload components on the page
        Uses fast methods first, then slower pattern discovery as fallback
        
        Returns:
            List of upload container WebElements
        """
        uploads = []
        
        # FAST METHOD 1: Find by input[type="file"] first (fastest and most reliable)
        try:
            print("   >> Searching for file inputs (fast method)...")
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
            print(f"   >> Found {len(file_inputs)} file input(s)")
            
            # Use set for faster deduplication
            seen_ids = set()
            
            # Process ALL file inputs efficiently
            for file_input in file_inputs:
                try:
                    upload_container = self._find_upload_container(file_input)
                    if upload_container:
                        elem_id = id(upload_container)
                        if elem_id not in seen_ids:
                            seen_ids.add(elem_id)
                            uploads.append(upload_container)
                except:
                    continue
            print(f"   >> Found {len(uploads)} unique upload container(s) from file inputs")
        except Exception as e:
            print(f"   >> Error finding file inputs: {str(e)}")
        
        # FAST METHOD 2: Find by Ant Design upload class patterns (optimized)
        try:
            print("   >> Searching for Ant Design upload classes (including dragger zones)...")
            # Use more specific selector for speed - include dragger zones
            class_uploads = self.driver.find_elements(By.CSS_SELECTOR, 
                '.ant-upload-select, .ant-upload-drag, .ant-upload-drag-container, .ant-upload-btn, [class*="ant-upload-select"], [class*="ant-upload-drag"]')
            
            seen_ids = set(id(u) for u in uploads)  # Get existing IDs
            
            # Process class matches efficiently
            for elem in class_uploads:
                try:
                    elem_id = id(elem)
                    if elem_id not in seen_ids:
                        # Quick check: does it have file input (directly or in parent)?
                        try:
                            # Check direct child first
                            elem.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                            seen_ids.add(elem_id)
                            uploads.append(elem)
                        except:
                            # Check if it's a dragger zone (has distinctive text)
                            try:
                                text = elem.text.lower()
                                if 'click or drag' in text or 'drag file' in text or ('upload' in text and len(text) > 5):
                                    # Find the parent upload container
                                    container = self._find_upload_container(elem)
                                    if container:
                                        container_id = id(container)
                                        if container_id not in seen_ids:
                                            seen_ids.add(container_id)
                                            uploads.append(container)
                                    else:
                                        # If no container found, use the element itself (might be dragger zone)
                                        class_attr = elem.get_attribute('class') or ''
                                        if 'ant-upload' in class_attr:
                                            seen_ids.add(elem_id)
                                            uploads.append(elem)
                                else:
                                    # Try to find upload container for this element
                                    container = self._find_upload_container(elem)
                                    if container:
                                        container_id = id(container)
                                        if container_id not in seen_ids:
                                            seen_ids.add(container_id)
                                            uploads.append(container)
                            except:
                                # Fallback: try to find container
                                container = self._find_upload_container(elem)
                                if container:
                                    container_id = id(container)
                                    if container_id not in seen_ids:
                                        seen_ids.add(container_id)
                                        uploads.append(container)
                except:
                    continue
            print(f"   >> Found {len(class_uploads)} element(s) with upload classes, total unique uploads: {len(uploads)}")
        except Exception as e:
            print(f"   >> Error finding upload classes: {str(e)}")
        
        # FAST METHOD 3: Direct data-attr-id search (optimized)
        try:
            print("   >> Searching for upload data-attr-id...")
            data_attr_uploads = self.driver.find_elements(By.CSS_SELECTOR, 
                '[data-attr-id*="upload" i], [data-atr-id*="upload" i]')
            
            seen_ids = set(id(u) for u in uploads)  # Get existing IDs
            
            # Process data-attr-id matches efficiently
            for elem in data_attr_uploads:
                try:
                    container = self._find_upload_container(elem)
                    if container:
                        container_id = id(container)
                        if container_id not in seen_ids:
                            seen_ids.add(container_id)
                            uploads.append(container)
                except:
                    continue
            print(f"   >> Found {len(data_attr_uploads)} element(s) with upload data-attr-id, total unique uploads: {len(uploads)}")
        except Exception as e:
            print(f"   >> Error finding upload data-attr-id: {str(e)}")
        
        # SLOW METHOD: PatternDiscovery (SKIP - too slow, only use if absolutely necessary)
        # Skip pattern discovery for speed - we already found uploads via fast methods
        if len(uploads) < 3:
            try:
                print("   >> Trying pattern discovery (may take a moment)...")
                import threading
                
                all_patterns = None
                discovery_complete = threading.Event()
                
                def discover_patterns():
                    nonlocal all_patterns
                    try:
                        all_patterns = self.pattern_discovery.discover_all_data_attr_ids()
                    except Exception as e:
                        pass
                    finally:
                        discovery_complete.set()
                
                discovery_thread = threading.Thread(target=discover_patterns, daemon=True)
                discovery_thread.start()
                
                if discovery_complete.wait(timeout=2):  # Max 2 seconds
                    upload_data_attr_ids = []
                    for component_type, patterns in (all_patterns or {}).items():
                        for pattern in patterns[:5]:  # Limit patterns per type
                            if 'upload' in pattern.lower():
                                upload_data_attr_ids.append(pattern)
                    
                    for data_attr_id in upload_data_attr_ids[:5]:  # Limit to first 5
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                f'[data-attr-id="{data_attr_id}"]')
                            for elem in elements:
                                container = self._find_upload_container(elem)
                                if container:
                                    elem_id = id(container)
                                    if not any(id(u) == elem_id for u in uploads):
                                        uploads.append(container)
                        except:
                            pass
                else:
                    print("   >> Pattern discovery timed out, skipping...")
            except Exception as e:
                print(f"   >> Pattern discovery error: {str(e)}")
                pass
        
        
        # METHOD 4: Find by aria-label containing upload keywords (optimized)
        try:
            print("   >> Searching for upload aria-labels...")
            aria_uploads = self.driver.find_elements(By.CSS_SELECTOR, 
                '[aria-label*="upload" i]')
            
            seen_ids = set(id(u) for u in uploads)  # Get existing IDs
            
            # Process aria-label matches efficiently
            for elem in aria_uploads:
                try:
                    container = self._find_upload_container(elem)
                    if container:
                        container_id = id(container)
                        if container_id not in seen_ids:
                            seen_ids.add(container_id)
                            uploads.append(container)
                except:
                    continue
            print(f"   >> Found {len(aria_uploads)} element(s) with upload aria-label, total unique uploads: {len(uploads)}")
        except Exception as e:
            print(f"   >> Error finding upload aria-labels: {str(e)}")
            pass
        
        # Method 5: Find by visible text patterns (ALWAYS check for dragger zones)
        try:
            text_patterns = [
                "Click or drag file to this area to upload",
                "Click to upload",
                "drag file to this area",
                "Click or drag"
            ]
            seen_ids = set(id(u) for u in uploads)
            
            for pattern in text_patterns:
                try:
                    # Use case-insensitive XPath
                    elements = self.driver.find_elements(By.XPATH, 
                        f'.//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{pattern.lower()}")]')
                    # Process text matches efficiently
                    for elem in elements:
                        try:
                            # For dragger zones, find the upload container
                            container = self._find_upload_container(elem)
                            if container:
                                container_id = id(container)
                                if container_id not in seen_ids:
                                    seen_ids.add(container_id)
                                    uploads.append(container)
                            else:
                                # If no container, check if element itself is upload-related
                                class_attr = elem.get_attribute('class') or ''
                                if 'ant-upload' in class_attr or 'upload' in class_attr.lower():
                                    elem_id = id(elem)
                                    if elem_id not in seen_ids:
                                        seen_ids.add(elem_id)
                                        uploads.append(elem)
                        except:
                            continue
                except:
                    continue
            print(f"   >> Processed text pattern matches, total unique uploads: {len(uploads)}")
        except:
            pass
        
        # Remove duplicates and filter valid uploads
        print(f"   >> Processing {len(uploads)} potential upload component(s)...")
        unique_uploads = []
        seen = set()
        for upload in uploads:
            try:
                elem_id = id(upload)
                if elem_id not in seen:
                    seen.add(elem_id)
                    if self._is_valid_upload(upload):
                        unique_uploads.append(upload)
            except:
                continue
        
        print(f"   >> Found {len(unique_uploads)} valid upload component(s)")
        return unique_uploads
    
    def _deduplicate_uploads(self, uploads: List[WebElement]) -> List[WebElement]:
        """
        Remove duplicate upload elements
        
        Args:
            uploads: List of upload WebElements
            
        Returns:
            Deduplicated list
        """
        unique_uploads = []
        seen_elements = set()
        for upload in uploads:
            try:
                elem_id = id(upload)
                if elem_id not in seen_elements:
                    unique_uploads.append(upload)
                    seen_elements.add(elem_id)
            except:
                continue
        return unique_uploads
    
    def _find_upload_container(self, element: WebElement) -> Optional[WebElement]:
        """
        Traverse DOM to find the Ant Design upload container (optimized for speed)
        
        Args:
            element: Starting element (input, button, text, etc.)
            
        Returns:
            Upload container WebElement or None
        """
        try:
            current = element
            
            # Traverse up to find upload container (max 8 levels to catch dragger zones)
            for level in range(8):
                try:
                    # Quick check: get class attribute once
                    class_attr = current.get_attribute('class') or ''
                    
                    # Fast check: is this an upload container?
                    if 'ant-upload' in class_attr:
                        # Check if it's a dragger zone or has file input
                        try:
                            current.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                            return current
                        except:
                            # Even without file input, if it has ant-upload class, it's likely the container
                            if 'ant-upload-drag' in class_attr or 'ant-upload-select' in class_attr:
                                return current
                            return current
                    
                    # Check if has file input as child (fast check)
                    try:
                        # Use direct child selector for speed
                        file_input = current.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                        if file_input:
                            return current
                    except:
                        pass
                    
                    # Check for dragger zone text patterns
                    try:
                        text = current.text.lower()
                        if ('click or drag' in text or 'drag file' in text) and 'ant-upload' in class_attr:
                            return current
                    except:
                        pass
                    
                    # Move to parent (only if not found yet)
                    try:
                        current = current.find_element(By.XPATH, './..')
                    except:
                        break
                except:
                    break
            
            return None
        except:
            return None
    
    def _is_valid_upload(self, element: WebElement) -> bool:
        """
        Verify if element is a valid Ant Design upload component
        
        Args:
            element: Element to verify
            
        Returns:
            True if valid upload component
        """
        try:
            # Check for file input
            try:
                file_input = element.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                if file_input:
                    return True
            except:
                pass
            
            # Check for upload class patterns
            class_attr = element.get_attribute('class') or ''
            if 'ant-upload' in class_attr:
                return True
            
            # Check for data-attr-id
            data_attr = element.get_attribute('data-attr-id') or ''
            if 'upload' in data_attr.lower():
                return True
            
            # Check for upload-related text
            text = element.text.lower()
            upload_keywords = ['upload', 'choose file', 'select file', 'drag', 'drop']
            if any(keyword in text for keyword in upload_keywords):
                return True
            
            return False
        except:
            return False
    
    def find_upload_by_label(self, label: str, timeout: int = 5) -> Optional[WebElement]:
        """
        Find upload component by semantic label/text
        
        Args:
            label: Label text to search for (e.g., "Profile Photo Upload", "Resume Upload")
            timeout: Maximum wait time
            
        Returns:
            Upload container WebElement or None
        """
        label_lower = label.lower()
        
        # Method 1: Find by data-attr-id using PatternDiscovery
        try:
            # Use PatternDiscovery to find matching data-attr-id
            matching_data_attr_id = self.pattern_discovery.find_matching_data_attr_id(
                label, element_type='generic'
            )
            
            if matching_data_attr_id:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        f'[data-attr-id="{matching_data_attr_id}"]')
                    for elem in elements:
                        container = self._find_upload_container(elem)
                        if container:
                            return container
                except:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, 
                            f'[data-atr-id="{matching_data_attr_id}"]')
                        for elem in elements:
                            container = self._find_upload_container(elem)
                            if container:
                                return container
                    except:
                        pass
            
            # Generate candidates and try them
            candidates = self.pattern_discovery.generate_candidates(label, element_type='generic')
            for candidate in candidates:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        f'[data-attr-id="{candidate}"]')
                    for elem in elements:
                        container = self._find_upload_container(elem)
                        if container and self._is_valid_upload(container):
                            return container
                except:
                    continue
            
            # Fallback: Direct CSS selector search
            try:
                data_attr_selector = f'[data-attr-id*="{label_lower}"], [data-attr-id*="{label}"]'
                elements = self.driver.find_elements(By.CSS_SELECTOR, data_attr_selector)
                for elem in elements:
                    container = self._find_upload_container(elem)
                    if container:
                        return container
            except:
                pass
        except:
            pass
        
        # Method 2: Find by aria-label
        try:
            aria_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                f'[aria-label*="{label_lower}" i], [aria-label*="{label}" i]')
            for elem in aria_elements:
                container = self._find_upload_container(elem)
                if container:
                    return container
        except:
            pass
        
        # Method 3: Find by visible text (fuzzy match)
        try:
            # Search for text containing label
            xpath = f'.//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{label_lower}")]'
            elements = self.driver.find_elements(By.XPATH, xpath)
            for elem in elements:
                container = self._find_upload_container(elem)
                if container:
                    return container
        except:
            pass
        
        # Method 4: Find by nearby label element
        try:
            # Look for label elements near upload
            label_elements = self.driver.find_elements(By.XPATH, 
                f'.//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{label_lower}")]')
            for label_elem in label_elements:
                # Find upload near this label
                try:
                    # Check if upload is sibling or nearby
                    upload = label_elem.find_element(By.XPATH, 
                        './following-sibling::*//*[contains(@class, "ant-upload")] | ./parent::*//*[contains(@class, "ant-upload")]')
                    if upload:
                        container = self._find_upload_container(upload)
                        if container:
                            return container
                except:
                    continue
        except:
            pass
        
        # Method 5: Find all uploads and match by context
        all_uploads = self.find_all_uploads()
        for upload in all_uploads:
            if self._matches_label(upload, label):
                return upload
        
        return None
    
    def _matches_label(self, upload: WebElement, label: str) -> bool:
        """
        Check if upload component matches the given label
        
        Args:
            upload: Upload container element
            label: Label to match
            
        Returns:
            True if matches
        """
        try:
            label_lower = label.lower()
            
            # Check data-attr-id using PatternDiscovery
            data_attr = upload.get_attribute('data-attr-id') or ''
            if not data_attr:
                data_attr = upload.get_attribute('data-atr-id') or ''
            
            if data_attr:
                # Use PatternDiscovery to check if label matches pattern
                matching_id = self.pattern_discovery.find_matching_data_attr_id(label, 'generic')
                if matching_id and matching_id == data_attr:
                    return True
                
                # Direct string matching
                if label_lower in data_attr.lower() or label in data_attr:
                    return True
            
            # Check aria-label
            aria_label = upload.get_attribute('aria-label') or ''
            if label_lower in aria_label.lower() or label in aria_label:
                return True
            
            # Check text content
            text = upload.text.lower()
            if label_lower in text:
                return True
            
            # Check nearby label elements
            try:
                labels = upload.find_elements(By.XPATH, 
                    './/ancestor::*//label | .//preceding-sibling::label | .//following-sibling::label')
                for label_elem in labels:
                    label_text = label_elem.text.lower()
                    if label_lower in label_text:
                        return True
            except:
                pass
            
            return False
        except:
            return False

