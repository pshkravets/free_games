import secrets

from fastapi import FastAPI, status, Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from free_games_email.models import User
from free_games_email.database import Base, engine, get_db
from free_games_email.utils import email_validation, password_validation, hash_password
from free_games_email.security import api_key_auth

app = FastAPI(debug=True)
Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post('/signup/')
def signup(email: str, passwd1: str, passwd2: str, db: Session = Depends(get_db)):
    if email_validation(email) and password_validation(passwd1, passwd2):
        user = User(
            email=email,
            password=hash_password(passwd1),
            api_key=secrets.token_hex(32)
        )
        db.add(user)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={'email': user.email, 'api_key': user.api_key}
        )

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail='You input invalid email or password don\'t match'
    )


@router.get('/get_api_key/')
def get_api_key(email: str, passwd: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with this email was not found'
        )
    if user.check_passwd(passwd):
        return {'api_key': user.api_key}
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Wrong password'
    )


@router.post('/enable_notifications/', dependencies=[Depends(api_key_auth)])
def enable_notifications(user: User = Depends(api_key_auth), db: Session = Depends(get_db)):
    user.email_notifications = True
    db.add(user)
    db.commit()
    return {
        'message': 'Email notifications for free games were enabled'
    }


@app.post('/disable_notifications/', dependencies=[Depends(api_key_auth)])
def disable_notifications(user: User = Depends(api_key_auth), db: Session = Depends(get_db)):
    user.email_notifications = False
    db.add(user)
    db.commit()
    return {
        'message': 'Email notifications for free games were disabled'
    }


app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)