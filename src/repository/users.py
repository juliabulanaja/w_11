
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """Retrieves user with specific email.

    :param email: Email to retrieve the user.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: _description_
    :rtype: User with specific email.
    :rtype: User | None
    """ 
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """Creates a new user.

    :param body: The data for the user to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """    
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """Updates refresh token.

    :param user: User whom refresh token update
    :type user: User
    :param token: New refresh token.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """    
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """Makes users email confirmed.

    :param email: Email should be confirmed.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """    
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """Updates avatar for user with specific email.

    :param email: Users email for whom avatar should be updated.
    :type email: str
    :param url: Avatar path.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: User with updated avatar.
    :rtype: User
    """    
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
    