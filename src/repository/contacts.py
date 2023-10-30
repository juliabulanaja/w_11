from datetime import date, timedelta
from typing import List

from sqlalchemy import Column, Integer, String, Boolean, func, Table, Interval, and_
from sqlalchemy.orm import Session


from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(db: Session, user: User) -> List[Contact]:
    """Retrieves list of user's contacts.

    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve contacts for.
    :type user: User
    :return: List of user's contacts.
    :rtype: List[Contact]
    """    
    return db.query(Contact).filter(Contact.user_id == user.id)


async def create_contact(body: ContactModel, db: Session, user: User) -> Contact:
    """Creates new contact.

    :param body: The data for the user to create.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param user: The user to create the contact for.
    :type user: User
    :return: The newly created contact.
    :rtype: Contact
    """    
    contact = Contact(firstname=body.firstname,
                      lastname=body.lastname,
                      email=body.email,
                      phone=body.phone,
                      birthday=body.birthday,
                      user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def get_contact(contact_id: int, db: Session, user: User) -> Contact:
    """ Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve the contact for.
    :type user: User
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Contact | None
    """    
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()



async def update_contact(contact_id: int, body: ContactModel, db: Session, user: User) -> Contact:
    """Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param user: The user to update the contact for.
    :type user: User
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """    

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if not contact:
        return None
    contact.firstname = body.firstname
    contact.lastname = body.lastname
    contact.email = body.email
    contact.phone = body.phone
    contact.birthday = body.birthday

    db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session, user: User) -> Contact:
    """Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param user: The user to remove the contact for.
    :type user: User
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact
    """    
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if not contact:
        return None

    db.delete(contact)
    db.commit()
    return contact


async def get_contacts_with_name(name: str, db: Session, user: User) -> List[Contact]:
    """Retrieves contacts with the specified name for a specific user.

    :param name: The name of the contacts to retrieve.
    :type name: str
    :param db: The database session.
    :type db: Session
    :param user: The user to get the contacts for.
    :type user: User
    :return: Contacts with the specified name for a specific user.
    :rtype: List[Contact]
    """    
    return db.query(Contact).filter(and_(Contact.firstname == name, Contact.user_id == user.id))


async def get_contacts_with_lastname(lastname: str, db: Session, user: User) -> List[Contact]:
    """Retrieves contacts with the specified lastname for a specific user.

    :param lastname: The lastname of the contacts to retrieve.
    :type lastname: str
    :param db: The database session.
    :type db: Session
    :param user: The user to get the contacts for.
    :type user: User
    :return: Contacts with the specified lastname for a specific user.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(and_(Contact.lastname == lastname, Contact.user_id == user.id))


async def get_contacts_with_email(email: str, db: Session, user: User) -> List[Contact]:
    """Retrieves contacts with the specified email for a specific user.

    :param email: Email of the contacts to retrieve.
    :type email: str
    :param db: The database session.
    :type db: Session
    :param user: The user to get the contacts for.
    :type user: User
    :return: Contacts with the specified email for a specific user.
    :rtype: List[Contact]
    """    
    return db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id))


async def get_contacts_with_recent_birthdays(db: Session, user: User) -> List[Contact]:
    """Retrieves contacts with recent birthdays for a specific user.

    :param db: The database session.
    :type db: Session
    :param user: The user to get the contacts for.
    :type user: User
    :return: contacts with recent birthdays for a specific user.
    :rtype: List[Contact]
    """    
    return db.query(Contact).filter(and_(has_birthday_next_week(Contact.birthday), Contact.user_id == user.id))


def has_birthday_next_week(birthday: date) -> bool:
    """Check if specific birthday is in next 7 days.

    :param birthday: Birthday to check.
    :type birthday: date
    :return: True if birthday is in next 7 days or False if not.
    :rtype: bool
    """
    current_age = func.date_part("year", func.age(birthday))
    age_in_7_days = func.date_part("year", func.age(birthday - func.cast(timedelta(7), Interval)))

    return age_in_7_days > current_age
