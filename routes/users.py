"""
User API Routes.
"""

import pickle
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Path, Query, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from entity.models import User
from schemas.users import UserResponse
from services.auth import auth_service
from conf.config import config
from repository import users as repository_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get("/me",
            response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    Get current user.

    :param user:  Get the current user from the database
    :type user : User
    :param db: Get the database session
    :type db: AsyncSession
    :return: A user
    :rtype: UserResponse
    """
    return user


@router.patch("/avatar",
              response_model=UserResponse,
              dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def get_current_user(file: UploadFile = File(),
                           user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db), ):
    """
    Get current user.

    :param file: Get the file from the request
    :type: UploadFile
    :param user: Get the current user from the database
    :type: User
    :param db: Get the database session
    :type db: AsyncSession
    :return: A user
    :rtype: UserResponse
    """

    # pubic_id = f"HW-13/{user.email}"
    res = cloudinary.uploader.upload(file.file, overwrite=True)
    # print(f"{res=}")
    res_url = res.get("secure_url")
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, config.CACHE_TTL_SEC)
    return user
