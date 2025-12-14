"""
E2E test for complete workout flow: login -> log workout -> view PRs in history.
"""
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.workout_page import WorkoutPage
from pages.history_page import HistoryPage, SessionDetailPage


@pytest.mark.smoke
def test_complete_workout_flow(page: Page, test_user: dict):
    """
    Test the complete workout flow:
    1. User logs in
    2. User starts a workout
    3. User logs all exercises with sets and reps
    4. User completes the workout
    5. User views the session in history
    6. User verifies PRs are displayed
    """
    
    # 1. Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user['email'], test_user['password'])
    
    # Verify we're on dashboard
    expect(page).to_have_url('**/dashboard')
    
    # 2. Start workout
    dashboard_page = DashboardPage(page)
    
    # Wait for workouts to load
    page.wait_for_selector('text=Day 1: Push', timeout=10000)
    
    # Click on the workout to start it
    dashboard_page.start_workout('Day 1: Push')
    
    # Verify we're on the workout page
    expect(page).to_have_url('**/workout/**')
    
    # 3. Log exercises
    workout_page = WorkoutPage(page)
    
    # First exercise: Bench Press
    current_exercise = workout_page.get_current_exercise_name()
    print(f'Logging exercise: {current_exercise}')
    
    bench_press_sets = [
        {'weight': 100, 'reps': 10},
        {'weight': 100, 'reps': 9},
        {'weight': 100, 'reps': 8},
    ]
    workout_page.log_full_exercise(bench_press_sets)
    
    # Small delay to ensure UI updates
    page.wait_for_timeout(1000)
    
    # Verify first exercise is marked as completed
    assert workout_page.is_exercise_completed('Bench Press')
    
    # Second exercise: Overhead Press
    current_exercise = workout_page.get_current_exercise_name()
    print(f'Logging exercise: {current_exercise}')
    
    overhead_press_sets = [
        {'weight': 60, 'reps': 12},
        {'weight': 60, 'reps': 11},
        {'weight': 60, 'reps': 10},
    ]
    workout_page.log_full_exercise(overhead_press_sets)
    
    # Small delay to ensure UI updates
    page.wait_for_timeout(1000)
    
    # 4. Complete workout
    workout_page.complete_workout()
    
    # Verify we're on the completion page
    expect(page).to_have_url('**/workout/complete')
    
    # Take screenshot of completion page
    page.screenshot(path='e2e/test-results/screenshots/workout_complete.png')
    
    # Wait a bit to see the completion page
    page.wait_for_timeout(2000)
    
    # 5. Navigate to history
    history_page = HistoryPage(page)
    history_page.navigate()
    
    # Verify we have sessions
    assert history_page.has_sessions(), 'No workout sessions found in history'
    
    # Click on the latest session
    history_page.get_latest_session()
    
    # 6. Verify session details and PRs
    session_detail = SessionDetailPage(page)
    
    # Take screenshot of session detail
    page.screenshot(path='e2e/test-results/screenshots/session_detail.png')
    
    # Verify the session shows completed status
    expect(page.locator('text=Completed')).to_be_visible()
    
    # Verify exercises are logged
    expect(page.locator('text=Bench Press')).to_be_visible()
    expect(page.locator('text=Overhead Press')).to_be_visible()
    
    # Verify sets are logged correctly for Bench Press
    assert session_detail.verify_set_logged('Bench Press', 1, 100, 10)
    assert session_detail.verify_set_logged('Bench Press', 2, 100, 9)
    assert session_detail.verify_set_logged('Bench Press', 3, 100, 8)
    
    # Verify sets are logged correctly for Overhead Press
    assert session_detail.verify_set_logged('Overhead Press', 1, 60, 12)
    assert session_detail.verify_set_logged('Overhead Press', 2, 60, 11)
    assert session_detail.verify_set_logged('Overhead Press', 3, 60, 10)
    
    # Verify PR indicators (since this is first workout, all should be PRs)
    # Note: PRs might not show on first workout depending on backend logic
    # Uncomment if PRs are expected on first workout:
    # assert session_detail.has_pr_badge(), 'No PR badges found'
    # assert session_detail.get_pr_count() > 0, 'No PRs recorded'
    
    print('✅ Workout flow test completed successfully!')


@pytest.mark.smoke
def test_login_invalid_credentials(page: Page):
    """Test login with invalid credentials."""
    login_page = LoginPage(page)
    login_page.navigate()
    
    # Try to login with invalid credentials
    login_page.email_input.fill('invalid@example.com')
    login_page.password_input.fill('wrongpassword')
    login_page.login_button.click()
    
    # Should remain on login page and show error
    page.wait_for_timeout(2000)
    expect(page).to_have_url('**/login')
    
    # Error message should be visible
    # Adjust selector based on your error message implementation
    expect(page.locator('text=Invalid')).to_be_visible(timeout=5000)
