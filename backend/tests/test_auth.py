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
