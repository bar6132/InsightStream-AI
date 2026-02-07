from pydantic import BaseModel, EmailStr, Field

class UserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="סיסמה באורך 6 תווים לפחות")

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str