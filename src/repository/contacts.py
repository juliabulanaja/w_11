from datetime import date, timedelta

from sqlalchemy import Column, Integer, String, Boolean, func, Table, Interval, and_
from sqlalchemy.orm import Session


from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(db: Session, user: User):
    return db.query(Contact).filter(Contact.user_id == user.id)


async def create_contact(body: ContactModel, db: Session, user: User):
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


async def get_contact(contact_id, db: Session, user: User):
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()



async def update_contact(contact_id, body, db: Session, user: User):
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


async def remove_contact(contact_id, db: Session, user: User):
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if not contact:
        return None

    db.delete(contact)
    db.commit()
    return contact


async def get_contacts_with_name(name, db: Session, user: User):
    return db.query(Contact).filter(and_(Contact.firstname == name, Contact.user_id == user.id))


async def get_contacts_with_lastname(lastname, db: Session, user: User):
    return db.query(Contact).filter(and_(Contact.lastname == lastname, Contact.user_id == user.id))


async def get_contacts_with_email(email, db: Session, user: User):
    return db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id))


async def get_contacts_with_recent_birthdays(db: Session, user: User):
    return db.query(Contact).filter(and_(has_birthday_next_week(Contact.birthday), Contact.user_id == user.id))


def has_birthday_next_week(birthday):

    current_age = func.date_part("year", func.age(birthday))
    age_in_7_days = func.date_part("year", func.age(birthday - func.cast(timedelta(7), Interval)))

    return age_in_7_days > current_age
