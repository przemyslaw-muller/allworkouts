"""
Pytest configuration and fixtures for E2E tests.
"""
import os
import sys
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright
from typing import Generator
import requests
from uuid import uuid4

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')


@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    """Configure browser context."""
    return {
        **browser_context_args,
        'viewport': {'width': 1920, 'height': 1080},
        'record_video_dir': 'e2e/test-results/videos/',
    }


@pytest.fixture(scope='function')
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope='function')
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope='function')
def test_user():
    """
    Create a test user with a workout plan.
    Returns user credentials and plan details.
    """
    # Generate unique email for this test run
    test_email = f'test_{uuid4().hex[:8]}@example.com'
    test_password = 'TestPassword123!'
    
    # Register user
    register_response = requests.post(
        f'{BACKEND_URL}/api/v1/auth/register',
        json={
            'email': test_email,
            'password': test_password,
            'name': 'E2E Test User'
        }
    )
    
    if register_response.status_code != 201:
        raise Exception(f'Failed to register test user: {register_response.text}')
    
    auth_data = register_response.json()['data']
    access_token = auth_data['access_token']
    user_id = auth_data['user']['id']
    
    # Create a workout plan with workouts and exercises
    headers = {'Authorization': f'Bearer {access_token}'}
    
    plan_response = requests.post(
        f'{BACKEND_URL}/api/v1/workout-plans',
        headers=headers,
        json={
            'name': 'E2E Test Plan',
            'description': 'Test plan for E2E testing',
            'workouts': [
                {
                    'name': 'Day 1: Push',
                    'day_number': 1,
                    'order_index': 0,
                    'exercises': [
                        {
                            'exercise_id': '00000000-0000-0000-0000-000000000001',  # Bench Press
                            'sequence': 0,
                            'set_configurations': [
                                {'set_number': 1, 'reps_min': 8, 'reps_max': 10},
                                {'set_number': 2, 'reps_min': 8, 'reps_max': 10},
                                {'set_number': 3, 'reps_min': 8, 'reps_max': 10},
                            ],
                            'rest_time_seconds': 90,
                            'confidence_level': 'high'
                        },
                        {
                            'exercise_id': '00000000-0000-0000-0000-000000000002',  # Overhead Press
                            'sequence': 1,
                            'set_configurations': [
                                {'set_number': 1, 'reps_min': 10, 'reps_max': 12},
                                {'set_number': 2, 'reps_min': 10, 'reps_max': 12},
                                {'set_number': 3, 'reps_min': 10, 'reps_max': 12},
                            ],
                            'rest_time_seconds': 60,
                            'confidence_level': 'high'
                        }
                    ]
                }
            ]
        }
    )
    
    if plan_response.status_code != 201:
        raise Exception(f'Failed to create workout plan: {plan_response.text}')
    
    plan_data = plan_response.json()['data']
    
    return {
        'email': test_email,
        'password': test_password,
        'user_id': user_id,
        'access_token': access_token,
        'plan_id': plan_data['id'],
        'workout_id': plan_data['id'],  # Will need to get actual workout ID
    }


@pytest.fixture(scope='function')
def authenticated_page(page: Page, test_user: dict) -> Page:
    """
    Create a page with an authenticated user session.
    """
    # Navigate to login page
    page.goto(f'{FRONTEND_URL}/login')
    
    # Fill in login form
    page.fill('input[type="email"]', test_user['email'])
    page.fill('input[type="password"]', test_user['password'])
    
    # Click login button
    page.click('button[type="submit"]')
    
    # Wait for navigation to dashboard
    page.wait_for_url(f'{FRONTEND_URL}/dashboard', timeout=10000)
    
    return page


def pytest_configure(config):
    """Pytest configuration hook."""
    # Create test results directory
    os.makedirs('e2e/test-results/videos', exist_ok=True)
    os.makedirs('e2e/test-results/screenshots', exist_ok=True)
