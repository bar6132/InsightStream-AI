from fastapi import FastAPI
from qdrant_client.http.models import Distance, VectorParams
from .core.database import supabase, qdrant
from .services.ai_engine import ai_engine
from .services.queue import publish_ingestion_task
from .routers import auth, profile, news, admin, health
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="InsightStream AI API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://100.78.219.101:3000",
    "http://100.78.219.101",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # מאפשר את כל ה-Methods (GET, POST, OPTIONS וכו')
    allow_headers=["*"], # מאפשר את כל ה-Headers (כולל Authorization)
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(news.router)
app.include_router(admin.router)
app.include_router(health.router)

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
async def trigger_ingestion():
    """
    Publishes a scrape job to the RabbitMQ queue.
    The worker container picks it up and runs the pipeline asynchronously.
    """
    await publish_ingestion_task({"task": "scrape_all"})
    return {"status": "Job queued ⏳ — worker will process it shortly"}


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