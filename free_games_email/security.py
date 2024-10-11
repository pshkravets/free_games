from free_games_email.database import get_db
from free_games_email.models import User

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def api_key_auth(api_key: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(api_key=api_key).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API key'
        )
    return user
