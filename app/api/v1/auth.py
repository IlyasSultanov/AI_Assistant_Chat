from fastapi import APIRouter, Depends

from app.jwtauth import utils as auth_utils
from app.schemas.userschema import UserSchema, TokenInfo
from app.service.auth_service import validate_auth_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenInfo)
async def login(user: UserSchema = Depends(validate_auth_user)):
    jwt_payload = {
        "sub": user.username,
        "name": user.username,
        "email": user.email,
    }
    access_token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(access_token=access_token, token_type="bearer")


@router.get("/logout/me")
async def logout_me(user: UserSchema = Depends(get_current_active_user)):
    return {"sub": user.username, "email": user.email}