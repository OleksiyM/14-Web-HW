import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from entity.models import Base, User
from db import get_db
from services.auth import auth_service

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_contact1 = {
    "first_name": "Jack",
    "last_name": "Smith",
    "email": "jack@example.com",
    "birthday": "2000-01-01",
    "phone": "1234567890",
    "notes": "user 1 notes"

}
test_user = {
    "username": "user",
    "password": "12345678",
    "email": "user@example.com",
    "avatar": "https://gravatar/123"
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(username=test_user["username"], email=test_user["email"], password=hash_password,
                                confirmed=True, role="user")
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create the test client with the desired base URL
    client = TestClient(app)
    client.base_url = "http://127.0.0.1:8000"  # Set the base URL

    # yield TestClient(app)
    yield client


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token
