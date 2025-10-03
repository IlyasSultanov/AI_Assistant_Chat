from fastapi import APIRouter


router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """
    Проверка состояния сервиса.
    
    Returns:
        dict: Статус сервиса {"status": "ok"}
    """
    return {"status": "ok"}