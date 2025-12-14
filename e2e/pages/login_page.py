"""
Login page object.
"""
from playwright.sync_api import Page, expect
from .base_page import BasePage


class LoginPage(BasePage):
    """Login page object."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Locators
        self.email_input = page.locator('input[type="email"]')
        self.password_input = page.locator('input[type="password"]')
        self.login_button = page.locator('button[type="submit"]')
    
    def navigate(self):
        """Navigate to login page."""
        self.navigate_to('/login')
    
    def login(self, email: str, password: str):
        """Perform login."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()
        
        # Wait for navigation to dashboard
        self.wait_for_url('/dashboard')
