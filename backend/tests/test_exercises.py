'''
Tests for exercises API endpoints.
'''

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Equipment, Exercise, ExerciseEquipment, User, UserEquipment


class TestListExercises:
    '''Tests for GET /api/v1/exercises'''

    def test_list_exercises_success(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        '''Test listing all exercises.'''
        response = client.get('/api/v1/exercises', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'exercises' in data['data']
        assert 'pagination' in data['data']
        assert isinstance(data['data']['exercises'], list)

    def test_list_exercises_pagination(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        '''Test exercise list pagination.'''
        response = client.get('/api/v1/exercises?page=1&limit=10', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['limit'] == 10
        assert 'total' in pagination
        assert 'total_pages' in pagination

    def test_list_exercises_search(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        '''Test searching exercises by name.'''
        # Use the full unique name to avoid pagination issues
        search_term = test_exercise.name
        response = client.get(
            f'/api/v1/exercises?search={search_term}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # Should find our test exercise
        exercise_names = [ex['name'] for ex in data['data']['exercises']]
        assert test_exercise.name in exercise_names

    def test_list_exercises_filter_muscle_group(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        '''Test filtering exercises by muscle group.'''
        muscle_group = test_exercise.primary_muscle_groups[0].value
        response = client.get(
            f'/api/v1/exercises?muscle_group={muscle_group}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # All returned exercises should have the muscle group
        for ex in data['data']['exercises']:
            assert muscle_group in ex['primary_muscle_groups']

    def test_list_exercises_filter_equipment(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise_with_equipment: Exercise,
        test_equipment: Equipment,
    ):
        '''Test filtering exercises by equipment.'''
        response = client.get(
            f'/api/v1/exercises?equipment_id={test_equipment.id}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # Should find our test exercise that uses this equipment
        exercise_ids = [ex['id'] for ex in data['data']['exercises']]
        assert str(test_exercise_with_equipment.id) in exercise_ids

    def test_list_exercises_filter_user_can_perform(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_exercise_with_equipment: Exercise,
        test_equipment: Equipment,
    ):
        '''Test filtering exercises by what user can perform.'''
        # Use search to find our specific test exercise (pagination workaround)
        exercise_name = test_exercise_with_equipment.name
        
        # First, user doesn't own equipment - should not be able to perform
        response = client.get(
            f'/api/v1/exercises?user_can_perform=true&search={exercise_name}',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        exercise_ids = [ex['id'] for ex in data['data']['exercises']]
        # Exercise requiring equipment user doesn't have should not be listed
        assert str(test_exercise_with_equipment.id) not in exercise_ids

        # Now add equipment ownership
        user_equipment = UserEquipment(
            user_id=test_user.id,
            equipment_id=test_equipment.id,
        )
        db.add(user_equipment)
        db.commit()

        # Now user should be able to perform the exercise
        response = client.get(
            f'/api/v1/exercises?user_can_perform=true&search={exercise_name}',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        exercise_ids = [ex['id'] for ex in data['data']['exercises']]
        assert str(test_exercise_with_equipment.id) in exercise_ids

    def test_list_exercises_limit_max(self, client: TestClient, auth_headers: dict):
        '''Test that limit is capped at 100.'''
        response = client.get('/api/v1/exercises?limit=200', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['pagination']['limit'] == 100

    def test_list_exercises_unauthorized(self, client: TestClient):
        '''Test listing exercises without authentication.'''
        response = client.get('/api/v1/exercises')

        assert response.status_code == 403


class TestGetExercise:
    '''Tests for GET /api/v1/exercises/{exercise_id}'''

    def test_get_exercise_success(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        '''Test getting exercise details.'''
        response = client.get(
            f'/api/v1/exercises/{test_exercise.id}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['id'] == str(test_exercise.id)
        assert data['data']['name'] == test_exercise.name
        assert 'primary_muscle_groups' in data['data']
        assert 'secondary_muscle_groups' in data['data']
        assert 'equipment' in data['data']
        assert 'personal_records' in data['data']
        assert 'default_weight' in data['data']
        assert 'default_reps' in data['data']
        assert 'default_rest_time_seconds' in data['data']

    def test_get_exercise_with_equipment(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise_with_equipment: Exercise,
        test_equipment: Equipment,
    ):
        '''Test getting exercise details includes equipment.'''
        response = client.get(
            f'/api/v1/exercises/{test_exercise_with_equipment.id}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        equipment_ids = [eq['id'] for eq in data['data']['equipment']]
        assert str(test_equipment.id) in equipment_ids

    def test_get_exercise_with_personal_records(
        self,
        client: TestClient,
        auth_headers: dict,
        test_personal_record,
        test_exercise: Exercise,
    ):
        '''Test getting exercise details includes personal records.'''
        response = client.get(
            f'/api/v1/exercises/{test_exercise.id}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert len(data['data']['personal_records']) >= 1
        pr_ids = [pr['id'] for pr in data['data']['personal_records']]
        assert str(test_personal_record.id) in pr_ids

    def test_get_exercise_not_found(self, client: TestClient, auth_headers: dict):
        '''Test getting non-existent exercise.'''
        fake_id = uuid.uuid4()
        response = client.get(f'/api/v1/exercises/{fake_id}', headers=auth_headers)

        assert response.status_code == 404

    def test_get_exercise_unauthorized(
        self, client: TestClient, test_exercise: Exercise
    ):
        '''Test getting exercise without authentication.'''
        response = client.get(f'/api/v1/exercises/{test_exercise.id}')

        assert response.status_code == 403


class TestGetExerciseSubstitutes:
    '''Tests for GET /api/v1/exercises/{exercise_id}/substitutes'''

    def test_get_substitutes_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise: Exercise,
        test_exercise_2: Exercise,
    ):
        '''Test getting exercise substitutes.'''
        response = client.get(
            f'/api/v1/exercises/{test_exercise.id}/substitutes', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
        # Each substitute should have required fields
        for sub in data['data']:
            assert 'id' in sub
            assert 'name' in sub
            assert 'primary_muscle_groups' in sub
            assert 'secondary_muscle_groups' in sub
            assert 'equipment' in sub
            assert 'match_score' in sub

    def test_get_substitutes_respects_equipment(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_exercise: Exercise,
    ):
        '''Test that substitutes only include exercises user can perform.'''
        # Create an exercise with equipment that user doesn't have
        equipment = Equipment(
            id=uuid.uuid4(),
            name=f'Special Equipment {uuid.uuid4().hex[:8]}',
            description='Equipment user does not have',
        )
        db.add(equipment)
        db.commit()

        exercise_with_equipment = Exercise(
            id=uuid.uuid4(),
            name=f'Special Exercise {uuid.uuid4().hex[:8]}',
            primary_muscle_groups=test_exercise.primary_muscle_groups,  # Same muscle group
            description='Exercise requiring special equipment',
        )
        db.add(exercise_with_equipment)
        db.commit()

        exercise_equipment = ExerciseEquipment(
            exercise_id=exercise_with_equipment.id,
            equipment_id=equipment.id,
        )
        db.add(exercise_equipment)
        db.commit()

        response = client.get(
            f'/api/v1/exercises/{test_exercise.id}/substitutes', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # The exercise requiring equipment user doesn't have should not be in substitutes
        substitute_ids = [sub['id'] for sub in data['data']]
        assert str(exercise_with_equipment.id) not in substitute_ids

    def test_get_substitutes_not_found(self, client: TestClient, auth_headers: dict):
        '''Test getting substitutes for non-existent exercise.'''
        fake_id = uuid.uuid4()
        response = client.get(
            f'/api/v1/exercises/{fake_id}/substitutes', headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_substitutes_unauthorized(
        self, client: TestClient, test_exercise: Exercise
    ):
        '''Test getting substitutes without authentication.'''
        response = client.get(f'/api/v1/exercises/{test_exercise.id}/substitutes')

        assert response.status_code == 403

    def test_get_substitutes_sorted_by_match_score(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        '''Test that substitutes are sorted by match score descending.'''
        response = client.get(
            f'/api/v1/exercises/{test_exercise.id}/substitutes', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        if len(data['data']) > 1:
            scores = [sub['match_score'] for sub in data['data']]
            assert scores == sorted(scores, reverse=True)
