import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "valorant_teammates.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Bảng đồng đội
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teammates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT NOT NULL,
        tagline TEXT NOT NULL,
        role TEXT NOT NULL,
        main_agent TEXT NOT NULL,
        rank_tier TEXT NOT NULL DEFAULT 'Unranked',
        rating_type TEXT NOT NULL DEFAULT 'duo_buddy',
        tags TEXT NOT NULL DEFAULT '[]',
        discord TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        matches_played INTEGER NOT NULL DEFAULT 1,
        win_rate INTEGER NOT NULL DEFAULT 50,
        is_favorite INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Bảng Hồ sơ của chính bạn
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY DEFAULT 1,
        game_name TEXT NOT NULL DEFAULT 'MeValorant',
        tagline TEXT NOT NULL DEFAULT 'VN1',
        role TEXT NOT NULL DEFAULT 'Controller',
        main_agent TEXT NOT NULL DEFAULT 'Omen',
        rank_tier TEXT NOT NULL DEFAULT 'Diamond',
        win_rate INTEGER NOT NULL DEFAULT 62,
        matches_played INTEGER NOT NULL DEFAULT 45,
        bio TEXT DEFAULT 'Tay to gánh team, tìm cạ cứng leo Radiant!',
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()

    # Khởi tạo dữ liệu hồ sơ cá nhân nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM user_profile")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO user_profile (id, game_name, tagline, role, main_agent, rank_tier, win_rate, matches_played, bio, updated_at)
        VALUES (1, 'ValorantPlayer', 'VN1', 'Controller', 'Omen', 'Ascendant', 65, 52, 'Chuyên viên smoke hỗ trợ và clutch round. Đang tìm cạ cứng leo rank!', ?)
        """, (now,))
        conn.commit()

    # Seed sample teammates if table is empty
    cursor.execute("SELECT COUNT(*) FROM teammates")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_sample_data(conn)
    
    conn.close()

def get_user_profile() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "id": 1,
        "game_name": "ValorantPlayer",
        "tagline": "VN1",
        "role": "Controller",
        "main_agent": "Omen",
        "rank_tier": "Ascendant",
        "win_rate": 65,
        "matches_played": 52,
        "bio": "Chuyên viên smoke gánh team!",
        "updated_at": datetime.now().isoformat()
    }

def update_user_profile(data: dict) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    updates = []
    params = []
    fields = ["game_name", "tagline", "role", "main_agent", "rank_tier", "win_rate", "matches_played", "bio"]

    for f in fields:
        if f in data and data[f] is not None:
            updates.append(f"{f} = ?")
            params.append(data[f])

    updates.append("updated_at = ?")
    params.append(now)

    query = f"UPDATE user_profile SET {', '.join(updates)} WHERE id = 1"
    cursor.execute(query, params)
    conn.commit()
    conn.close()

    return get_user_profile()

def seed_sample_data(conn: sqlite3.Connection):
    sample_teammates = [
        (
            "ViperQueen", "VN1", "Controller", "Viper", "Ascendant", "carry",
            json.dumps(["Lineup", "Clutch God", "Chill"]),
            "viperqueen#8899",
            "Lineup Breeze và Icebox siêu đỉnh. Vòng 12 1v3 cứu cả trận đấu.",
            14, 78, 1,
            datetime.now().isoformat(), datetime.now().isoformat()
        ),
        (
            "TenZ_Fake", "007", "Duelist", "Jett", "Diamond", "duo_buddy",
            json.dumps(["Entry", "OP God", "Aim To"]),
            "tenzfake#1234",
            "Tay rất to, dash vào site dọn sạch defenders. Rất chịu nghe theo IGL.",
            22, 65, 1,
            datetime.now().isoformat(), datetime.now().isoformat()
        ),
        (
            "SovaDartGuy", "VIET", "Initiator", "Sova", "Platinum", "good_comms",
            json.dumps(["Lineup", "IGL", "Support"]),
            "sovadart#5566",
            "Mũi tên quét ra hết vị trí địch. Callout chuẩn từng miligiây.",
            9, 67, 0,
            datetime.now().isoformat(), datetime.now().isoformat()
        ),
        (
            "ChamberRich", "FLEX", "Sentinel", "Chamber", "Immortal", "carry",
            json.dumps(["Lurker", "OP God", "Headhunter"]),
            "richguy#9999",
            "Bắn Headhunter như hack. Giữ flank cực an toàn, luôn gánh round súng lục.",
            18, 72, 1,
            datetime.now().isoformat(), datetime.now().isoformat()
        ),
        (
            "HealMeBro", "Troll", "Sentinel", "Sage", "Gold", "avoid",
            json.dumps(["Troll", "No Mic"]),
            "",
            "Sage battle chạy lên trước chết sớm, xin heal không cho, né gấp!",
            3, 33, 0,
            datetime.now().isoformat(), datetime.now().isoformat()
        ),
        (
            "CloveSimp", "UWU", "Controller", "Clove", "Platinum", "chill",
            json.dumps(["Aggressive Smoke", "Support", "Friendly"]),
            "clovesimp#0404",
            "Chết vẫn smoke hỗ trợ nhiệt tình, không bao giờ tilt dù thua ngược.",
            11, 55, 0,
            datetime.now().isoformat(), datetime.now().isoformat()
        )
    ]

    cursor = conn.cursor()
    cursor.executemany("""
    INSERT INTO teammates (
        game_name, tagline, role, main_agent, rank_tier, rating_type,
        tags, discord, notes, matches_played, win_rate, is_favorite,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_teammates)
    conn.commit()

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    d["is_favorite"] = bool(d["is_favorite"])
    try:
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
    except Exception:
        d["tags"] = []
    return d

def get_all_teammates(
    search: Optional[str] = None,
    role: Optional[str] = None,
    rank_tier: Optional[str] = None,
    rating_type: Optional[str] = None,
    is_favorite: Optional[bool] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM teammates WHERE 1=1"
    params = []

    if search:
        query += " AND (game_name LIKE ? OR tagline LIKE ? OR main_agent LIKE ? OR notes LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    if role and role != "All":
        query += " AND role = ?"
        params.append(role)

    if rank_tier and rank_tier != "All":
        query += " AND rank_tier = ?"
        params.append(rank_tier)

    if rating_type and rating_type != "All":
        query += " AND rating_type = ?"
        params.append(rating_type)

    if is_favorite is not None:
        query += " AND is_favorite = ?"
        params.append(1 if is_favorite else 0)

    query += " ORDER BY is_favorite DESC, updated_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result

def get_teammate_by_id(teammate_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teammates WHERE id = ?", (teammate_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row_to_dict(row)
    return None

def create_teammate(data: dict) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    tags_str = json.dumps(data.get("tags", []))

    cursor.execute("""
    INSERT INTO teammates (
        game_name, tagline, role, main_agent, rank_tier, rating_type,
        tags, discord, notes, matches_played, win_rate, is_favorite,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["game_name"].strip(),
        data["tagline"].strip(),
        data["role"],
        data["main_agent"],
        data.get("rank_tier", "Unranked"),
        data.get("rating_type", "duo_buddy"),
        tags_str,
        data.get("discord", "").strip(),
        data.get("notes", "").strip(),
        data.get("matches_played", 1),
        data.get("win_rate", 50),
        1 if data.get("is_favorite", False) else 0,
        now,
        now
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_teammate_by_id(new_id)

def update_teammate(teammate_id: int, data: dict) -> Optional[Dict[str, Any]]:
    existing = get_teammate_by_id(teammate_id)
    if not existing:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    updates = []
    params = []

    field_mappings = [
        "game_name", "tagline", "role", "main_agent", "rank_tier",
        "rating_type", "discord", "notes", "matches_played", "win_rate"
    ]

    for field in field_mappings:
        if field in data and data[field] is not None:
            updates.append(f"{field} = ?")
            params.append(data[field])

    if "tags" in data and data["tags"] is not None:
        updates.append("tags = ?")
        params.append(json.dumps(data["tags"]))

    if "is_favorite" in data and data["is_favorite"] is not None:
        updates.append("is_favorite = ?")
        params.append(1 if data["is_favorite"] else 0)

    updates.append("updated_at = ?")
    params.append(now)

    params.append(teammate_id)
    query = f"UPDATE teammates SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()

    return get_teammate_by_id(teammate_id)

def toggle_favorite(teammate_id: int) -> Optional[Dict[str, Any]]:
    existing = get_teammate_by_id(teammate_id)
    if not existing:
        return None
    new_fav = not existing["is_favorite"]
    return update_teammate(teammate_id, {"is_favorite": new_fav})

def delete_teammate(teammate_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teammates WHERE id = ?", (teammate_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM teammates")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teammates WHERE is_favorite = 1")
    favs = cursor.fetchone()[0]

    cursor.execute("SELECT role, COUNT(*) as count FROM teammates GROUP BY role")
    role_dist = {row["role"]: row["count"] for row in cursor.fetchall()}

    cursor.execute("SELECT rank_tier, COUNT(*) as count FROM teammates GROUP BY rank_tier")
    rank_dist = {row["rank_tier"]: row["count"] for row in cursor.fetchall()}

    cursor.execute("SELECT rating_type, COUNT(*) as count FROM teammates GROUP BY rating_type")
    rating_dist = {row["rating_type"]: row["count"] for row in cursor.fetchall()}

    most_common_role = "None"
    if role_dist:
        most_common_role = max(role_dist, key=role_dist.get)

    conn.close()
    return {
        "total_teammates": total,
        "favorites_count": favs,
        "role_distribution": role_dist,
        "rank_distribution": rank_dist,
        "rating_distribution": rating_dist,
        "most_common_role": most_common_role
    }
