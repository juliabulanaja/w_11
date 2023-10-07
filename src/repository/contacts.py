from datetime import date, timedelta

from sqlalchemy import Column, Integer, String, Boolean, func, Table, Interval

from src.database.models import Contact


async def get_contacts(db):
    return db.query(Contact).all()


async def create_contact(body, db):
    contact = Contact(firstname=body.firstname,
                      lastname=body.lastname,
                      email=body.email,
                      phone=body.phone,
                      birthday=body.birthday)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def get_contact(contact_id, db):
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def update_contact(contact_id, body, db):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        return None
    contact.firstname = body.firstname
    contact.lastname = body.lastname
    contact.email = body.email
    contact.phone = body.phone
    contact.birthday = body.birthday

    db.commit()
    return contact


async def remove_contact(contact_id, db):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        return None

    db.delete(contact)
    db.commit()
    return contact


async def get_contacts_with_name(name, db):
    return db.query(Contact).filter(Contact.firstname == name)


async def get_contacts_with_lastname(lastname, db):
    return db.query(Contact).filter(Contact.lastname == lastname)


async def get_contacts_with_email(email, db):
    return db.query(Contact).filter(Contact.email == email)


async def get_contacts_with_recent_birthdays(db):
    return db.query(Contact).filter(has_birthday_next_week(Contact.birthday))


def has_birthday_next_week(birthday):

    current_age = func.date_part("year", func.age(birthday))
    age_in_7_days = func.date_part("year", func.age(birthday - func.cast(timedelta(7), Interval)))

    return age_in_7_days > current_age
