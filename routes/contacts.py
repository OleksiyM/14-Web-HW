"""Contacts API Routes

Provides API routes for managing contact resources, including creating, retrieving, and updating contacts for authenticated users."""
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from db import get_db
from repository import contacts as repository_contacts
from entity.models import User, Role
from services.auth import auth_service
from services.roles import RoleAccess
from schemas.contacts import ContactSchema, ContactResponseSchema
from conf.config import config
from conf import messages

router = APIRouter(prefix='/contacts', tags=['contacts'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.post('/', response_model=ContactResponseSchema,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def create_contact(contact: ContactSchema = Body(...), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user), ):
    """
    Creates a contact for the current user. If the contact already exists, an HTTP 409 error is returned.

    :param contact: Validate the request body
    :type contact: ContactSchema
    :param db: Get the database session
    :type db: AsyncSession
    :param user: Get the current user
    :type user: User
    :return: A contact
    :rtype: ContactResponseSchema
    :raise: HTTPException with status code 409 when contact already exists
    """
    try:
        contact = await repository_contacts.create_contact(contact, db, user)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.CONTACT_ALREADY_EXISTS)
    return contact


@router.get('/search', response_model=list[ContactResponseSchema],
            dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def search_contacts(limit: int = Query(10, ge=10, le=100),
                          offset: int = Query(0, ge=0),
                          q: str = Query(min_length=3, max_length=50),
                          db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    """
    Searches for contacts by name, last name, e-mail.
    If no contacts match the search query, an empty list is returned and raises an HTTP 404 error.

    :param limit: Limit the number of contacts returned
    :type limit: int
    :param offset: Skip the first n contacts
    :type offset: int
    :param q: Search query
    :type q: str
    :param db: Get the database session
    :type db: AsyncSession
    :param user: Get the current user
    :type user: User
    :return: A list of contacts that match the search query
    :rtype: list[ContactResponseSchema]
    :raise: HTTPException with status code 404 when no contacts match the search query
    """

    contacts = await repository_contacts.search_contacts(limit, offset, q, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contacts


@router.get('/birthdays', response_model=list[ContactResponseSchema],
            dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def get_birthdays(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts with birthdays for the current user.
    If no contacts with birthdays are found, an HTTP 404 error is raised.

    :param db: Get the database session
    :type db: AsyncSession
    :param user: Get the current user
    :type user: User
    :return: A list of contacts with birthdays for the current user.
    :rtype: list[ContactResponseSchema]
    :raise: HTTPException with status code 404 when no contacts with birthdays are found.
    """

    contacts_with_birthdays = await repository_contacts.get_birthdays(db, user)
    if contacts_with_birthdays is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contacts_with_birthdays


@router.get('/', response_model=list[ContactResponseSchema],
            dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def get_contacts(limit: int = Query(10, ge=10, le=100),
                       offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts.
    If no contacts, an empty list is returned and raises an HTTP 404 error.

    :param limit: Limit the number of contacts returned
    :type limit:  int
    :param offset: Skip the first n contacts
    :type offset: int
    :param db: Get the database session
    :type db: AsyncSession
    :param user: Get the current user
    :type user: User
    :return: A list of contacts. If no contacts, an empty list is returned and raises an HTTP 404 error.
    :rtype: list[ContactResponseSchema]
    :raise: HTTPException with status code 404 when no contacts are found.
    """

    contacts = await repository_contacts.get_contacts(limit, offset, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponseSchema,
            dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a contact by ID.
    If no contact is found, an HTTP 404 error is raised.

    :param contact_id: Get the contact ID
    :type contact_id: int
    :param db: Get the database session
    :type db: AsyncSession
    :param user: Get the current user
    :type user: User
    :return: A contact by ID. If no contact is found, an HTTP 404 error is raised.
    :rtype: ContactResponseSchema
    :raise: HTTPException with status code 404 when no contact is found.
    """

    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contact


@router.put('/{contact_id}', response_model=ContactResponseSchema,
            status_code=status.HTTP_202_ACCEPTED,
            dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def update_contact(contact_id: int = Path(ge=1), body: ContactSchema = Body(...),
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Updates a contact by ID.
    If no contact is found, an HTTP 404 error is raised.

    :param contact_id: Get the contact ID
    :type contact_id: int
    :param body: Validate the request body
    :type body: ContactSchema
    :param db: Get the database session
    :type db: AsyncSession
    :param user: Get the current user
    :type user: User
    :return: A contact by ID. If no contact is found, an HTTP 404 error is raised.
    :rtype: ContactResponseSchema
    :raise: HTTPException with status code 404 when no contact is found.
    """

    # if not (body.first_name or body.last_name or body.email or body.phone):
    #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")
    try:
        updated_contact = await repository_contacts.update_contact(contact_id, body, db, user)
    except HTTPException as e:
        print(f'Error: {e}')

    if not updated_contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)

    return updated_contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RateLimiter(times=config.LIMIT_TIMES, seconds=config.LIMIT_SECONDS))], )
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """Deletes a contact by ID

    :param: contact_id: Get the contact ID
    :type contact_id: int
    :param: db: Get the database session
    :type db: AsyncSession
    :param: user: Get the current user
    :type user: User
    :return: A contact by ID and 204 status code.
    :rtype: ContactSchema
    """
    # contact = await repository_contacts.get_contact(contact_id, db)
    # if contact is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact
