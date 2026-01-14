from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class RoutePointCreate(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    timestamp: datetime
    sequence: int


class RoutePointResponse(BaseModel):
    id: UUID
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    timestamp: datetime
    sequence: int

    class Config:
        from_attributes = True


class DriveBase(BaseModel):
    name: Optional[str] = None
    start_time: datetime


class DriveCreate(DriveBase):
    route_points: Optional[List[RoutePointCreate]] = []


class DriveUpdate(BaseModel):
    name: Optional[str] = None
    end_time: Optional[datetime] = None
    distance: Optional[float] = None
    duration: Optional[int] = None
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None
    route_points: Optional[List[RoutePointCreate]] = []


class DriveResponse(DriveBase):
    id: UUID
    user_id: UUID
    end_time: Optional[datetime] = None
    distance: float
    duration: int
    average_speed: float
    max_speed: float
    start_location: Optional[dict] = None
    end_location: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    route_points: List[RoutePointResponse] = []

    class Config:
        from_attributes = True


class DriveSummary(BaseModel):
    id: UUID
    name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    distance: float
    duration: int
    average_speed: float
    max_speed: float
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_drives: int
    total_distance: float  # in meters
    total_duration: int  # in seconds
    average_distance: float
    average_duration: float

