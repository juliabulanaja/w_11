from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.database.auth import auth_service
from src.services.email import send_email
from src.schemas import UserDb
from src.conf.config import settings
from src.database.models import User

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", 
             response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED
             )
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)) -> dict:
    """Initialize db query to create new user.

    :param body: Data for creating new user.
    :type body: UserModel
    :param background_tasks: BackgroundTasks to sent email background.
    :type background_tasks: BackgroundTasks
    :param request: Request to get url from.
    :type request: Request
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :raises HTTPException: If user with such email already exists.
    :return: Dictionary with newly created user and message.
    :rtype: dict
    """    
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    """Initialize db query to login user with specific data.

    :param body: Credentials data to login usesr, defaults to Depends()
    :type body: OAuth2PasswordRequestForm, optional
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :raises HTTPException: If user with such email does not exist.
    :raises HTTPException: If user has not confirmed his email.
    :raises HTTPException: If passwird is not correct.
    :return: Dictionary with access_token, refresh_token and token_type.
    :rtype: dict
    """    

    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get('/refresh_token', 
            response_model=TokenModel,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> dict:
    """Refresh token for specific user.

    :param credentials: Credentials to update token, defaults to Security(security)
    :type credentials: HTTPAuthorizationCredentials, optional
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :raises HTTPException: If user's refresh_token is not equal token from request.
    :return: Dictionary with access_token, refresh_token and token_type.
    :rtype: dict
    """    
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    """Confirmes email in user profile.

    :param token: Token to confirm email.
    :type token: str
    :param db: The database session, defaults to Depends(get_db).
    :type db: Session, optional
    :raises HTTPException: If user with such email does not exist.
    :return: Dictionary with message.
    :rtype: dict
    """    
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))]
             )
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)) -> dict:
    """Sends email for email confirmation.

    :param body: Email to confirm.
    :type body: RequestEmail
    :param background_tasks: BackgroundTasks to sent email background.
    :type background_tasks: BackgroundTasks
    :param request: Request to get url from.
    :type request: Request
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :return: Dictionary with message.
    :rtype: dict
    """    
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)) -> User:
    """Gets information about user.

    :param current_user: User to get information about, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :return: User.
    :rtype: User
    """    
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)) -> User:
    """Initialize db query to update user's avatar.

    :param file: File to update, defaults to File()
    :type file: UploadFile, optional
    :param current_user: User to avatar update, defaults to Depends(auth_service.get_current_user)
    :type current_user: User, optional
    :param db: The database session, defaults to Depends(get_db)
    :type db: Session, optional
    :return: User with updated avatar.
    :rtype: User
    """     
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user