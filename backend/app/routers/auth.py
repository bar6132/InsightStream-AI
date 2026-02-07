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

@router.post("/login", response_model=Token)
async def login(user: UserAuth):
    """
    התחברות למערכת וקבלת JWT Token.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })

        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer",
            "user_id": response.user.id,
            "email": response.user.email
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail="Login failed. Check email/password.")