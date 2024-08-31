from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from .schemas import UserModel, UserCreateModel, UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

from .utils import create_access_token, decode_access_token, verify_password
from datetime import timedelta

user_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2

# bearer token

@user_router.post(
    '/signup',
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED
)
async def create_user_account(
        user_data: UserCreateModel,
        session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    user_exists = await user_service.user_exist(email, session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists")

    new_user = await user_service.create_user(user_data, session)
    return new_user


@user_router.post(
    '/login',
)
async def login_user(
        login_data: UserLoginModel,
        session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
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
