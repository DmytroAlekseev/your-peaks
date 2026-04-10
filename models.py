from pydantic import BaseModel
from typing import Optional, List


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class Mountain(BaseModel):
    id: str
    name: str
    elevation_m: int
    lat: float
    lon: float
    oblast: str
    raion: str
    climbed: bool = False
    climbed_at: Optional[str] = None


class ClimbToggle(BaseModel):
    notes: Optional[str] = None


class GoalToggle(BaseModel):
    pass


class ProfileResponse(BaseModel):
    username: str
    email: str
    total_mountains: int
    climbed_count: int
    climbed_percent: float
    climbed_mountains: List[Mountain]
