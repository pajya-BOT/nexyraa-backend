from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router
from app.api.scan import router as scan_router
from app.api.compare import router as compare_router
app = FastAPI(title="Nexyraa API")

# ✅ THIS IS THE FIX (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all frontends (safe for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Nexyraa Premium Backend Running"}

app.include_router(analyze_router)
app.include_router(scan_router)
app.include_router(compare_router)   
