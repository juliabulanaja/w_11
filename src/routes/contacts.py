from typing import Union, List

from fastapi import FastAPI, Path, APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.auth import auth_service
from src.repository import contacts as repository_contacts
from src.database.models import Contact, User
from src.schemas import ContactModel, ContactResponse, ContactUpdate

router = APIRouter(tags=["contacts"])


@router.get("/healthchecker")
def root() -> dict:
    """Initialize endpoint for monitor the health of an API .

    :return: Dictionary with message.
    :rtype: dict
    """    
    return {"message": "Welcome to FastAPI!"}


@router.get("/contacts/", 
            response_model=List[ContactResponse], 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)) -> List[Contact]:
    """Initialize db query to get list of user's contacts.

    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :param current_user: The user to retrieve contacts for, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :return: List of user's contacts.
    :rtype: List[Contact]
    """    
    return await repository_contacts.get_contacts(db, current_user)


@router.post("/contacts/", 
             response_model=ContactResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))]
             )
async def create_contact(body: ContactModel, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """Initialize db query to get contact that belong to specific user.

    :param body: Data for creation new contact.
    :type body: ContactModel
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :param current_user: The user to create contact for, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :return: Newly created contact.
    :rtype: Contact
    """    
    return await repository_contacts.create_contact(body, db, current_user)


@router.get("/contacts/{contact_id}", 
            response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contact(contact_id: int = Path(description="The ID of the contact to get", ge=1),
                       db: Session = Depends(get_db), 
                       current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """Initialize db query to get user's contact.

    :param contact_id: ID to get contact, defaults to Path(description="The ID of the contact to get", ge=1).
    :type contact_id: int, optional
    :param db: The database session, defaults to Depends(get_db).
    :type db: Session, optional
    :param current_user: The user to get contact related for, defaults to Depends(auth_service.get_current_user).
    :type current_user: User, optional
    :raises HTTPException: If contact does not exist with such ID.
    :return: contact with specific ID.
    :rtype: Contact
    """    
    contact = await repository_contacts.get_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/contacts/{contact_id}", 
            response_model=ContactResponse, 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def update_contact(body: ContactUpdate, contact_id: int = Path(description="The ID of the contact to put", ge=1),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """Initialize db query to update contact with specific ID.

    :param body: Data for updating new contact.
    :type body: ContactUpdate
    :param contact_id: ID to change contact with, defaults to Path(description="The ID of the contact to put", ge=1)
    :type contact_id: int, optional
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :param current_user: The user to update contact related for, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :raises HTTPException: If contact does not exist with such ID.
    :return: Updated contact.
    :rtype: Contact
    """    
    contact = await repository_contacts.update_contact(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/contacts/{contact_id}", 
               response_model=ContactResponse,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))]
               )
async def remove_contact(contact_id: int = Path(description="The ID of the contact to delete", ge=1),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """Initialize db query to remove contact with specific ID.

    :param contact_id: ID to remove contact with, defaults to Path(description="The ID of the contact to delete", ge=1)
    :type contact_id: int, optional
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :param current_user: The user to remove contact related for, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :raises HTTPException: If contact does not exist with such ID
    :return: Removed contact.
    :rtype: Contact
    """    
    contact = await repository_contacts.remove_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/contacts/search-by-firstname/{firstname}", 
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts_by_firstname(firstname: str = Path(description="Show contacts with name", min_length=2, max_length=50),
                                     db: Session = Depends(get_db),
                                     current_user: User = Depends(auth_service.get_current_user)) -> List[Contact]:
    """Initialize db query to get list of contacts with specific firstname.

    :param firstname: Firstname to get contacts with, defaults to Path(description="Show contacts with name", min_length=2, max_length=50).
    :type firstname: str, optional
    :param db: The database session, defaults to Depends(get_db).
    :type db: Session, optional
    :param current_user: The user to get list of contacts related with, defaults to Depends(auth_service.get_current_user).
    :type current_user: User, optional
    :return: List of contacts with specific firstname.
    :rtype: List[Contact]
    """    
    return await repository_contacts.get_contacts_with_name(firstname, db, current_user)


@router.get("/contacts/search-by-lastname/{lastname}", 
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts_by_lastname(lastname: str = Path(description="Show contacts with lastname", min_length=2, max_length=50),
                                    db: Session = Depends(get_db),
                                    current_user: User = Depends(auth_service.get_current_user)) -> List[Contact]:
    """Initialize db query to get list of contacts with specific lastname.

    :param lastname: Lastname to get contacts with, defaults to Path(description="Show contacts with lastname", min_length=2, max_length=50)
    :type lastname: str, optional
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :param current_user: The user to get list of contacts related with, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :return: List of contacts with specific lastname.
    :rtype: List[Contact]
    """    
    return await repository_contacts.get_contacts_with_lastname(lastname, db, current_user)


@router.get("/contacts/search-by-email/{email}", 
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts_by_email(email: str = Path(description="Show contacts with email", min_length=2, max_length=50),
                                 db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)) -> List[Contact]:
    """Initialize db query to get list of contacts with specific email.

    :param email: Email to get contacts with, defaults to Path(description="Show contacts with email", min_length=2, max_length=50)
    :type email: str, optional
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :param current_user: The user to get list of contacts related with, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :return: List of contacts with specific email.
    :rtype: List[Contact]
    """    
    return await repository_contacts.get_contacts_with_email(email, db, current_user)


@router.get("/contacts/birthday-contacts/", 
            response_model=List[ContactResponse], 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts_with_recent_birthdays(db: Session = Depends(get_db), 
                                              current_user: User = Depends(auth_service.get_current_user)) -> List[Contact]:
    """Initialize db query to get list of contacts with birthday next week related to specific user.

    :param db: The database session, defaults to Depends(get_db).
    :type db: Session, optional
    :param current_user: The user to get list of contacts related with, defaults to Depends(auth_service.get_current_user).
    :type current_user: User, optional
    :return: List of contacts with birthday next week related to specific user
    :rtype: List[Contact]
    """    
    return await repository_contacts.get_contacts_with_recent_birthdays(db, current_user)

