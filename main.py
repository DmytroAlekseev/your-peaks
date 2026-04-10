"""
Твої Вершини — MVP backend
Run: python main.py
Then open: http://localhost:8000
"""

from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import auth
import database
import utils
from models import ClimbToggle, UserCreate, UserLogin

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(title="Твої Вершини", version="1.0.0")

database.init_db()

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/auth/register")
def register(user: UserCreate):
    if database.get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = auth.hash_password(user.password)
    database.create_user(user.username, user.email, hashed)
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "username": user.username}


@app.post("/api/auth/login")
def login(user: UserLogin):
    db_user = database.get_user_by_username(user.username)
    if not db_user or not auth.verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "username": user.username}


# ── Mountains ─────────────────────────────────────────────────────────────────

@app.get("/api/mountains")
def get_mountains(
    search: Optional[str] = None,
    mountain_system: Optional[str] = None,
    oblast: Optional[str] = None,
    raion: Optional[str] = None,
    min_elevation: Optional[int] = None,
    max_elevation: Optional[int] = None,
    current_user: dict = Depends(auth.get_current_user),
):
    all_mountains = [dict(m) for m in utils.load_mountains()]
    filtered = utils.filter_mountains(all_mountains, search, mountain_system, oblast, raion, min_elevation, max_elevation)

    climbed = database.get_climbed_ids(current_user["id"])
    goals = database.get_goal_ids(current_user["id"])
    for m in filtered:
        if m["id"] in climbed:
            m["climbed"] = True
            m["climbed_at"] = climbed[m["id"]]["climbed_at"]
        else:
            m["climbed"] = False
            m["climbed_at"] = None
        if m["id"] in goals:
            m["goal"] = True
            m["goal_added_at"] = goals[m["id"]]["added_at"]
        else:
            m["goal"] = False
            m["goal_added_at"] = None

    return filtered


@app.get("/api/mountains/meta")
def get_meta(current_user: dict = Depends(auth.get_current_user)):
    return {
        "mountain_systems": utils.get_all_mountain_systems(),
        "oblasts": utils.get_all_oblasts(),
        "raions": utils.get_all_raions(),
        "total": len(utils.load_mountains()),
    }


# ── Climbed ───────────────────────────────────────────────────────────────────

@app.post("/api/climbed/{mountain_id}")
def mark_climbed(
    mountain_id: str,
    body: ClimbToggle = ClimbToggle(),
    current_user: dict = Depends(auth.get_current_user),
):
    if not utils.get_mountain_by_id(mountain_id):
        raise HTTPException(status_code=404, detail="Mountain not found")
    database.add_climbed(current_user["id"], mountain_id, body.notes)
    return {"status": "climbed"}


@app.delete("/api/climbed/{mountain_id}")
def unmark_climbed(
    mountain_id: str,
    current_user: dict = Depends(auth.get_current_user),
):
    database.remove_climbed(current_user["id"], mountain_id)
    return {"status": "unclimbed"}


# ── Goal ──────────────────────────────────────────────────────────────────────

@app.post("/api/goal/{mountain_id}")
def mark_goal(
    mountain_id: str,
    current_user: dict = Depends(auth.get_current_user),
):
    if not utils.get_mountain_by_id(mountain_id):
        raise HTTPException(status_code=404, detail="Mountain not found")
    database.add_goal(current_user["id"], mountain_id)
    return {"status": "goal"}


@app.delete("/api/goal/{mountain_id}")
def unmark_goal(
    mountain_id: str,
    current_user: dict = Depends(auth.get_current_user),
):
    database.remove_goal(current_user["id"], mountain_id)
    return {"status": "ungoal"}


# ── Profile ───────────────────────────────────────────────────────────────────

@app.get("/api/profile")
def get_profile(current_user: dict = Depends(auth.get_current_user)):
    all_mountains = utils.load_mountains()
    climbed_map = database.get_climbed_ids(current_user["id"])
    goal_map = database.get_goal_ids(current_user["id"])

    climbed_count = len(climbed_map)
    # goals that are NOT yet climbed
    pending_goal_count = len([gid for gid in goal_map if gid not in climbed_map])
    # total goals = climbed + pending goals
    total_goal_count = climbed_count + pending_goal_count
    goal_climbed_percent = round(climbed_count / total_goal_count * 100, 1) if total_goal_count > 0 else 0.0

    climbed_mountains = []
    for m in all_mountains:
        if m["id"] in climbed_map:
            entry = dict(m)
            entry["climbed"] = True
            entry["climbed_at"] = climbed_map[m["id"]]["climbed_at"]
            entry["goal"] = m["id"] in goal_map
            climbed_mountains.append(entry)

    climbed_mountains.sort(key=lambda x: x["elevation_m"], reverse=True)

    goal_mountains = []
    for m in all_mountains:
        if m["id"] in goal_map and m["id"] not in climbed_map:
            entry = dict(m)
            entry["climbed"] = False
            entry["goal"] = True
            entry["goal_added_at"] = goal_map[m["id"]]["added_at"]
            goal_mountains.append(entry)

    goal_mountains.sort(key=lambda x: x["elevation_m"], reverse=True)

    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "climbed_count": climbed_count,
        "pending_goal_count": pending_goal_count,
        "total_goal_count": total_goal_count,
        "goal_climbed_percent": goal_climbed_percent,
        "climbed_mountains": climbed_mountains,
        "goal_mountains": goal_mountains,
    }


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
