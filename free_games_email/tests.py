import pytest

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from free_games_email.database import Base, get_db
from free_games_email.main import app
from free_games_email.models import User


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_payload():
    return {
        'email': 'user@gmail.com',
        'passwd1': 'qwe123',
        'passwd2': 'qwe123'
    }


def test_signup_api(test_client, db_session, user_payload):
    response = test_client.post('/signup/', params=user_payload)
    user = db_session.query(User).filter_by(email='user@gmail.com').first()
    assert response.status_code == 201
    assert response.json()['api_key'] == user.api_key


def test_signup_bad_email(test_client, db_session):
    response = test_client.post('/signup/', params={
        'email': 'user',
        'passwd1': 'qwe123',
        'passwd2': 'qwe123'
    })
    assert response.status_code == 422
    assert response.json()['detail'] == "You input invalid email or password don't match"


def test_signup_bad_passwd(test_client, db_session):
    response = test_client.post('/signup/', params={
        'email': 'user@gmail.com',
        'passwd1': 'qwe',
        'passwd2': 'qwe123'
    })
    assert response.status_code == 422
    assert response.json()['detail'] == "You input invalid email or password don't match"


def test_get_api_key(test_client, db_session, user_payload):
    test_client.post('/signup/', params=user_payload)
    response = test_client.get('/get_api_key/', params={
        'email': user_payload['email'],
        'passwd': user_payload['passwd1']
    })
    user = db_session.query(User).filter_by(email=user_payload['email']).first()
    assert response.status_code == 200
    assert response.json()['api_key'] == user.api_key


def test_get_api_key_wrong_email(test_client, user_payload):
    test_client.post('/signup/', params=user_payload)
    response = test_client.get('/get_api_key/', params={
        'email': 'wrong_email@gmail.com',
        'passwd': user_payload['passwd1']
    })
    assert response.status_code == 404
    assert response.json()['detail'] == 'User with this email was not found'


def test_get_api_key_wrong_passwd(test_client, user_payload):
    test_client.post('/signup/', params=user_payload)
    response = test_client.get('/get_api_key/', params={
        'email': user_payload['email'],
        'passwd': 'wrong_password'
    })
    assert response.status_code == 403
    assert response.json()['detail'] == 'Wrong password'


def test_enable_notifications_api(test_client, db_session, user_payload):
    signup_response = test_client.post('/signup/', params=user_payload)
    headers = {
        'Authorization': f'Bearer {signup_response.json()["api_key"]}'
    }
    response = test_client.post('/enable_notifications/', headers=headers)
    assert response.status_code == 200
    user = db_session.query(User).filter_by(email=user_payload['email']).first()
    assert user.email_notifications is True


def test_enable_notifications_api_wrong_token(test_client, db_session, user_payload):
    test_client.post('/signup/', params=user_payload)
    headers = {
        'Authorization': f'Bearer wrong_token'
    }
    response = test_client.post('/enable_notifications/', headers=headers)
    assert response.status_code == 401
    user = db_session.query(User).filter_by(email=user_payload['email']).first()
    assert user.email_notifications is False
