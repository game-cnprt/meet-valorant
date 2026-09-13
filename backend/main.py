from fastapi import FastAPI, HTTPException, Query, Header, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from dotenv import load_dotenv

from models import TeammateCreate, TeammateUpdate, TeammateResponse, StatsResponse, UserProfileModel, UserProfileUpdate
import database
import riot_service

# Load .env file
load_dotenv()

app = FastAPI(
    title="MeetValorant API (HenrikDev Powered)",
    description="API quản lý và lưu trữ thông tin đồng đội Valorant sử dụng HenrikDev API",
    version="2.0.0"
)

# Allow CORS for Vue frontend dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def root():
    return {
        "app": "MeetValorant API (HenrikDev Powered)",
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/api/stats", response_model=StatsResponse)
def get_stats():
    return database.get_stats()

@app.get("/api/profile")
def get_profile():
    """Lấy thông tin Hồ Sơ Cá Nhân của bạn"""
    return database.get_user_profile()

@app.put("/api/profile")
def update_profile(payload: UserProfileUpdate):
    """Cập nhật thông tin Hồ Sơ Cá Nhân của bạn"""
    update_data = payload.model_dump(exclude_unset=True)
    return database.update_user_profile(update_data)

@app.get("/api/teammates", response_model=List[TeammateResponse])
def list_teammates(
    q: Optional[str] = Query(None, description="Tìm kiếm theo tên, tag, đặc vụ, ghi chú"),
    role: Optional[str] = Query(None, description="Lọc theo Role (Duelist, Initiator, Controller, Sentinel)"),
    rank_tier: Optional[str] = Query(None, description="Lọc theo Rank tier"),
    rating_type: Optional[str] = Query(None, description="Lọc theo Đánh giá"),
    is_favorite: Optional[bool] = Query(None, description="Chỉ lấy cạ cứng được đánh dấu sao")
):
    return database.get_all_teammates(
        search=q,
        role=role,
        rank_tier=rank_tier,
        rating_type=rating_type,
        is_favorite=is_favorite
    )

@app.get("/api/teammates/{teammate_id}", response_model=TeammateResponse)
def get_teammate(teammate_id: int):
    mate = database.get_teammate_by_id(teammate_id)
    if not mate:
        raise HTTPException(status_code=404, detail="Không tìm thấy đồng đội")
    return mate

@app.post("/api/teammates", response_model=TeammateResponse, status_code=status.HTTP_201_CREATED)
def create_teammate(payload: TeammateCreate):
    created = database.create_teammate(payload.model_dump())
    return created

@app.put("/api/teammates/{teammate_id}", response_model=TeammateResponse)
def update_teammate(teammate_id: int, payload: TeammateUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    updated = database.update_teammate(teammate_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy đồng đội để cập nhật")
    return updated

@app.post("/api/teammates/{teammate_id}/toggle-favorite", response_model=TeammateResponse)
def toggle_favorite(teammate_id: int):
    updated = database.toggle_favorite(teammate_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy đồng đội")
    return updated

@app.delete("/api/teammates/{teammate_id}")
def delete_teammate(teammate_id: int):
    success = database.delete_teammate(teammate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy đồng đội để xóa")
    return {"message": "Đã xóa đồng đội thành công", "id": teammate_id}

@app.get("/api/henrik/account/{game_name}/{tagline}")
async def search_henrik_account(game_name: str, tagline: str):
    """
    Endpoint tra cứu tài khoản Valorant qua HenrikDev API
    """
    result = await riot_service.fetch_account_info(game_name, tagline)
    if not result["success"]:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])
    return result

@app.get("/api/henrik/matches/{game_name}/{tagline}")
async def fetch_henrik_matches(game_name: str, tagline: str, region: str = Query("ap", description="Server region: ap, na, eu, kr")):
    """
    Endpoint tra cứu trận đấu & trích xuất toàn bộ player vừa gặp qua HenrikDev API
    """
    result = await riot_service.fetch_recent_matches_and_players(game_name, tagline, region)
    if not result["success"]:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])
    return result

@app.post("/api/henrik/import-teammates/{game_name}/{tagline}")
async def import_all_teammates(game_name: str, tagline: str, region: str = Query("ap", description="Server region: ap, na, eu, kr")):
    """
    Endpoint tự động quét các trận đấu mới nhất và LƯU TẤT CẢ ĐỒNG ĐỘI (Teammates) vào cơ sở dữ liệu SQLite!
    """
    result = await riot_service.import_all_teammates_from_matches(game_name, tagline, region)
    if not result["success"]:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])
    return result

@app.post("/api/seed")
def reseed_sample():
    conn = database.get_connection()
    database.seed_sample_data(conn)
    conn.close()
    return {"message": "Đã nạp lại dữ liệu mẫu"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
