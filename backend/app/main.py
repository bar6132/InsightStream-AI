from fastapi import FastAPI, BackgroundTasks
from qdrant_client.http.models import Distance, VectorParams
from .core.database import supabase, qdrant
from .services.ai_engine import ai_engine
from .services.ingestion import ingestion_service
from .routers import auth, profile, news

app = FastAPI(title="InsightStream AI API")

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(news.router)

@app.on_event("startup")
async def init_db():
    """
    פונקציה שרצה אוטומטית כשהשרת עולה.
    יוצרת את ה-Collection ב-Qdrant אם הוא לא קיים.
    """
    try:
        collections = qdrant.get_collections()
        exists = any(c.name == "news_vectors" for c in collections.collections)
        
        if not exists:
            print("📦 Creating new Qdrant collection...")
            qdrant.create_collection(
                collection_name="news_vectors",
                # הגדרנו 3072 לפי הבדיקה שעשית (Google Gemini Embedding)
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
            )
            print("✅ Qdrant Collection 'news_vectors' created successfully!")
        else:
            print("INFO: Qdrant collection already exists.")
            
    except Exception as e:
        print(f"⚠️ DB Init Warning: {e}")
        
        
@app.get("/")
async def health_check():
    """
    בדיקת בריאות פשוטה.
    עצם זה שהצלחנו לייבא את supabase ו-qdrant מלמעלה,
    אומר שההגדרות נטענו בהצלחה.
    """
    return {
        "status": "online",
        "project": "InsightStream AI",
        "version": "0.1.0",
        "system": "All Systems Go 🚀" 
    }
    
@app.get("/test-ai")
async def test_ai_capabilities():
    """
    בדיקה מעמיקה ל-AI כולל רשימת מודלים זמינים
    """
    report = {}
    
    # 1. בדיקת Groq (סיכום)
    try:
        summary = await ai_engine.summarize_article("Artificial Intelligence is transforming the world...")
        report["groq_status"] = "✅ Working"
        report["groq_response"] = summary[:50] + "..."
    except Exception as e:
        report["groq_status"] = f"❌ Failed: {str(e)}"

    # 2. בדיקת Google (וקטורים)
    try:
        # בדיקה 1: נסיון רגיל
        vector = ai_engine.get_embedding("Hello World")
        report["google_status"] = "✅ Working"
        report["embedding_length"] = len(vector)
    except Exception as e:
        report["google_status"] = f"❌ Failed: {str(e)}"
        
        # דיאגנוסטיקה: שליפת רשימת המודלים הזמינים מהחשבון שלך
        try:
            available_models = []
            for m in ai_engine.google_client.models.list():
                # נחפש רק מודלים של Embedding
                if "embed" in m.name:
                    available_models.append(m.name)
            report["available_embedding_models"] = available_models
        except Exception as list_error:
            report["list_models_error"] = str(list_error)

    return report

@app.post("/trigger-ingestion")
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Endpoint ידני להפעלת האיסוף.
    משתמש ב-BackgroundTasks כדי לא לתקוע את השרת.
    """
    background_tasks.add_task(ingestion_service.run_pipeline)
    return {"status": "Ingestion started in background ⏳"}


@app.get("/debug-qdrant")
async def debug_qdrant():
    """
    בדיקה מהירה: כמה וקטורים יש לנו באמת בתוך Qdrant?
    """
    try:
        # בדיקת מידע על הקולקשיין
        collection_info = qdrant.get_collection("news_vectors")
        count = collection_info.points_count
        
        # בדיקת וקטור אחד לדוגמה (כדי לראות את הגודל שלו)
        sample = qdrant.scroll(
            collection_name="news_vectors",
            limit=1,
            with_vectors=True
        )
        
        vector_size = "No vectors found"
        if sample[0]:
            # בדיקת גודל הוקטור הראשון שנמצא
            vector_size = len(sample[0][0].vector)

        return {
            "status": "Checking Qdrant 🧐",
            "total_vectors": count,
            "vector_dimension_in_db": vector_size,
            "expected_dimension": 3072 # מה שהגדרנו בקוד
        }
    except Exception as e:
        return {"error": str(e)}