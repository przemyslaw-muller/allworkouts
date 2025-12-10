'''
Tests for equipment API endpoints.
'''

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Equipment, UserEquipment


class TestListEquipment:
    '''Tests for GET /api/v1/equipment'''

    def test_list_equipment_success(
        self, client: TestClient, auth_headers: dict, test_equipment: Equipment
    ):
        '''Test listing all equipment.'''
        response = client.get('/api/v1/equipment', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
        # Should contain at least our test equipment
        equipment_names = [eq['name'] for eq in data['data']]
        assert test_equipment.name in equipment_names

    def test_list_equipment_with_ownership(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user_equipment: UserEquipment,
        test_equipment: Equipment,
    ):
        '''Test that owned equipment is marked correctly.'''
        response = client.get('/api/v1/equipment', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Find our test equipment and verify ownership
        owned_equipment = next(
            (eq for eq in data['data'] if eq['id'] == str(test_equipment.id)), None
        )
        assert owned_equipment is not None
        assert owned_equipment['is_user_owned'] is True

    def test_list_equipment_search(
        self, client: TestClient, auth_headers: dict, test_equipment: Equipment
    ):
        '''Test searching equipment by name.'''
        # Search for our test equipment
        search_term = test_equipment.name[:10]
        response = client.get(
            f'/api/v1/equipment?search={search_term}', headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert len(data['data']) >= 1
        assert any(eq['name'] == test_equipment.name for eq in data['data'])

    def test_list_equipment_filter_owned(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user_equipment: UserEquipment,
        test_equipment: Equipment,
        test_equipment_2: Equipment,
    ):
        '''Test filtering by user_owned=true.'''
        response = client.get('/api/v1/equipment?user_owned=true', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # All returned equipment should be owned
        for eq in data['data']:
            assert eq['is_user_owned'] is True
        # Our owned equipment should be in the list
        equipment_ids = [eq['id'] for eq in data['data']]
        assert str(test_equipment.id) in equipment_ids

    def test_list_equipment_filter_not_owned(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user_equipment: UserEquipment,
        test_equipment_2: Equipment,
    ):
        '''Test filtering by user_owned=false.'''
        response = client.get('/api/v1/equipment?user_owned=false', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # All returned equipment should not be owned
        for eq in data['data']:
            assert eq['is_user_owned'] is False
        # Our unowned equipment should be in the list
        equipment_ids = [eq['id'] for eq in data['data']]
        assert str(test_equipment_2.id) in equipment_ids

    def test_list_equipment_unauthorized(self, client: TestClient):
        '''Test listing equipment without authentication.'''
        response = client.get('/api/v1/equipment')

        assert response.status_code == 401


class TestUpdateEquipmentOwnership:
    '''Tests for PUT /api/v1/equipment/{equipment_id}/ownership'''

    def test_add_ownership_success(
        self, client: TestClient, auth_headers: dict, test_equipment: Equipment
    ):
        '''Test adding equipment ownership.'''
        response = client.put(
            f'/api/v1/equipment/{test_equipment.id}/ownership',
            json={'is_owned': True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['equipment_id'] == str(test_equipment.id)
        assert data['data']['is_owned'] is True

    def test_remove_ownership_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user_equipment: UserEquipment,
        test_equipment: Equipment,
    ):
        '''Test removing equipment ownership.'''
        response = client.put(
            f'/api/v1/equipment/{test_equipment.id}/ownership',
            json={'is_owned': False},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['equipment_id'] == str(test_equipment.id)
        assert data['data']['is_owned'] is False

    def test_ownership_toggle(
        self, client: TestClient, auth_headers: dict, test_equipment: Equipment, db: Session
    ):
        '''Test toggling ownership on and off.'''
        # Add ownership
        response = client.put(
            f'/api/v1/equipment/{test_equipment.id}/ownership',
            json={'is_owned': True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()['data']['is_owned'] is True

        # Verify in list
        list_response = client.get('/api/v1/equipment?user_owned=true', headers=auth_headers)
        owned_ids = [eq['id'] for eq in list_response.json()['data']]
        assert str(test_equipment.id) in owned_ids

        # Remove ownership
        response = client.put(
            f'/api/v1/equipment/{test_equipment.id}/ownership',
            json={'is_owned': False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()['data']['is_owned'] is False

        # Verify in list
        list_response = client.get('/api/v1/equipment?user_owned=false', headers=auth_headers)
        not_owned_ids = [eq['id'] for eq in list_response.json()['data']]
        assert str(test_equipment.id) in not_owned_ids

    def test_ownership_nonexistent_equipment(self, client: TestClient, auth_headers: dict):
        '''Test updating ownership for non-existent equipment.'''
        fake_id = uuid.uuid4()
        response = client.put(
            f'/api/v1/equipment/{fake_id}/ownership',
            json={'is_owned': True},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_ownership_unauthorized(self, client: TestClient, test_equipment: Equipment):
        '''Test updating ownership without authentication.'''
        response = client.put(
            f'/api/v1/equipment/{test_equipment.id}/ownership',
            json={'is_owned': True},
        )

        assert response.status_code == 401

    def test_ownership_isolation_between_users(
        self,
        client: TestClient,
        auth_headers: dict,
        auth_headers_user2: dict,
        test_equipment: Equipment,
    ):
        '''Test that ownership is isolated between users.'''
        # User 1 adds ownership
        response = client.put(
            f'/api/v1/equipment/{test_equipment.id}/ownership',
            json={'is_owned': True},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # User 2 should not see this as owned
        list_response = client.get('/api/v1/equipment', headers=auth_headers_user2)
        equipment = next(
            (eq for eq in list_response.json()['data'] if eq['id'] == str(test_equipment.id)),
            None,
        )
        assert equipment is not None
        assert equipment['is_user_owned'] is False
