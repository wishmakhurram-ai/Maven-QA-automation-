"""
Base Page Object class for Selenium operations
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional, List


class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, driver: webdriver):
        """
        Initialize base page with WebDriver instance
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 2)  # Optimized for speed
    
    def find_element(self, by: By, value: str, timeout: int = 2):
        """
        Find a single element with explicit wait
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement if found
            
        Raises:
            TimeoutException: If element not found within timeout
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def find_elements(self, by: By, value: str, timeout: int = 2) -> List:
        """
        Find multiple elements with explicit wait
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements
        """
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((by, value)))
        return self.driver.find_elements(by, value)
    
    def wait_for_element(self, by: By, value: str, timeout: int = 2, root=None):
        """
        Wait for element to be present
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            root: Optional root element to search within
            
        Returns:
            WebElement when found
        """
        if root:
            wait = WebDriverWait(root, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        else:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
    
    def is_element_present(self, by: By, value: str, timeout: int = 2) -> bool:
        """
        Check if element is present on the page
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            True if element is present, False otherwise
        """
        try:
            self.find_element(by, value, timeout)
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, by: By, value: str, timeout: int = 2) -> bool:
        """
        Check if element is visible on the page
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            True if element is visible, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False
    
    def is_element_clickable(self, by: By, value: str, timeout: int = 2) -> bool:
        """
        Check if element is clickable
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            True if element is clickable, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.element_to_be_clickable((by, value)))
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_clickable(self, by: By, value: str, timeout: int = 2):
        """
        Wait for element to be clickable
        
        Args:
            by: Selenium By locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement when clickable
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def execute_js(self, script: str, *args):
        """
        Execute JavaScript code
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            Result of JavaScript execution
        """
        return self.driver.execute_script(script, *args)










