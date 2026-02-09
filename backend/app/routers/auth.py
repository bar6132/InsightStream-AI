from fastapi import APIRouter, HTTPException, status
from ..core.database import supabase
from ..schemas.user import UserAuth, Token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(user: UserAuth):
    """
    הרשמה של משתמש חדש למערכת.
    """
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        
        if not response.user:
            raise HTTPException(status_code=400, detail="Registration failed")
            
        return {"message": "User created successfully", "user_id": response.user.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.post("/login", response_model=Token)
# async def login(user: UserAuth):
#     """
#     התחברות למערכת וקבלת JWT Token.
#     """
#     try:
#         response = supabase.auth.sign_in_with_password({
#             "email": user.email,
#             "password": user.password
#         })

#         if not response.session:
#             raise HTTPException(status_code=401, detail="Invalid credentials")

#         return {
#             "access_token": response.session.access_token,
#             "token_type": "bearer",
#             "user_id": response.user.id,
#             "email": response.user.email
#         }

#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Login failed. Check email/password.")
# בתוך auth_router.py או main.py (איפה שפונקציית ה-login נמצאת)

# בתוך auth_router.py

@router.post("/login")
async def login(credentials: UserAuth): # שימוש ב-Schema שהגדרת
    try:
        # 1. התחברות ל-Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        user_id = auth_response.user.id
        
        # 2. שליפת ה-Role וה-Tags מטבלת ה-user_preferences שלך
        # הטבלה שראינו בתמונות ששלחת
        pref_response = supabase.table("user_preferences") \
            .select("role, tags") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        # חילוץ הנתונים (עם fallback למקרה שאין עדיין שורה בטבלה)
        role = pref_response.data.get("role", "user") if pref_response.data else "user"
        tags = pref_response.data.get("tags", []) if pref_response.data else []

        # 3. החזרת המבנה שה-Frontend שלנו מצפה לו
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": auth_response.user.email,
            "role": role,
            "tags": tags
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))