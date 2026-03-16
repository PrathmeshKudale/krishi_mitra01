# 🌾 Krishi Mitra v2 — AI Farming Assistant

> Upgraded from Streamlit → **FastAPI + Beautiful HTML/JS Frontend**

## Why We Ditched Streamlit

| Feature | Streamlit (Old) | FastAPI + HTML (New) |
|---|---|---|
| UI Quality | Generic/Plain | Custom, beautiful, mobile-friendly |
| Performance | Slow (Python re-runs) | Fast REST API |
| Mobile Support | Poor | Fully responsive |
| Language Switcher | Basic | Hindi/Marathi/English inline |
| Customization | Very Limited | Unlimited |
| Database | None | SQLite → PostgreSQL |
| Scalability | Single-user | Multi-user API |

---

## 🏗️ Project Structure

```
krishi-mitra/
├── backend/
│   ├── main.py          # FastAPI app with all routes
│   ├── database.py      # SQLAlchemy + SQLite/PostgreSQL
│   ├── models.py        # ORM models (User, Chat, Crops, etc.)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── ai_service.py    # Google Gemini AI integration
│   └── requirements.txt
│
└── frontend/
    └── index.html       # Complete single-file website
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API will be at: `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

### 2. Frontend

Simply open `frontend/index.html` in a browser.

For production, serve with any static hosting:
```bash
# Simple Python server
python -m http.server 3000 --directory frontend

# Or use nginx, Vercel, Netlify etc.
```

---

## 🗄️ Database

**Development**: SQLite (`krishi_mitra.db`) — zero configuration needed.

**Production (PostgreSQL)**:
```bash
export DATABASE_URL="postgresql://user:password@localhost/krishi_mitra"
```

### Database Schema

- **users** — Farmer profiles (name, phone, location, language)
- **chat_sessions** — Conversation sessions
- **chat_messages** — Full chat history
- **crop_records** — Farmer's crop tracking
- **disease_reports** — Disease diagnosis history
- **market_prices** — Price cache
- **weather_logs** — Advisory history

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | AI chat (main feature) |
| POST | `/api/users` | Create/find user |
| POST | `/api/crops` | Add crop record |
| POST | `/api/disease/analyze` | Disease diagnosis |
| GET | `/api/market/prices` | Market price insights |
| POST | `/api/weather/advisory` | Weather-based advice |
| GET | `/api/schemes` | Government schemes |

---

## 🌐 Environment Variables

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./krishi_mitra.db   # or postgresql://...
```

---

## 🌍 Languages Supported

- 🇮🇳 **English** — Default
- 🇮🇳 **Hindi** (हिंदी) — Devanagari
- 🇮🇳 **Marathi** (मराठी) — Devanagari

---

## 📱 Features

1. **AI Chat** — Multilingual farming advice powered by Gemini
2. **Crop Library** — Kharif/Rabi/Zaid crop guide with one-click advice
3. **Disease Analyzer** — Symptom-based diagnosis with treatments
4. **Market Insights** — Mandi prices, MSP info
5. **Weather Advisory** — Season and location-based guidance
6. **Government Schemes** — PM-KISAN, PMFBY, KCC and more
7. **Crop Records** — Track your farm's crop history

---

## 🔄 Migration from Old Streamlit Code

Your old `app.py` / `main_app.py` / `ai_service.py` logic maps to:

- `ai_service.py` (old) → `backend/ai_service.py` (new, enhanced)
- `database.py` (old) → `backend/models.py` + `backend/database.py`
- `app.py` (old) → `backend/main.py` (FastAPI routes) + `frontend/index.html`

---

*Built for Indian farmers 🌾 | जय किसान*
