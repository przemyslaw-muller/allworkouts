"""
Dashboard page object.
"""
from playwright.sync_api import Page, expect
from .base_page import BasePage


class DashboardPage(BasePage):
    """Dashboard page object."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Locators
        self.workout_cards = page.locator('[data-testid="workout-card"]')
        self.active_plan_card = page.locator('text=Active')
    
    def navigate(self):
        """Navigate to dashboard."""
        self.navigate_to('/dashboard')
    
    def start_workout(self, workout_name: str):
        """Start a workout by clicking on it."""
        # Find the workout card and click it
        workout_card = self.page.locator(f'text={workout_name}')
        workout_card.click()
        
        # Wait for navigation to active workout
        self.page.wait_for_url('**/workout/**', timeout=10000)
    
    def has_active_plan(self) -> bool:
        """Check if there's an active plan."""
        return self.active_plan_card.count() > 0
