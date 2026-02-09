import os
from supabase import create_client, Client
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# 1. טעינת משתני הסביבה מקובץ .env
load_dotenv()

# 2. הגדרת Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  CRITICAL WARNING: Supabase credentials missing in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = None
if SUPABASE_SERVICE_ROLE_KEY:
    supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    print("✅ Admin client initialized (User limits active)")
else:
    print("⚠️ WARNING: No Service Role Key found. User limits will not work.")
    
# 3. הגדרת Qdrant
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

print(f"🔌 Connecting to Qdrant at: {QDRANT_URL}") # לוג שיעזור לנו להבין לאן הוא מתחבר

if QDRANT_URL:
    qdrant = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60 # הגדלת זמן ההמתנה למניעת ניתוקים
    )
else:
    print("⚠️  CRITICAL WARNING: QDRANT_URL missing in .env")
    qdrant = None