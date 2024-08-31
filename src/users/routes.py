from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime
from src.db.main import get_session
from .schemas import UserModel, UserCreateModel, UserLoginModel
from .service import UserService
from .utils import create_access_token, decode_access_token, verify_password
from .dependencies import RefreshTokenBearer


users_router = APIRouter()
users_service = UserService()

REFRESH_TOKEN_EXPIRY = 2


@users_router.post(
    '/signup',
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED
)
async def create_user_account(
        user_data: UserCreateModel,
        session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    user_exists = await users_service.user_exist(email, session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists")

    new_user = await users_service.create_user(user_data, session)
    return new_user


@users_router.post(
    '/login',
)
async def login_user(
        login_data: UserLoginModel,
        session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await users_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                }
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    'message': 'Login successful',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user:': {
                        'email': user.email,
                        'uid': str(user.uid)
                    }
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid email or password"
    )


@users_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(content={
            "access_token": new_access_token
        })

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details="Invalid or expired token")
