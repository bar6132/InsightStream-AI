from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from ..dependencies import get_current_user
from ..core.database import supabase

router = APIRouter(prefix="/profile", tags=["Profile"])

# מודל לקבלת רשימת תגיות מהמשתמש
class UserTags(BaseModel):
    tags: List[str]

@router.post("/preferences")
async def update_preferences(preferences: UserTags, user = Depends(get_current_user)):
    """
    שמירה או עדכון של תחומי העניין של המשתמש.
    דורש טוקן התחברות!
    """
    try:
        user_id = user.id
        
        # שימוש ב-upsert: אם קיים - מעדכן, אם לא - יוצר חדש
        data = {
            "user_id": user_id,
            "tags": preferences.tags
        }
        
        result = supabase.table("user_preferences").upsert(data).execute()
        return {"message": "Preferences updated successfully", "tags": preferences.tags}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/preferences")
async def get_preferences(user = Depends(get_current_user)):
    """
    שליפת התגיות של המשתמש המחובר
    """
    try:
        user_id = user.id
        response = supabase.table("user_preferences").select("tags").eq("user_id", user_id).execute()
        
        if not response.data:
            return {"tags": []}
            
        return response.data[0]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))