from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    drives = relationship("Drive", back_populates="user", cascade="all, delete-orphan")


class Drive(Base):
    __tablename__ = "drives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    distance = Column(Float, default=0.0)  # in meters
    duration = Column(Integer, default=0)  # in seconds
    average_speed = Column(Float, default=0.0)  # in km/h
    max_speed = Column(Float, default=0.0)  # in km/h
    start_location = Column(Geometry("POINT", srid=4326), nullable=True)
    end_location = Column(Geometry("POINT", srid=4326), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="drives")
    route_points = relationship("RoutePoint", back_populates="drive", cascade="all, delete-orphan", order_by="RoutePoint.sequence")


class RoutePoint(Base):
    __tablename__ = "route_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drive_id = Column(UUID(as_uuid=True), ForeignKey("drives.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)  # in km/h
    timestamp = Column(DateTime, nullable=False)
    sequence = Column(Integer, nullable=False)  # order in route

    drive = relationship("Drive", back_populates="route_points")

