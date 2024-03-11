"""
This module contains the authentication routes for the API.
"""

from fastapi import APIRouter, HTTPException, Depends, Path, Query, Security, status, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth import auth_service
from services.email import send_email
from schemas.users import UserSchema, UserResponse, TokenSchema, RequestEmail
from repository import users as repository_users
from db import get_db
from conf import messages

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
    It takes in a UserSchema object, which is validated by pydantic.
    If the email already exists, it raises an HTTPException with status code 409 (Conflict).

    :param body: Validate the request body
    :type: UserSchema
    :param db: Get the database session
    :type db: AsyncSession
    :param bt: Add a task to the background tasks queue (send e-mail)
    :type bt: BackgroundTasks
    :param request: Get the base url of the application
    :type request: Request
    :return: A user
    :rtype: UserResponse
    :raise: HTTPException with status code 409 when the email already exists
    """

    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post('/login', response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    The login function takes in a username and password, validates them, and returns a token.
    If the username or password is incorrect, it raises an HTTPException with status code 401 (Unauthorized).

    :param body: Get the username and password from the request body
    :type body: OAuth2PasswordRequestForm
    :param db: Get the database session
    :type db: AsyncSession
    :return: A token
    :rtype: TokenSchema
    :raise: HTTPException with status code 401 when the username or password is incorrect
    """

    user = await repository_users.get_user_by_email(body.username, db)
    # print(f'{body.username}, {body.password}')
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD)
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    new_refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, new_refresh_token, db)
    # print(f"{access_token=}, {new_refresh_token=}")
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    The refresh_token function takes in a refresh token, decodes it, and returns an access token.
    If the refresh token is invalid, it raises an HTTPException with status code 401 (Unauthorized).

    :param credentials: Get the refresh token from the request
    :type credentials: HTTPAuthorizationCredentials
    :param db: Get the database session
    :type db: AsyncSession
    :return: A token
    :rtype: TokenSchema
    :raise: HTTPException with status code 401 when the refresh token is invalid
    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function takes in a token, decodes it, and returns a message.
    If the token is invalid, it raises an HTTPException with status code 400 (Bad Request).

    :param token: Get the token from the URL
    :type token: str
    :param db: Get the database session
    :type db: AsyncSession
    :return: A message
    :rtype: dict
    :raise: HTTPException with status code 400 if the token is invalid
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.EMAIL_VERIFICATION_ERROR)
    if user.confirmed:
        return {"message": "Email already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed successfully"}


@router.post('/request_email')
async def request_email(body: RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    The request_email function takes in an email, gets the user with that email, and sends an email to the user.
    If the user does not exist, it returns a message.

    :param body: Get the email from the request body
    :type body: RequestEmail
    :param background_tasks: Add a task to the background tasks queue (send e-mail)
    :type: BackgroundTasks
    :param request: Get the base url of the application
    :type request: Request
    :param db: Get the database session
    :type db: AsyncSession
    :return: A message
    :rtype: dict
    """

    user = await repository_users.get_user_by_email(body.email, db)

    if user:
        # print(f"{user.email}")
        if user.confirmed:
            return {"message": "Email already confirmed"}
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
        return {"message": "Email confirmation sent successfully"}
    else:
        return {"message": "User with this email does not exist"}
