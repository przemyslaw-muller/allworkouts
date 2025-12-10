'''
Tests for personal records API endpoints.
'''

import uuid
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import RecordTypeEnum
from app.models import Exercise, PersonalRecord, User


class TestListPersonalRecords:
    '''Tests for GET /api/v1/personal-records'''

    def test_list_personal_records_success(
        self, client: TestClient, auth_headers: dict, test_personal_record: PersonalRecord
    ):
        '''Test listing personal records.'''
        response = client.get('/api/v1/personal-records', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'records' in data['data']
        assert 'pagination' in data['data']
        assert len(data['data']['records']) >= 1

    def test_list_personal_records_filter_by_exercise(
        self,
        client: TestClient,
        auth_headers: dict,
        test_personal_record: PersonalRecord,
        test_exercise: Exercise,
    ):
        '''Test filtering personal records by exercise.'''
        response = client.get(
            f'/api/v1/personal-records?exercise_id={test_exercise.id}',
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # All records should be for the specified exercise
        for record in data['data']['records']:
            assert record['exercise']['id'] == str(test_exercise.id)

    def test_list_personal_records_filter_by_type(
        self, client: TestClient, auth_headers: dict, test_personal_record: PersonalRecord
    ):
        '''Test filtering personal records by record type.'''
        response = client.get(
            f'/api/v1/personal-records?record_type={RecordTypeEnum.ONE_RM.value}',
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        for record in data['data']['records']:
            assert record['record_type'] == RecordTypeEnum.ONE_RM.value

    def test_list_personal_records_pagination(
        self, client: TestClient, auth_headers: dict, test_personal_record: PersonalRecord
    ):
        '''Test personal records pagination.'''
        response = client.get(
            '/api/v1/personal-records?page=1&limit=5', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['limit'] == 5

    def test_list_personal_records_empty(
        self, client: TestClient, auth_headers_user2: dict
    ):
        '''Test listing personal records when user has none.'''
        response = client.get('/api/v1/personal-records', headers=auth_headers_user2)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert len(data['data']['records']) == 0

    def test_list_personal_records_unauthorized(self, client: TestClient):
        '''Test listing personal records without authentication.'''
        response = client.get('/api/v1/personal-records')

        assert response.status_code == 401


class TestCreatePersonalRecord:
    '''Tests for POST /api/v1/personal-records'''

    def test_create_personal_record_success(
        self, client: TestClient, auth_headers: dict, test_exercise_2: Exercise, db: Session
    ):
        '''Test creating a new personal record.'''
        response = client.post(
            '/api/v1/personal-records',
            json={
                'exercise_id': str(test_exercise_2.id),
                'record_type': RecordTypeEnum.ONE_RM.value,
                'value': 120.5,
                'unit': 'kg',
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['record_type'] == RecordTypeEnum.ONE_RM.value
        assert float(data['data']['value']) == 120.5

        # Cleanup
        db.query(PersonalRecord).filter(PersonalRecord.id == data['data']['id']).delete()
        db.commit()

    def test_create_personal_record_updates_existing(
        self,
        client: TestClient,
        auth_headers: dict,
        test_personal_record: PersonalRecord,
        test_exercise: Exercise,
    ):
        '''Test that creating a higher PR updates existing record.'''
        # Get current value
        current_value = float(test_personal_record.value)
        new_value = current_value + 50  # Higher value

        response = client.post(
            '/api/v1/personal-records',
            json={
                'exercise_id': str(test_exercise.id),
                'record_type': test_personal_record.record_type.value,
                'value': new_value,
                'unit': 'kg',
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        # Should update to new higher value
        assert float(data['data']['value']) == new_value

    def test_create_personal_record_lower_value_rejected(
        self,
        client: TestClient,
        auth_headers: dict,
        test_personal_record: PersonalRecord,
        test_exercise: Exercise,
    ):
        '''Test that creating a lower PR is rejected.'''
        current_value = float(test_personal_record.value)
        lower_value = current_value - 10  # Lower value

        response = client.post(
            '/api/v1/personal-records',
            json={
                'exercise_id': str(test_exercise.id),
                'record_type': test_personal_record.record_type.value,
                'value': lower_value,
                'unit': 'kg',
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_personal_record_nonexistent_exercise(
        self, client: TestClient, auth_headers: dict
    ):
        '''Test creating PR for non-existent exercise.'''
        fake_id = uuid.uuid4()
        response = client.post(
            '/api/v1/personal-records',
            json={
                'exercise_id': str(fake_id),
                'record_type': RecordTypeEnum.ONE_RM.value,
                'value': 100,
                'unit': 'kg',
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_create_personal_record_unauthorized(
        self, client: TestClient, test_exercise: Exercise
    ):
        '''Test creating PR without authentication.'''
        response = client.post(
            '/api/v1/personal-records',
            json={
                'exercise_id': str(test_exercise.id),
                'record_type': RecordTypeEnum.ONE_RM.value,
                'value': 100,
                'unit': 'kg',
            },
        )

        assert response.status_code == 401


class TestDeletePersonalRecord:
    '''Tests for DELETE /api/v1/personal-records/{record_id}'''

    def test_delete_personal_record_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_exercise: Exercise,
    ):
        '''Test deleting a personal record.'''
        # Create a PR to delete
        pr = PersonalRecord(
            id=uuid.uuid4(),
            user_id=test_user.id,
            exercise_id=test_exercise.id,
            record_type=RecordTypeEnum.TOTAL_VOLUME,
            value=Decimal('500.0'),
            unit='kg',
            achieved_at=datetime.utcnow(),
        )
        db.add(pr)
        db.commit()

        response = client.delete(
            f'/api/v1/personal-records/{pr.id}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify it's deleted
        deleted_pr = db.query(PersonalRecord).filter(PersonalRecord.id == pr.id).first()
        assert deleted_pr is None

    def test_delete_personal_record_not_found(self, client: TestClient, auth_headers: dict):
        '''Test deleting non-existent personal record.'''
        fake_id = uuid.uuid4()
        response = client.delete(
            f'/api/v1/personal-records/{fake_id}', headers=auth_headers
        )

        assert response.status_code == 404

    def test_delete_personal_record_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_personal_record: PersonalRecord,
    ):
        '''Test that user cannot delete another user's personal record.'''
        response = client.delete(
            f'/api/v1/personal-records/{test_personal_record.id}',
            headers=auth_headers_user2,
        )

        # Should return 404 since the record doesn't belong to user2
        assert response.status_code == 404

    def test_delete_personal_record_unauthorized(
        self, client: TestClient, test_personal_record: PersonalRecord
    ):
        '''Test deleting PR without authentication.'''
        response = client.delete(
            f'/api/v1/personal-records/{test_personal_record.id}'
        )

        assert response.status_code == 401
