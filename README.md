# InsightStream AI 🚀

**InsightStream AI** is an intelligent news aggregator platform that leverages Generative AI to deliver a hyper-personalized news feed. The system collects articles in real-time from RSS sources, summarizes them using **Llama 3**, and performs **Semantic Search** based on vector embeddings to match content with user interests.

![Status](https://img.shields.io/badge/Status-Active_Development-green)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

## ✨ Key Features

* **🔄 Automated Ingestion:** Continuous fetching of articles from top RSS sources (TechCrunch, The Verge, Wired, etc.).
* **🧠 AI Summarization:** Utilizes **Llama 3** (via Groq Cloud) to generate concise and accurate summaries of long-form articles.
* **💎 Vector Database & Embeddings:** Converts text into vector embeddings using **Google Gemini** and stores them in **Qdrant** for semantic understanding.
* **🎯 Smart Personalization:** Users define interests (tags), and the system matches articles based on meaning and context, not just keywords.
* **🔒 Secure Authentication:** Robust user management and authentication using **Supabase Auth** with JWT protection.

---

## 🛠️ Tech Stack & Architecture

### Backend (Server)
* **Language:** Python 3.10
* **Framework:** FastAPI (High performance, async)
* **AI Engine:**
    * **Summarization:** Groq Cloud (Llama 3-8b-8192)
    * **Embeddings:** Google Gemini (embedding-001)
* **Databases:**
    * **Relational:** Supabase (PostgreSQL) - User management, article metadata, user preferences.
    * **Vector:** Qdrant - Storing high-dimensional vectors for semantic search.
* **Parsing:** `feedparser`, `BeautifulSoup`

### Infrastructure
* **Containerization:** Docker & Docker Compose for consistent environments.

### Frontend (Coming Soon 🚧)
* **Framework:** Next.js 16
* **Styling:** Tailwind CSS

---

## 📂 Project Structure

```bash
InsightStream-AI/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py       # Environment variables management
│   │   │   └── database.py     # Database connections (Supabase & Qdrant)
│   │   ├── routers/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── news.py         # Personalized feed generation
│   │   │   └── profile.py      # User preferences (Tags) management
│   │   ├── services/
│   │   │   ├── ai_engine.py    # Logic for Groq and Gemini interactions
│   │   │   └── ingestion.py    # The RSS Crawler pipeline
│   │   ├── schemas/            # Pydantic models for data validation
│   │   ├── dependencies.py     # Auth Middleware & JWT Verification
│   │   └── main.py             # Server entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # (Under construction - Next.js 16)
├── docker-compose.yml          # Orchestration for Backend + Qdrant
├── .gitignore
└── README.md
```
## 🚀 Installation & Setup

### Prerequisites
* **Docker** & **Docker Compose** installed.
* API Keys/Credentials for: **Supabase**, **Groq**, **Google Gemini**.

### 1. Clone the Repository
```bash
git clone [https://github.com/bar6132/InsightStream-AI.git](https://github.com/bar6132/InsightStream-AI.git)
cd InsightStream-AI
```
### 2. Environment Configuration (.env)
```bash
# Database & Auth (Supabase)
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_anon_key"

# AI Services
GROQ_API_KEY="your_groq_api_key"
GOOGLE_API_KEY="your_google_gemini_key"

# Vector Database (Qdrant)
# When running via Docker Compose, the service name is 'qdrant'
QDRANT_URL="http://qdrant:6333"
QDRANT_API_KEY=""
```
### 3. Build and Run
* Use Docker Compose to spin up the backend server and the Qdrant database:
```bash
docker-compose up --build
```
* API Server: http://localhost:8000
* Swagger Documentation: http://localhost:8000/docs

## 📖 API Workflow Guide
** To test the system using the built-in Swagger UI: **

### 1. Authentication (Sign Up):
* Use POST /auth/signup to create a new user.
* Note: Ensure email confirmation is disabled in Supabase for development, or verify the email link sent.
  
### 2. Login:
* Use POST /auth/login.
* Copy the returned access_token.
* Click the Authorize (🔒) button at the top of Swagger and paste the token (format: Bearer <token> or just <token> if using HTTPBearer).
  
### 3. Set Preferences:
* Send a request to POST /profile/preferences with your tags.
  ```bash
  {
  "tags": ["AI", "Cyber Security", "Python"]
  }  
  ```
### 4. Trigger Ingestion:
* Run POST /trigger-ingestion.
* The system will scrape RSS feeds, summarize articles via AI, vectorize them, and store them in the DB. (Check terminal logs for progress).

### 5. Get Personalized Feed:
* Run GET /news/feed.
* The system will return articles ranked by relevance to your defined tags using vector similarity.

