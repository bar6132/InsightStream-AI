from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .core.database import supabase

# רכיב האבטחה שמוסיף את המנעול ל-Swagger
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    פונקציה זו רצה לפני כל בקשה מוגנת.
    היא מחלצת את הטוקן אוטומטית ומאמתת אותו מול Supabase.
    """
    token = credentials.credentials # מקבל את הטוקן נקי (בלי המילה Bearer)

    try:
        user = supabase.auth.get_user(token)
        
        if not user or not user.user:
             raise HTTPException(status_code=401, detail="Invalid Token")
             
        return user.user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token"
        )