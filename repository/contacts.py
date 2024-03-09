"""Module for managing contact data

This module provides functions for working with contact data in the database.
"""
from datetime import timedelta, datetime
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select, or_, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from entity.models import Contact, User
from schemas.contacts import ContactSchema, ContactResponseSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User) -> [Contact]:
    """
    Returns a list of contacts
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify how many contacts to skip
    :param db: AsyncSession: Database connection
    :param user: User: User object
    :return: A list of contacts
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Returns a contact
    :param contact_id: int: ID of the contact
    :param db: AsyncSession: Database connection
    :param user: User: User object
    :return: A contact or None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(contact: ContactSchema, db: AsyncSession, user: User):
    """
    Creates a new contact
    :param contact: ContactSchema: Contact object
    :param db: AsyncSession: Database connection
    :param user: User: User object
    :return: A contact
    """
    contact_obj = Contact(**contact.dict(), user=user)
    db.add(contact_obj)
    await db.commit()
    await db.refresh(contact_obj)
    return contact_obj


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    """
    Updates a contact
    :param contact_id: int: ID of the contact
    :param body: ContactSchema: Contact object
    :param db: AsyncSession: Database connection
    :param user: User: User object
    :return: A contact or None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    # contact_email = await get_contact_by_email(contact.email, db)
    # if contact_email and contact_email.id != contact.id:  # Ignore conflicting email for same contact
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    #
    # contact_phone = await get_contact_by_phone(contact.phone, db)
    # if contact_phone and contact_phone.id != contact.id:  # Ignore conflicting phone for same contact
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already in use")
    if body.first_name is not None:
        contact.first_name = body.first_name
    if body.last_name is not None:
        contact.last_name = body.last_name
    if body.birthday is not None:
        contact.birthday = body.birthday
    if body.phone is not None:
        contact.phone = body.phone
    if body.email is not None:
        contact.email = body.email
    if body.notes is not None:
        contact.notes = body.notes

    # for attr, value in body.dict().items():
    #     if hasattr(contact, attr):  # Avoid overriding internal fields
    #         setattr(contact, attr, value)
    try:
        await db.commit()
        await db.refresh(contact)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact already in use")

    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Deletes a contact by ID.
    :param contact_id: int: ID of the contact to delete.
    :param db: AsyncSession: Database connection
    :param user: User object
    :return: Returns the deleted contact object. If the contact does not exist, returns None.
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact_obj = result.scalar_one_or_none()
    if not contact_obj:
        return None
    await db.delete(contact_obj)
    await db.commit()
    return contact_obj


async def get_contact_by_email(email: str, db: AsyncSession, user: User) -> ContactResponseSchema | None:
    """
    Returns a contact by email.
    :param email: str: Email of the contact to return.
    :param db: AsyncSession: Database connection
    :param user: User object
    :return: A contact or None
    """
    stmt = select(Contact).filter_by(email=email, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    return contact


async def get_contact_by_phone(phone: str, db: AsyncSession, user: User) -> ContactResponseSchema | None:
    """
    Returns a contact by phone.
    :param phone: str: Phone of the contact to return.
    :param db: AsyncSession: Database connection
    :param user: User object
    :return: A contact or None
    """
    stmt = select(Contact).filter_by(phone=phone, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    return contact


async def search_contacts(limit: int, offset: int, q: str, db: AsyncSession, user: User) -> Sequence[Contact]:
    """
    Searches for contacts by first name, last name, or email.
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify how many contacts to skip
    :param q: str: Search query
    :param db: AsyncSession: Database connection
    :param user: User object
    :return: A list of contacts
    """
    stmt = select(Contact).filter(
        or_(
            Contact.first_name.ilike(f"%{q}%"),
            Contact.last_name.ilike(f"%{q}%"),
            Contact.email.ilike(f"%{q}%")
        )
    ).filter_by(user=user).offset(offset).limit(limit).order_by(Contact.first_name)

    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_birthdays(db: AsyncSession, user: User):
    """
    Returns a list of contacts whose birthday is today or in the next 7 days.
    :param db: AsyncSession: Database connection
    :param user: User object
    :return: A list of contacts
    """
    # get today's date and the next 7 days' dates as datetime objects
    today = datetime.now().date()

    # list of the next 7 days
    upcoming_dates = [today + timedelta(days=i) for i in range(1, 8)]

    # conditions for the query
    conditions = [and_(extract('month', Contact.birthday) == date.month, extract('day', Contact.birthday) == date.day)
                  for date in upcoming_dates]

    # query with OR condition for each upcoming date
    stmt = select(Contact).where(or_(*conditions)).filter_by(user=user)

    result = await db.execute(stmt)
    contacts = result.scalars().all()

    return contacts
