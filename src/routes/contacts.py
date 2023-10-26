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
def root():
    return {"message": "Welcome to FastAPI!"}


@router.get("/contacts/", 
            response_model=List[ContactResponse], 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.get_contacts(db, current_user)


@router.post("/contacts/", 
             response_model=ContactResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))]
             )
async def create_contact(body: ContactModel, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body, db, current_user)


@router.get("/contacts/{contact_id}", 
            response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contact(contact_id: int = Path(description="The ID of the contact to get", ge=1),
                       db: Session = Depends(get_db), 
                       current_user: User = Depends(auth_service.get_current_user)):
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
                         current_user: User = Depends(auth_service.get_current_user)):
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
                         current_user: User = Depends(auth_service.get_current_user)):
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
                                     current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.get_contacts_with_name(firstname, db, current_user)


@router.get("/contacts/search-by-lastname/{lastname}", 
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts_by_lastname(lastname: str = Path(description="Show contacts with lastname", min_length=2, max_length=50),
                                    db: Session = Depends(get_db),
                                    current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.get_contacts_with_lastname(lastname, db, current_user)


@router.get("/contacts/search-by-email/{email}", 
            response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts_by_email(email: str = Path(description="Show contacts with email", min_length=2, max_length=50),
                                 db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.get_contacts_with_email(email, db, current_user)


@router.get("/contacts/birthday-contacts/", 
            response_model=List[ContactResponse], 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def read_contacts_with_recent_birthdays(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.get_contacts_with_recent_birthdays(db, current_user)

