"""
Vercel Serverless Handler for FastAPI
"""
import sys
sys.path.insert(0, '.')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 创建 FastAPI 应用
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from api.market import router as market_router
from api.signals import router as signals_router

app.include_router(market_router, prefix="/api")
app.include_router(signals_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "name": "Crypto AI Signal Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "market": "/api/market",
            "signals": "/api/signals",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
def health():
    return {"status": "healthy"}

# Vercel handler
handler = app
