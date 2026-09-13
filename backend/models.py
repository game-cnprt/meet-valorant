from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TeammateBase(BaseModel):
    game_name: str = Field(..., min_length=1, max_length=50, description="Tên trong game (Riot ID)")
    tagline: str = Field(..., min_length=1, max_length=10, description="Tagline Riot (ví dụ: VN1, NA1)")
    role: str = Field(..., description="Vai trò chính: Duelist, Initiator, Controller, Sentinel")
    main_agent: str = Field(..., description="Đặc vụ tủ (Jett, Omen, Sova, Cypher, ...)")
    rank_tier: str = Field(default="Unranked", description="Bậc xếp hạng: Iron, Bronze, Silver, Gold, Platinum, Diamond, Ascendant, Immortal, Radiant, Unranked")
    rating_type: str = Field(default="duo_buddy", description="Đánh giá: carry, good_comms, duo_buddy, chill, avoid")
    tags: List[str] = Field(default_factory=list, description="Thẻ phong cách chơi: Entry, Lurker, IGL, Lineup, Op God, Chill...")
    discord: Optional[str] = Field(default="", description="Tài khoản Discord hoặc liên hệ")
    notes: Optional[str] = Field(default="", description="Ghi chú trận đấu, kỷ niệm hoặc kinh nghiệm")
    matches_played: int = Field(default=1, ge=0, description="Số trận đã chơi cùng nhau")
    win_rate: int = Field(default=50, ge=0, le=100, description="Tỉ lệ thắng ước tính (%)")
    is_favorite: bool = Field(default=False, description="Đánh dấu cạ cứng (ghim lên đầu)")

class TeammateCreate(TeammateBase):
    pass

class TeammateUpdate(BaseModel):
    game_name: Optional[str] = None
    tagline: Optional[str] = None
    role: Optional[str] = None
    main_agent: Optional[str] = None
    rank_tier: Optional[str] = None
    rating_type: Optional[str] = None
    tags: Optional[List[str]] = None
    discord: Optional[str] = None
    notes: Optional[str] = None
    matches_played: Optional[int] = None
    win_rate: Optional[int] = None
    is_favorite: Optional[bool] = None

class TeammateResponse(TeammateBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class UserProfileModel(BaseModel):
    game_name: str
    tagline: str
    role: str
    main_agent: str
    rank_tier: str
    win_rate: int
    matches_played: int
    bio: Optional[str] = ""

class UserProfileUpdate(BaseModel):
    game_name: Optional[str] = None
    tagline: Optional[str] = None
    role: Optional[str] = None
    main_agent: Optional[str] = None
    rank_tier: Optional[str] = None
    win_rate: Optional[int] = None
    matches_played: Optional[int] = None
    bio: Optional[str] = None

class StatsResponse(BaseModel):
    total_teammates: int
    favorites_count: int
    role_distribution: dict
    rank_distribution: dict
    rating_distribution: dict
    most_common_role: str
