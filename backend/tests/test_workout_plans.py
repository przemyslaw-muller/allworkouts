'''
Tests for workout plans API endpoints.
'''

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import ConfidenceLevelEnum
from app.models import Exercise, User, WorkoutExercise, WorkoutPlan


class TestListWorkoutPlans:
    '''Tests for GET /api/v1/workout-plans'''

    def test_list_workout_plans_success(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        '''Test listing workout plans.'''
        response = client.get('/api/v1/workout-plans', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'plans' in data['data']
        assert 'pagination' in data['data']
        assert len(data['data']['plans']) >= 1

    def test_list_workout_plans_pagination(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        '''Test workout plans pagination.'''
        response = client.get('/api/v1/workout-plans?page=1&limit=5', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['limit'] == 5

    def test_list_workout_plans_empty(
        self, client: TestClient, auth_headers_user2: dict
    ):
        '''Test listing workout plans when user has none.'''
        response = client.get('/api/v1/workout-plans', headers=auth_headers_user2)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert len(data['data']['plans']) == 0

    def test_list_workout_plans_with_exercise_count(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_plan_with_exercises: WorkoutPlan,
    ):
        '''Test that workout plans include exercise count.'''
        response = client.get('/api/v1/workout-plans', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        plan = next(
            (p for p in data['data']['plans'] if p['id'] == str(test_workout_plan_with_exercises.id)),
            None,
        )
        assert plan is not None
        assert plan['exercise_count'] >= 2

    def test_list_workout_plans_unauthorized(self, client: TestClient):
        '''Test listing workout plans without authentication.'''
        response = client.get('/api/v1/workout-plans')

        assert response.status_code == 403


class TestGetWorkoutPlan:
    '''Tests for GET /api/v1/workout-plans/{plan_id}'''

    def test_get_workout_plan_success(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        '''Test getting workout plan details.'''
        response = client.get(
            f'/api/v1/workout-plans/{test_workout_plan.id}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['id'] == str(test_workout_plan.id)
        assert data['data']['name'] == test_workout_plan.name
        assert 'exercises' in data['data']
        assert 'created_at' in data['data']
        assert 'updated_at' in data['data']

    def test_get_workout_plan_with_exercises(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_plan_with_exercises: WorkoutPlan,
    ):
        '''Test getting workout plan details includes exercises.'''
        response = client.get(
            f'/api/v1/workout-plans/{test_workout_plan_with_exercises.id}',
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert len(data['data']['exercises']) >= 2

        # Check exercise details
        for exercise in data['data']['exercises']:
            assert 'id' in exercise
            assert 'exercise' in exercise
            assert 'sequence' in exercise
            assert 'sets' in exercise
            assert 'reps_min' in exercise
            assert 'reps_max' in exercise

    def test_get_workout_plan_not_found(self, client: TestClient, auth_headers: dict):
        '''Test getting non-existent workout plan.'''
        fake_id = uuid.uuid4()
        response = client.get(f'/api/v1/workout-plans/{fake_id}', headers=auth_headers)

        assert response.status_code == 404

    def test_get_workout_plan_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_plan: WorkoutPlan,
    ):
        '''Test that user cannot access another user's workout plan.'''
        response = client.get(
            f'/api/v1/workout-plans/{test_workout_plan.id}',
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_get_workout_plan_unauthorized(
        self, client: TestClient, test_workout_plan: WorkoutPlan
    ):
        '''Test getting workout plan without authentication.'''
        response = client.get(f'/api/v1/workout-plans/{test_workout_plan.id}')

        assert response.status_code == 403


class TestCreateWorkoutPlan:
    '''Tests for POST /api/v1/workout-plans'''

    def test_create_workout_plan_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_exercise: Exercise,
        test_exercise_2: Exercise,
    ):
        '''Test creating a new workout plan.'''
        response = client.post(
            '/api/v1/workout-plans',
            json={
                'name': 'Test Created Plan',
                'description': 'A test workout plan',
                'exercises': [
                    {
                        'exercise_id': str(test_exercise.id),
                        'sequence': 1,
                        'sets': 3,
                        'reps_min': 8,
                        'reps_max': 12,
                        'rest_time_seconds': 90,
                        'confidence_level': ConfidenceLevelEnum.MEDIUM.value,
                    },
                    {
                        'exercise_id': str(test_exercise_2.id),
                        'sequence': 2,
                        'sets': 4,
                        'reps_min': 6,
                        'reps_max': 10,
                        'rest_time_seconds': 120,
                        'confidence_level': ConfidenceLevelEnum.HIGH.value,
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['name'] == 'Test Created Plan'
        assert 'id' in data['data']

        # Cleanup
        plan_id = data['data']['id']
        db.query(WorkoutExercise).filter(WorkoutExercise.workout_plan_id == plan_id).delete()
        db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).delete()
        db.commit()

    def test_create_workout_plan_invalid_exercise(
        self, client: TestClient, auth_headers: dict
    ):
        '''Test creating workout plan with non-existent exercise.'''
        fake_id = uuid.uuid4()
        response = client.post(
            '/api/v1/workout-plans',
            json={
                'name': 'Invalid Plan',
                'exercises': [
                    {
                        'exercise_id': str(fake_id),
                        'sequence': 1,
                        'sets': 3,
                        'reps_min': 8,
                        'reps_max': 12,
                        'rest_time_seconds': 90,
                        'confidence_level': ConfidenceLevelEnum.MEDIUM.value,
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_workout_plan_unauthorized(
        self, client: TestClient, test_exercise: Exercise
    ):
        '''Test creating workout plan without authentication.'''
        response = client.post(
            '/api/v1/workout-plans',
            json={
                'name': 'Test Plan',
                'exercises': [
                    {
                        'exercise_id': str(test_exercise.id),
                        'sequence': 1,
                        'sets': 3,
                        'reps_min': 8,
                        'reps_max': 12,
                        'rest_time_seconds': 90,
                        'confidence_level': ConfidenceLevelEnum.MEDIUM.value,
                    },
                ],
            },
        )

        assert response.status_code == 403


class TestUpdateWorkoutPlan:
    '''Tests for PUT /api/v1/workout-plans/{plan_id}'''

    def test_update_workout_plan_name(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        '''Test updating workout plan name.'''
        response = client.put(
            f'/api/v1/workout-plans/{test_workout_plan.id}',
            json={'name': 'Updated Plan Name'},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'updated_at' in data['data']

    def test_update_workout_plan_description(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        '''Test updating workout plan description.'''
        response = client.put(
            f'/api/v1/workout-plans/{test_workout_plan.id}',
            json={'description': 'Updated description'},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    def test_update_workout_plan_exercises(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_plan: WorkoutPlan,
        test_exercise: Exercise,
    ):
        '''Test updating workout plan exercises.'''
        response = client.put(
            f'/api/v1/workout-plans/{test_workout_plan.id}',
            json={
                'exercises': [
                    {
                        'exercise_id': str(test_exercise.id),
                        'sequence': 1,
                        'sets': 5,
                        'reps_min': 5,
                        'reps_max': 5,
                        'rest_time_seconds': 180,
                        'confidence_level': ConfidenceLevelEnum.HIGH.value,
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    def test_update_workout_plan_not_found(self, client: TestClient, auth_headers: dict):
        '''Test updating non-existent workout plan.'''
        fake_id = uuid.uuid4()
        response = client.put(
            f'/api/v1/workout-plans/{fake_id}',
            json={'name': 'Updated Name'},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_workout_plan_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_plan: WorkoutPlan,
    ):
        '''Test that user cannot update another user's workout plan.'''
        response = client.put(
            f'/api/v1/workout-plans/{test_workout_plan.id}',
            json={'name': 'Hacked Name'},
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_update_workout_plan_unauthorized(
        self, client: TestClient, test_workout_plan: WorkoutPlan
    ):
        '''Test updating workout plan without authentication.'''
        response = client.put(
            f'/api/v1/workout-plans/{test_workout_plan.id}',
            json={'name': 'Updated Name'},
        )

        assert response.status_code == 403


class TestDeleteWorkoutPlan:
    '''Tests for DELETE /api/v1/workout-plans/{plan_id}'''

    def test_delete_workout_plan_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
    ):
        '''Test soft deleting a workout plan.'''
        # Create a plan to delete
        plan = WorkoutPlan(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name='Plan to Delete',
        )
        db.add(plan)
        db.commit()

        response = client.delete(
            f'/api/v1/workout-plans/{plan.id}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify it's soft deleted (still exists but with deleted_at)
        db.refresh(plan)
        assert plan.deleted_at is not None

        # Cleanup
        db.delete(plan)
        db.commit()

    def test_delete_workout_plan_not_found(self, client: TestClient, auth_headers: dict):
        '''Test deleting non-existent workout plan.'''
        fake_id = uuid.uuid4()
        response = client.delete(
            f'/api/v1/workout-plans/{fake_id}', headers=auth_headers
        )

        assert response.status_code == 404

    def test_delete_workout_plan_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_plan: WorkoutPlan,
    ):
        '''Test that user cannot delete another user's workout plan.'''
        response = client.delete(
            f'/api/v1/workout-plans/{test_workout_plan.id}',
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_delete_workout_plan_unauthorized(
        self, client: TestClient, test_workout_plan: WorkoutPlan
    ):
        '''Test deleting workout plan without authentication.'''
        response = client.delete(f'/api/v1/workout-plans/{test_workout_plan.id}')

        assert response.status_code == 403
