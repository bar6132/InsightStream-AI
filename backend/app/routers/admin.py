from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import get_current_user
from ..core.database import supabase, supabase_admin, qdrant

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

# --- 🛡️ Security Check ---
def check_admin(user):
    """
    בודק האם למשתמש הנוכחי יש הרשאת 'admin'.
    אם לא - זורק שגיאה 403.
    """
    # שליפת התפקיד מטבלת ההעדפות
    response = supabase.table("user_preferences").select("role").eq("user_id", user.id).execute()
    
    if not response.data:
        raise HTTPException(status_code=403, detail="User profile not found")
        
    role = response.data[0].get("role")
    if role != 'admin':
        print(f"⚠️ Unauthorized admin access attempt by: {user.email}")
        raise HTTPException(status_code=403, detail="Access denied: Admins only")
    
    return True

# --- 👥 User Management ---

@router.get("/users")
async def list_users(user = Depends(get_current_user)):
    """
    מחזיר את רשימת כל המשתמשים (כולל מיילים ומזהים).
    """
    check_admin(user)
    try:
        # שימוש ב-Service Role כדי לשלוף את כל המשתמשים מ-Auth
        users = supabase_admin.auth.admin.list_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, user = Depends(get_current_user)):
    """
    מחיקת משתמש מהמערכת (Ban).
    """
    check_admin(user)
    try:
        # מחיקה ממערכת האימות (Auth)
        supabase_admin.auth.admin.delete_user(user_id)
        
        # מחיקה מטבלת הפרופילים (למקרה שאין Cascade)
        supabase_admin.table("user_preferences").delete().eq("user_id", user_id).execute()
        
        return {"status": "success", "message": f"User {user_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/make-admin")
async def make_user_admin(user_id: str, user = Depends(get_current_user)):
    """
    הופך משתמש רגיל לאדמין.
    """
    check_admin(user)
    try:
        supabase_admin.table("user_preferences").update({"role": "admin"}).eq("user_id", user_id).execute()
        return {"status": "success", "message": f"User {user_id} is now an Admin"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 🧹 Data Management ---

@router.delete("/data/articles")
async def clear_all_articles(user = Depends(get_current_user)):
    """
    ⚠️ סכנה: מוחק את כל הכתבות מהמערכת (Supabase + Qdrant).
    שימושי לניקוי לפני השקה מחדש.
    """
    check_admin(user)
    try:
        # 1. מחיקה מ-Supabase
        supabase_admin.table("news_articles").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # 2. מחיקה מ-Qdrant (מחיקת הקולקציה ויצירה מחדש זה הכי נקי)
        try:
            qdrant.delete_collection("news_vectors")
            # יצירה מחדש (חשוב!)
            qdrant.create_collection(
                collection_name="news_vectors",
                vectors_config={"size": 768, "distance": "Cosine"} # וודא שזה הגודל הנכון למודל שלך!
            )
        except Exception as q_err:
            print(f"Qdrant cleanup warning: {q_err}")

        return {"status": "success", "message": "All articles and vectors wiped clean."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def system_stats(user = Depends(get_current_user)):
    """
    סטטיסטיקות כלליות למערכת.
    """
    check_admin(user)
    try:
        # ספירת משתמשים
        users_count = supabase_admin.table("user_preferences").select("*", count="exact").execute().count
        
        # ספירת כתבות
        articles_count = supabase_admin.table("news_articles").select("*", count="exact").execute().count
        
        return {
            "total_users": users_count,
            "total_articles": articles_count,
            "system_status": "Healthy 🟢"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))