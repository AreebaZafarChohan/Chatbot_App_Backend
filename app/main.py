from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.websocket import router as websocket_router

app = FastAPI()

# ---- CORS middleware ----
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://chatbot-app-9tbq.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Include routers ----
app.include_router(websocket_router)

@app.get("/")
def home():
    return {"message": "Backend is running ✅"}
