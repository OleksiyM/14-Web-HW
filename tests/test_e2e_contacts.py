from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi_limiter.depends import RateLimiter
import pytest

from services.auth import auth_service
from main import app
from conf.messages import NOT_AUTHENTICATED, CONTACT_NOT_FOUND


def test_get_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get('/api/contacts', headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == []


def test_get_contacts_no_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        redis_mock.get.return_value = None
        response = client.get('/api/contacts', headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == []


def test_get_contacts_not_authorize(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get('/api/contacts')
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED


def test_create_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("api/contacts", headers=headers, json={
            "first_name": "Jack",
            "last_name": "Smith",
            "email": "jack@example.com",
            "birthday": "2000-01-01",
            "phone": "1234567890",
            "notes": "user 1 notes"
        })
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["first_name"] == "Jack"
        assert data["email"] == "jack@example.com"
        assert data["phone"] == "1234567890"
        assert data["notes"] == "user 1 notes"


def test_create_contact_not_authorized(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.post("api/contacts", json={
            "first_name": "Jack",
            "last_name": "Smith",
            "email": "jack@example.com",
            "birthday": "2000-01-01",
            "phone": "1234567890",
            "notes": "user 1 notes"
        })
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED


def test_get_contact_by_id(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 1
        response = client.get(f"api/contacts/{contact_id}", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == contact_id
        assert data["first_name"] == "Jack"
        assert data["email"] == "jack@example.com"
        assert data["phone"] == "1234567890"
        assert data["notes"] == "user 1 notes"


def test_get_contact_by_id_not_authorized(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        contact_id = 1
        response = client.get(f"api/contacts/{contact_id}")
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED


def test_search_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"api/contacts/search?q=Jack", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        print(data)
        assert data == [
            {'id': 1, 'first_name': 'Jack', 'last_name': 'Smith', 'birthday': '2000-01-01', 'notes': 'user 1 notes',
             'email': 'jack@example.com', 'phone': '1234567890'}]


def test_search_contacts_not_found(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"api/contacts/search?q=John", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == []


def test_search_contacts_not_authorize(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get(f"api/contacts/search?q=Jack")
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED


def test_search_birthdays(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"api/contacts/birthdays", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == []


def test_search_birthdays_not_authorized(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get(f"api/contacts/birthdays")
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED


def test_get_contact_by_id_not_found(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 123
        response = client.get(f"api/contacts/{contact_id}", headers=headers)
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == CONTACT_NOT_FOUND


def test_get_contact_by_id(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 1
        response = client.get(f"api/contacts/{contact_id}", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == contact_id
        assert data["first_name"] == "Jack"
        assert data["email"] == "jack@example.com"
        assert data["phone"] == "1234567890"
        assert data["notes"] == "user 1 notes"


def test_get_contact_by_id_not_authorized(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        contact_id = 1
        response = client.get(f"api/contacts/{contact_id}")
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED


def test_update_contagt_by_id(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 1
        response = client.put(f"api/contacts/{contact_id}", headers=headers, json={
            "first_name": "Jack_updated",
            "last_name": "Smith_updated",
            "email": "jack_updated@example.com",
            "birthday": "2000-01-01",
            "phone": "1234567890",
            "notes": "user 1 notes_updated"
        })
        assert response.status_code == 202, response.text
        data = response.json()
        assert data["id"] == contact_id
        assert data["first_name"] == "Jack_updated"
        assert data["last_name"] == "Smith_updated"
        assert data["email"] == "jack_updated@example.com"
        assert data["phone"] == "1234567890"
        assert data["notes"] == "user 1 notes_updated"


def test_update_contagt_by_id_not_authorized(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        contact_id = 1
        response = client.put(f"api/contacts/{contact_id}", json={
            "first_name": "Jack_updated",
            "last_name": "Smith_updated",
            "email": "jack_updated@example.com",
            "birthday": "2000-01-01",
            "phone": "1234567890",
            "notes": "user 1 notes_updated"
        })
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED


def test_delete_contact_by_id(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        contact_id = 1
        response = client.delete(f"api/contacts/{contact_id}", headers=headers)
        assert response.status_code == 204, response.text


def test_delete_contact_by_id_not_authorized(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        contact_id = 1
        response = client.delete(f"api/contacts/{contact_id}")
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == NOT_AUTHENTICATED
