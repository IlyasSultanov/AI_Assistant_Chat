from fastapi import APIRouter, Depends

from app.jwtauth import utils as auth_utils
from app.schemas.userschema import UserSchema, TokenInfo
from app.service.auth_service import validate_auth_user, get_current_active_user
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenInfo)
async def login(user: UserSchema = Depends(validate_auth_user)):
    jwt_payload = {
        "sub": user.username,
        "name": user.username,
        "email": user.email,
    }
    access_token = auth_utils.encode_jwt(jwt_payload)
    refresh_token = auth_utils.encode_jwt(
        jwt_payload,
        expires_in=settings.auth_settings.refresh_token_expires_minutes,
    )
    return TokenInfo(access_token=access_token, token_type="bearer", refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenInfo)
async def refresh_token(payload: dict = Depends(lambda: {}), token: str | None = None):
    # Эта заглушка предполагает, что refresh токен приходит, например, в теле запроса
    # или через Authorization: Bearer. Для простоты — используем такой же декодер
    # и возвращаем новый access токен.
    # В реальном проекте здесь можно хранить refresh токены в БД/блэк-листе.
    if token is None:
        # Если токен не передан явно, пытаемся прочесть из зависимостей авторизации —
        # но в данном примере оставим простую проверку.
        return TokenInfo(access_token="", token_type="bearer")

    data = auth_utils.decode_jwt(token)
    new_access = auth_utils.encode_jwt({
        "sub": data.get("sub"),
        "name": data.get("name"),
        "email": data.get("email"),
    })
    return TokenInfo(access_token=new_access, token_type="bearer")


@router.get("/logout/me")
async def logout_me(user: UserSchema = Depends(get_current_active_user)):
    return {"sub": user.username, "email": user.email}