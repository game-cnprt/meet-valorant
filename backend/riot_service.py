import os
import httpx
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import database
from data_helpers import get_role_from_agent

# Load .env file with explicit path to backend/.env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

def get_henrikdev_api_key() -> str:
    return os.getenv("HENRIKDEV_API_KEY", "").strip()

HENRIK_BASE_URL = "https://api.henrikdev.xyz"

def get_headers() -> dict:
    key = get_henrikdev_api_key()
    return {"Authorization": key} if key else {}

async def fetch_account_info(game_name: str, tagline: str) -> Dict[str, Any]:
    """
    Tra cứu thông tin tài khoản Valorant (Name, Tag, PUUID, Region, Level, Card Image) từ HenrikDev API.
    Endpoint: GET /valorant/v1/account/{name}/{tag}
    """
    hdev_key = get_henrikdev_api_key()
    if not hdev_key:
        return {
            "success": False,
            "status_code": 400,
            "error": "Chưa cấu hình HENRIKDEV_API_KEY trong file .env"
        }

    url = f"{HENRIK_BASE_URL}/valorant/v1/account/{game_name}/{tagline}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=get_headers())
            
            if res.status_code == 200:
                data = res.json().get("data") or {}
                puuid = data.get("puuid")
                region = data.get("region") or "ap"

                # Cố gắng lấy thêm thông tin Rank hiện tại từ HenrikDev MMR API
                rank_name = "Unranked"
                mmr_url = f"{HENRIK_BASE_URL}/valorant/v2/by-puuid/mmr/{region}/{puuid}"
                try:
                    mmr_res = await client.get(mmr_url, headers=get_headers())
                    if mmr_res.status_code == 200:
                        mmr_data = mmr_res.json().get("data") or {}
                        rank_name = (mmr_data.get("current_data") or {}).get("currenttierpatched", "Unranked")
                except Exception:
                    pass

                return {
                    "success": True,
                    "status_code": 200,
                    "puuid": puuid,
                    "game_name": data.get("name"),
                    "tagline": data.get("tag"),
                    "region": region,
                    "account_level": data.get("account_level"),
                    "rank_tier": rank_name,
                    "card_image": (data.get("card") or {}).get("small")
                }
            elif res.status_code == 404:
                return {
                    "success": False,
                    "status_code": 404,
                    "error": f"Không tìm thấy tài khoản '{game_name}#{tagline}' trên hệ thống HenrikDev API."
                }
            elif res.status_code == 401:
                return {
                    "success": False,
                    "status_code": 401,
                    "error": "HENRIKDEV_API_KEY không hợp lệ. Vui lòng kiểm tra lại key trong .env."
                }
            else:
                return {
                    "success": False,
                    "status_code": res.status_code,
                    "error": f"Lỗi từ HenrikDev API (HTTP {res.status_code})"
                }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "error": f"Không thể kết nối đến HenrikDev API: {str(e)}"
        }

async def fetch_recent_matches_and_players(game_name: str, tagline: str, region: str = "ap") -> Dict[str, Any]:
    """
    Tra cứu danh sách trận đấu vừa chơi và trích xuất TOÀN BỘ người chơi trong trận từ HenrikDev API.
    Endpoint: GET /valorant/v3/matches/{region}/{name}/{tag}
    """
    hdev_key = get_henrikdev_api_key()
    if not hdev_key:
        return {
            "success": False,
            "status_code": 400,
            "error": "Chưa cấu hình HENRIKDEV_API_KEY trong file .env"
        }

    # Lấy vùng máy chủ chính xác nếu có
    acc_res = await fetch_account_info(game_name, tagline)
    if acc_res.get("success") and acc_res.get("region"):
        region = acc_res["region"]

    url = f"{HENRIK_BASE_URL}/valorant/v3/matches/{region}/{game_name}/{tagline}"

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            res = await client.get(url, headers=get_headers())
            
            if res.status_code == 200:
                matches_raw = res.json().get("data") or []
                parsed_matches = []

                target_name_lower = game_name.lower()
                target_tag_lower = tagline.lower()

                for m in matches_raw:
                    if not m:
                        continue
                    meta = m.get("metadata") or {}
                    players_dict = m.get("players") or {}
                    players_raw = players_dict.get("all_players") or []

                    # Tìm team của user trong trận đấu
                    user_team = None
                    for p in players_raw:
                        if not p:
                            continue
                        p_name = (p.get("name") or "").lower()
                        p_tag = (p.get("tag") or "").lower()
                        if p_name == target_name_lower and p_tag == target_tag_lower:
                            user_team = p.get("team")
                            break

                    parsed_players = []
                    for p in players_raw:
                        if not p:
                            continue
                        p_name = p.get("name") or "Unknown"
                        p_tag = p.get("tag") or "000"
                        p_team = p.get("team")
                        is_me = (p_name.lower() == target_name_lower and p_tag.lower() == target_tag_lower)
                        is_teammate = bool(user_team and p_team == user_team and not is_me)

                        stats = p.get("stats") or {}
                        parsed_players.append({
                            "game_name": p_name,
                            "tagline": p_tag,
                            "puuid": p.get("puuid"),
                            "agent_name": p.get("character") or "Unknown",
                            "team": p_team,
                            "is_me": is_me,
                            "is_teammate": is_teammate,
                            "kills": stats.get("kills", 0),
                            "deaths": stats.get("deaths", 0),
                            "assists": stats.get("assists", 0),
                            "score": stats.get("score", 0)
                        })

                    parsed_matches.append({
                        "match_id": meta.get("matchid"),
                        "map": meta.get("map"),
                        "mode": meta.get("mode"),
                        "game_start": meta.get("game_start_patched"),
                        "rounds_played": meta.get("rounds_played"),
                        "players": parsed_players
                    })

                return {
                    "success": True,
                    "status_code": 200,
                    "game_name": game_name,
                    "tagline": tagline,
                    "total_matches": len(parsed_matches),
                    "matches": parsed_matches
                }
            elif res.status_code == 404:
                return {
                    "success": False,
                    "status_code": 404,
                    "error": f"Không tìm thấy lịch sử trận đấu cho '{game_name}#{tagline}' trên HenrikDev API."
                }
            else:
                return {
                    "success": False,
                    "status_code": res.status_code,
                    "error": f"Lỗi từ HenrikDev API (HTTP {res.status_code}): {res.text[:200]}"
                }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "error": f"Lỗi kết nối máy chủ API: {str(e)}"
        }

async def import_all_teammates_from_matches(game_name: str, tagline: str, region: str = "ap") -> Dict[str, Any]:
    """
    Tự động quét tất cả các trận đấu gần đây của user và LƯU TOÀN BỘ ĐỒNG ĐỘI (Teammates) vào cơ sở dữ liệu SQLite!
    """
    matches_res = await fetch_recent_matches_and_players(game_name, tagline, region)
    if not matches_res.get("success"):
        return matches_res

    matches = matches_res.get("matches", [])
    added_count = 0
    existing_count = 0
    saved_list = []

    for m in matches:
        map_name = m.get("map", "Valorant Map")
        players = m.get("players", [])
        
        for p in players:
            # Chỉ lưu đồng đội cùng team (không lưu chính mình và đối thủ)
            if not p.get("is_teammate"):
                continue

            p_name = p.get("game_name")
            p_tag = p.get("tagline")
            agent = p.get("agent_name", "Jett")
            role = get_role_from_agent(agent)

            # Kiểm tra nếu đồng đội đã có trong database chưa
            existing = database.get_all_teammates(search=p_name)
            match_found = False
            for ex in existing:
                if ex.get("game_name", "").lower() == p_name.lower() and ex.get("tagline", "").lower() == p_tag.lower():
                    # Cập nhật số trận
                    database.update_teammate(ex["id"], {
                        "matches_played": ex.get("matches_played", 1) + 1
                    })
                    existing_count += 1
                    match_found = True
                    break

            if not match_found:
                new_mate = database.create_teammate({
                    "game_name": p_name,
                    "tagline": p_tag,
                    "role": role,
                    "main_agent": agent,
                    "rank_tier": "Diamond",  # Bậc mặc định khi import từ API
                    "rating_type": "duo_buddy",
                    "tags": ["Vừa Gặp", "Tự Động Import", "Cùng Team"],
                    "discord": "",
                    "notes": f"Tự động lưu từ trận đấu map {map_name}. KDA: {p.get('kills')}/{p.get('deaths')}/{p.get('assists')}, Score: {p.get('score')}",
                    "matches_played": 1,
                    "win_rate": 60,
                    "is_favorite": False
                })
                added_count += 1
                saved_list.append(f"{p_name}#{p_tag} ({agent})")

    return {
        "success": True,
        "status_code": 200,
        "added_count": added_count,
        "existing_updated_count": existing_count,
        "total_processed": added_count + existing_count,
        "saved_teammates": saved_list
    }
