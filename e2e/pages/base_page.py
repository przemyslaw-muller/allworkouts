"""
Base page object for common functionality.
"""
from playwright.sync_api import Page, expect
import os

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')


class BasePage:
    """Base page object with common methods."""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = FRONTEND_URL
    
    def navigate_to(self, path: str):
        """Navigate to a specific path."""
        url = f'{self.base_url}{path}'
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')
    
    def wait_for_toast(self, text: str = None, timeout: int = 5000):
        """Wait for a toast notification to appear."""
        if text:
            self.page.wait_for_selector(f'text={text}', timeout=timeout)
        else:
            self.page.wait_for_selector('[role="alert"]', timeout=timeout)
    
    def take_screenshot(self, name: str):
        """Take a screenshot."""
        self.page.screenshot(path=f'e2e/test-results/screenshots/{name}.png')
    
    def wait_for_url(self, url: str, timeout: int = 10000):
        """Wait for URL to match."""
        self.page.wait_for_url(f'{self.base_url}{url}', timeout=timeout)
