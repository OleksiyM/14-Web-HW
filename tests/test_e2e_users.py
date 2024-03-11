from unittest.mock import MagicMock, AsyncMock, Mock, patch
import cloudinary
import pytest

from services.auth import auth_service
from entity.models import User
import repository.users as repository_users


def test_get_me(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        # response = client.get('api/users/me', headers=headers)
        # assert response.status_code != 200, response.text


def test_get_me_not_authorized(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("api/users/me")
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_avatar_not_authorized(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("api/users/avatar")
        assert response.status_code == 405, response.text
        assert response.json() == {"detail": "Method Not Allowed"}


def test_avatar_authorized_with_valid_token(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        token = get_token  # Get a valid authentication token
        headers = {"Authorization": f"Bearer {token}"}

        # real file uploaded to the Cloudinary service
        with open("./tests/test_image.jpg", "rb") as image_file:
            response = client.patch("api/users/avatar", headers=headers, files={"file": image_file})

        assert response.status_code == 200
        assert response.json()["avatar"] is not None
