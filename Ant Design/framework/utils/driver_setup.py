"""
WebDriver setup utility
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from typing import Optional
import os


class DriverSetup:
    """Utility class for setting up WebDriver instances"""
    
    @staticmethod
    def get_chrome_driver(
        headless: bool = False,
        maximize: bool = True,
        chromedriver_path: Optional[str] = None
    ) -> webdriver.Chrome:
        """
        Create and configure Chrome WebDriver
        
        Args:
            headless: Run browser in headless mode
            maximize: Maximize browser window on start
            chromedriver_path: Path to ChromeDriver executable (optional)
            
        Returns:
            Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        if maximize:
            chrome_options.add_argument('--start-maximized')
        
        # Additional options for better automation
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Set ChromeDriver path if provided
        service = None
        if chromedriver_path:
            service = Service(chromedriver_path)
        
        return webdriver.Chrome(service=service, options=chrome_options)
    
    @staticmethod
    def get_firefox_driver(
        headless: bool = False,
        maximize: bool = True,
        geckodriver_path: Optional[str] = None
    ) -> webdriver.Firefox:
        """
        Create and configure Firefox WebDriver
        
        Args:
            headless: Run browser in headless mode
            maximize: Maximize browser window on start
            geckodriver_path: Path to GeckoDriver executable (optional)
            
        Returns:
            Configured Firefox WebDriver instance
        """
        firefox_options = FirefoxOptions()
        
        if headless:
            firefox_options.add_argument('--headless')
        
        # Set GeckoDriver path if provided
        service = None
        if geckodriver_path:
            service = Service(geckodriver_path)
        
        driver = webdriver.Firefox(service=service, options=firefox_options)
        
        if maximize:
            driver.maximize_window()
        
        return driver
    
    @staticmethod
    def get_driver(
        browser: str = 'chrome',
        headless: bool = False,
        maximize: bool = True,
        driver_path: Optional[str] = None
    ) -> webdriver:
        """
        Get WebDriver instance for specified browser
        
        Args:
            browser: Browser type ('chrome' or 'firefox')
            headless: Run browser in headless mode
            maximize: Maximize browser window on start
            driver_path: Path to driver executable (optional)
            
        Returns:
            Configured WebDriver instance
        """
        browser = browser.lower()
        
        if browser == 'chrome':
            return DriverSetup.get_chrome_driver(headless, maximize, driver_path)
        elif browser == 'firefox':
            return DriverSetup.get_firefox_driver(headless, maximize, driver_path)
        else:
            raise ValueError(f"Unsupported browser: {browser}. Supported: 'chrome', 'firefox'")









