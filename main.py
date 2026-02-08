from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import sys
sys.path.insert(0, '.')

app = FastAPI()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
