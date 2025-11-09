from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from random import randint
from typing import Any

app = FastAPI(root_path="/api/v1")

# Data dummy
data = [
    {
        "campaign_id": 1,
        "name": "kanjut",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaign_id": 2,
        "name": "badag",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/campaign")
async def get_campaigns():
    """Mengambil semua campaign"""
    return {"campaigns": data}


@app.get("/campaign/{id}")
async def get_campaign(id: int):
    """Mengambil campaign berdasarkan ID"""
    for campaign in data:
        if campaign["campaign_id"] == id:
            return {"campaign": campaign}
    # 🔴 Dulu kamu return HTTPException langsung (salah),
    # yang benar harus pakai `raise`
    raise HTTPException(status_code=404, detail="Campaign not found")


@app.post("/campaign")
async def create_campaign(body: dict[str, Any]):
    """Membuat campaign baru"""
    new_campaign = {
        "campaign_id": randint(100, 10000),
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        "created_at": datetime.now(),
    }

    data.append(new_campaign)
    return {"campaign": new_campaign}
