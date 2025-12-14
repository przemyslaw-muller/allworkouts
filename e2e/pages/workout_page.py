"""
Active workout page object.
"""
from playwright.sync_api import Page, expect
from .base_page import BasePage


class WorkoutPage(BasePage):
    """Active workout session page object."""
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def log_set(self, set_number: int, weight: float, reps: int):
        """
        Log a single set.
        Assumes we're on the current exercise.
        """
        # Find the set input row
        set_row = self.page.locator(f'text=Set {set_number}').locator('..')
        
        # Fill weight
        weight_input = set_row.locator('input[type="number"]').first
        weight_input.fill(str(weight))
        
        # Fill reps
        reps_input = set_row.locator('input[type="number"]').last
        reps_input.fill(str(reps))
        
        # Click Log button
        log_button = set_row.locator('button:has-text("Log")')
        log_button.click()
        
        # Wait for success indicator
        self.page.wait_for_selector('text=✓', timeout=5000)
    
    def complete_exercise(self):
        """Complete the current exercise."""
        complete_button = self.page.locator('button:has-text("Complete Exercise")')
        complete_button.click()
        
        # Wait for next exercise or completion
        self.page.wait_for_timeout(1000)
    
    def log_full_exercise(self, sets_data: list[dict]):
        """
        Log all sets for an exercise.
        sets_data: [{'weight': 100, 'reps': 10}, ...]
        """
        for i, set_data in enumerate(sets_data, start=1):
            self.log_set(i, set_data['weight'], set_data['reps'])
            
            # Small delay between sets
            self.page.wait_for_timeout(500)
        
        # Complete the exercise
        self.complete_exercise()
    
    def complete_workout(self):
        """Complete the entire workout."""
        # Wait for all exercises to be completed
        complete_workout_button = self.page.locator('button:has-text("Complete Workout")')
        
        # Wait for button to be enabled
        expect(complete_workout_button).to_be_enabled(timeout=10000)
        
        complete_workout_button.click()
        
        # Wait for navigation to completion page
        self.page.wait_for_url('**/workout/complete', timeout=10000)
    
    def get_current_exercise_name(self) -> str:
        """Get the name of the current exercise."""
        # Find the exercise with the pulsing indicator (current)
        current_exercise = self.page.locator('.animate-pulse').locator('..')
        exercise_name = current_exercise.locator('h3').inner_text()
        return exercise_name
    
    def is_exercise_completed(self, exercise_name: str) -> bool:
        """Check if an exercise is marked as completed."""
        exercise_card = self.page.locator(f'text={exercise_name}').locator('..')
        checkmark = exercise_card.locator('svg path[d*="M5 13l4 4L19 7"]')
        return checkmark.count() > 0
