"""
History page object.
"""
from playwright.sync_api import Page, expect
from .base_page import BasePage


class HistoryPage(BasePage):
    """Workout history page object."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Locators
        self.session_cards = page.locator('[data-testid="session-card"]')
    
    def navigate(self):
        """Navigate to history page."""
        self.navigate_to('/history')
    
    def get_latest_session(self):
        """Click on the most recent session."""
        # Get the first session card (most recent)
        first_session = self.page.locator('text=Today').locator('..').locator('..').locator('a').first
        first_session.click()
        
        # Wait for navigation to session detail
        self.page.wait_for_url('**/history/**', timeout=10000)
    
    def has_sessions(self) -> bool:
        """Check if there are any sessions."""
        return self.page.locator('text=Today').count() > 0 or \
               self.page.locator('text=Yesterday').count() > 0


class SessionDetailPage(BasePage):
    """Session detail page object."""
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def has_pr_badge(self) -> bool:
        """Check if the session has PR badges."""
        pr_badge = self.page.locator('text=PR').first
        return pr_badge.count() > 0
    
    def get_pr_count(self) -> int:
        """Get the number of PRs in this session."""
        pr_badges = self.page.locator('text=PR')
        return pr_badges.count()
    
    def has_pr_summary(self) -> bool:
        """Check if there's a PR summary card at the top."""
        pr_summary = self.page.locator('text=new PR')
        return pr_summary.count() > 0
    
    def get_exercise_volume(self, exercise_name: str) -> str:
        """Get the total volume for an exercise."""
        exercise_section = self.page.locator(f'text={exercise_name}').locator('..')
        volume_text = exercise_section.locator('text=volume').inner_text()
        return volume_text
    
    def verify_set_logged(self, exercise_name: str, set_number: int, weight: float, reps: int) -> bool:
        """Verify that a specific set was logged correctly."""
        # Find the exercise section
        exercise_section = self.page.locator(f'text={exercise_name}').locator('..')
        
        # Find the row for the specific set
        set_row = exercise_section.locator('table').locator(f'tr:has-text("Set {set_number}")')
        
        # Check if weight and reps match
        row_text = set_row.inner_text()
        return str(weight) in row_text and str(reps) in row_text
