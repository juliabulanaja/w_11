from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings
from src.database.models import User


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password:str, hashed_password: str) -> bool:
        """Verifies if plain_password has hash equal hashed_password

        :param plain_password: Plain password to check.
        :type plain_password: str
        :param hashed_password: Hashed password to compare with.
        :type hashed_password: str
        :return: Returns True if plain password has hash equal hashed_password or False if not.
        :rtype: bool
        """    
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Get hash string from password.

        :param password: Password to get hash from.
        :type password: str
        :return: Hash string from password.
        :rtype: str
        """        
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """Creates new ACCESS token with specific data and specific time.

        :param data: Data to create token with.
        :type data: dict
        :param expires_delta: Seconds to new token will work, defaults to None
        :type expires_delta: Optional[float], optional
        :return: Newly created ACCESS token.
        :rtype: str
        """        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """Creates new REFRESH token with specific data and specific time.

        :param data: Data to create token with.
        :type data: dict
        :param expires_delta: Seconds to new token will work, defaults to None
        :type expires_delta: Optional[float], optional
        :return: Newly created REFRESH token.
        :rtype: str
        """        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """Gets email from refresh token.

        :param refresh_token: Refresh token to decode.
        :type refresh_token: str
        :raises HTTPException: If scope is not equal 'refresh_token'.
        :raises HTTPException: If credentiales are not valid.
        :return: Email from refresh token.
        :rtype: str
        """        
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """Get user from token.

        :param token: Token to get user from, defaults to Depends(oauth2_scheme)
        :type token: str, optional
        :param db: The database session, defaults to Depends(get_db)
        :type db: Session, optional
        :raises credentials_exception: If credentiales are not valid.
        :raises credentials_exception: If scope is not equal 'access_token'.
        :raises credentials_exception: If there are no email in data.
        :raises credentials_exception: If user does not exist.
        :return: User from token.
        :rtype: User
        """        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user
    

    def create_email_token(self, data: dict) -> str:
        """Creates token for email service.

        :param data: Data to create token with.
        :type data: dict
        :return: Newly created token.
        :rtype: str
        """        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    

    async def get_email_from_token(self, token: str) -> str:
        """Gets email from specific token

        :param token: Token to get email from.
        :type token: str
        :raises HTTPException: Invalid token for email verification
        :return: Email
        :rtype: str
        """        
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()