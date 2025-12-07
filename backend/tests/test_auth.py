'''
Tests for authentication API endpoints.
'''

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import create_refresh_token, hash_password
from app.models import User


class TestRegister:
    '''Tests for POST /api/v1/auth/register'''

    def test_register_success(self, client: TestClient, db: Session):
        '''Test successful user registration.'''
        email = f'newuser_{uuid.uuid4().hex[:8]}@example.com'
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'password': 'securepassword123',
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['user']['email'] == email
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['error'] is None

        # Verify user was created in database
        user = db.query(User).filter(User.email == email).first()
        assert user is not None

        # Cleanup
        db.delete(user)
        db.commit()

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        '''Test registration fails with duplicate email.'''
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': test_user.email,
                'password': 'anotherpassword123',
            },
        )
        
        assert response.status_code == 201  # API returns 201 but with error in body
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_EMAIL_EXISTS'

    def test_register_invalid_email(self, client: TestClient):
        '''Test registration fails with invalid email format.'''
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': 'notanemail',
                'password': 'securepassword123',
            },
        )
        
        assert response.status_code == 422  # Validation error

    def test_register_short_password(self, client: TestClient):
        '''Test registration fails with too short password.'''
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': 'test@example.com',
                'password': '123',  # Too short
            },
        )
        
        assert response.status_code == 422  # Validation error


class TestLogin:
    '''Tests for POST /api/v1/auth/login'''

    def test_login_success(self, client: TestClient, test_user: User):
        '''Test successful login.'''
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': test_user.email,
                'password': 'testpassword123',
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['user']['email'] == test_user.email
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        '''Test login fails with wrong password.'''
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': test_user.email,
                'password': 'wrongpassword',
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_INVALID_CREDENTIALS'

    def test_login_nonexistent_user(self, client: TestClient):
        '''Test login fails with non-existent email.'''
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'nonexistent@example.com',
                'password': 'somepassword',
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_INVALID_CREDENTIALS'

    def test_login_missing_fields(self, client: TestClient):
        '''Test login fails with missing required fields.'''
        response = client.post(
            '/api/v1/auth/login',
            json={'email': 'test@example.com'},  # Missing password
        )
        
        assert response.status_code == 422


class TestRefreshToken:
    '''Tests for POST /api/v1/auth/refresh'''

    def test_refresh_token_success(self, client: TestClient, test_user: User):
        '''Test successful token refresh.'''
        refresh_token = create_refresh_token(str(test_user.id))
        
        response = client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'access_token' in data['data']

    def test_refresh_token_invalid(self, client: TestClient):
        '''Test refresh fails with invalid token.'''
        response = client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': 'invalid.token.here'},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_TOKEN_INVALID'

    def test_refresh_token_deleted_user(self, client: TestClient, db: Session):
        '''Test refresh fails when user is deleted.'''
        # Create a user, get refresh token, then delete user
        user = User(
            id=uuid.uuid4(),
            email=f'deleted_{uuid.uuid4().hex[:8]}@example.com',
            password_hash=hash_password('password123'),
        )
        db.add(user)
        db.commit()
        
        refresh_token = create_refresh_token(str(user.id))
        
        # Delete the user
        db.delete(user)
        db.commit()
        
        response = client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_TOKEN_INVALID'


class TestGetMe:
    '''Tests for GET /api/v1/auth/me'''

    def test_get_me_success(self, client: TestClient, test_user: User, auth_headers: dict):
        '''Test successful retrieval of current user profile.'''
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['id'] == str(test_user.id)
        assert data['data']['email'] == test_user.email
        assert data['data']['unit_system'] == test_user.unit_system.value
        assert 'created_at' in data['data']
        assert 'updated_at' in data['data']

    def test_get_me_unauthorized(self, client: TestClient):
        '''Test get me fails without authentication.'''
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client: TestClient):
        '''Test get me fails with invalid token.'''
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        
        assert response.status_code == 401


class TestUpdateMe:
    '''Tests for PATCH /api/v1/auth/me'''

    def test_update_me_unit_system(self, client: TestClient, test_user: User, auth_headers: dict, db: Session):
        '''Test successful update of user unit system.'''
        # Change to imperial
        response = client.patch(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'unit_system': 'imperial'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['unit_system'] == 'imperial'
        
        # Verify in database
        db.refresh(test_user)
        assert test_user.unit_system.value == 'imperial'
        
        # Change back to metric
        response = client.patch(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'unit_system': 'metric'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['unit_system'] == 'metric'

    def test_update_me_no_changes(self, client: TestClient, test_user: User, auth_headers: dict):
        '''Test update with no fields provided.'''
        response = client.patch(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['email'] == test_user.email

    def test_update_me_unauthorized(self, client: TestClient):
        '''Test update fails without authentication.'''
        response = client.patch(
            '/api/v1/auth/me',
            json={'unit_system': 'imperial'}
        )
        
        assert response.status_code == 401

    def test_update_me_invalid_unit_system(self, client: TestClient, auth_headers: dict):
        '''Test update fails with invalid unit system.'''
        response = client.patch(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'unit_system': 'invalid'}
        )
        
        assert response.status_code == 422


class TestDeleteMe:
    '''Tests for DELETE /api/v1/auth/me'''

    def test_delete_me_success(self, client: TestClient, db: Session):
        '''Test successful account deletion.'''
        # Create a temporary user
        user = User(
            id=uuid.uuid4(),
            email=f'todelete_{uuid.uuid4().hex[:8]}@example.com',
            password_hash=hash_password('password123'),
        )
        db.add(user)
        db.commit()
        
        # Login to get token
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': user.email,
                'password': 'password123',
            },
        )
        access_token = response.json()['data']['access_token']
        
        # Delete account
        response = client.delete(
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 204
        
        # Verify user was deleted
        deleted_user = db.query(User).filter(User.id == user.id).first()
        assert deleted_user is None

    def test_delete_me_unauthorized(self, client: TestClient):
        '''Test delete fails without authentication.'''
        response = client.delete('/api/v1/auth/me')
        
        assert response.status_code == 401

    def test_delete_me_invalid_token(self, client: TestClient):
        '''Test delete fails with invalid token.'''
        response = client.delete(
            '/api/v1/auth/me',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        
        assert response.status_code == 401
