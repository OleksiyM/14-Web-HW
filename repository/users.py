"""
User Management
Provides functions for managing user accounts, including updating refresh tokens and creating new users.
"""

from fastapi import Depends
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from entity.models import User
from schemas.users import UserSchema


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Update refresh token for user.
    :param user: User object.
    :param token: Refresh token.
    :param db: Database session.
    :return: None.
    :raise: None.
    """
    user.refresh_token = token
    await db.commit()


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Create new user.
    :param body: UserSchema object.
    :param db: Database session.
    :return: User object.
    :raise: None.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(f'Error: {err}')

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Get user by email.
    :param email: User email.
    :param db: Database session.
    :return: User object.
    :raise: None.
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """
    Get user by username.
    :param username: User username.
    :param db: Database session.
    :return: User object.
    :raise: None.
    """
    stmt = select(User).filter_by(username=username)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirm email. Mark user as confirmed.
    :param email: User email.
    :param db: Database session.
    :return: None.
    :raise: None.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Update avatar url.
    :param email: User email.
    :param url: Avatar url.
    :param db: Database session.
    :return: User object.
    :raise: None.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
