# from fastapi import APIRouter, Depends, HTTPException
# from ..dependencies import get_current_user
# from ..core.database import supabase, qdrant
# from ..services.ai_engine import ai_engine

# router = APIRouter(prefix="/news", tags=["News"])

# @router.get("/feed")
# async def get_personalized_feed(user = Depends(get_current_user)):
#     """
#     הלב של המערכת: מחזיר פיד חדשות מותאם אישית.
#     1. שולף את התגיות של המשתמש.
#     2. ממיר אותן לווקטור.
#     3. מוצא כתבות רלוונטיות ב-Qdrant.
#     """
#     try:
#         # 1. שליפת התגיות של המשתמש
#         user_pref = supabase.table("user_preferences").select("tags").eq("user_id", user.id).execute()
        
#         tags = []
#         if user_pref.data and user_pref.data[0].get("tags"):
#             tags = user_pref.data[0]["tags"]
        
#         # אם למשתמש אין תגיות, נחזיר כתבות כלליות (או ריק)
#         if not tags:
#             return {"message": "No interests defined yet", "articles": []}

#         # 2. יצירת וקטור חיפוש מתוך התגיות (למשל: "AI Tech Coding")
#         search_query = " ".join(tags)
#         print(f"🔍 Searching for: {search_query}")
        
#         query_vector = ai_engine.get_embedding(search_query)

#         # 3. חיפוש סמנטי ב-Qdrant
#         search_result = qdrant.search(
#             collection_name="news_vectors",
#             query_vector=query_vector,
#             limit=10  # מחזיר את 10 הכתבות הכי רלוונטיות
#         )

#         # 4. פרמוט התוצאות ל-JSON יפה
#         articles = []
#         for hit in search_result:
#             articles.append({
#                 "id": hit.id,
#                 "score": hit.score, # עד כמה זה מתאים (0 עד 1)
#                 "title": hit.payload.get("title"),
#                 "url": hit.payload.get("url"),
#                 "source": hit.payload.get("source"),
#                 "summary": hit.payload.get("summary", "No summary available") 
#             })

#         return {"feed": articles}

#     except Exception as e:
#         print(f"Error fetching feed: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch news feed")
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from ..core.database import supabase, qdrant
from ..services.ai_engine import ai_engine

router = APIRouter(prefix="/news", tags=["News"])

@router.get("/feed")
async def get_personalized_feed(user = Depends(get_current_user)):
    try:
        # 1. שליפת תגיות (נשאר אותו דבר)
        user_pref = supabase.table("user_preferences").select("tags").eq("user_id", user.id).execute()
        
        tags = []
        if user_pref.data and user_pref.data[0].get("tags"):
            tags = user_pref.data[0]["tags"]
        
        if not tags:
            tags = ["Technology", "AI"]
            print("⚠️ No tags found using default: Technology, AI")

        # 2. יצירת וקטור (נשאר אותו דבר)
        search_query = " ".join(tags)
        print(f"🔍 Searching for: {search_query}")
        query_vector = ai_engine.get_embedding(search_query)

        # 3. חיפוש ב-Qdrant (השינוי הגדול!)
        # במקום search, אנחנו משתמשים ב-query_points
        search_result = qdrant.query_points(
            collection_name="news_vectors",
            query=query_vector, # הפרמטר נקרא עכשיו 'query' ולא 'query_vector'
            limit=10
        )
        
        # התוצאה מגיעה בתוך אובייקט שמכיל רשימה בשם points
        points = search_result.points
        print(f"✅ Found {len(points)} articles")

        # 4. פרמוט התוצאות
        articles = []
        for hit in points: # רצים על points
            articles.append({
                "id": hit.id,
                "score": hit.score,
                "title": hit.payload.get("title"),
                "url": hit.payload.get("url"),
                "source": hit.payload.get("source"),
                "summary": hit.payload.get("summary", "No summary available") 
            })

        return {"feed": articles}

    except Exception as e:
        print(f"❌ Error fetching feed: {e}")
        # במקרה של שגיאה, נדפיס את הפרטים המלאים לטרמינל
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch news feed")