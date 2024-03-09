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
    :param user: User: Get the current user from the database
    :return: A user
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
    :param file: UploadFile: Get the file from the request
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Get the database session
    :return: A user
    """
    pubic_id = f"HW-13/{user.email}"
    # res = cloudinary.uploader.upload(file.file, pubic_id=pubic_id, overwrite=True)
    res = cloudinary.uploader.upload(file.file, overwrite=True)
    # print(f"{res=}")
    # res_url = cloudinary.CloudinaryImage(pubic_id).build_url(
    #     width=600, height=600, crop="fill", version=res.get("version")
    # )
    # res_url = cloudinary.CloudinaryImage(pubic_id).build_url(version=res.get("version"))
    res_url = res.get("secure_url")
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, config.CACHE_TTL_SEC)
    return user
