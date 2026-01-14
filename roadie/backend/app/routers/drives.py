from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2 import functions as gf
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models import User, Drive, RoutePoint
from app.schemas import (
    DriveCreate,
    DriveUpdate,
    DriveResponse,
    DriveSummary,
    RoutePointCreate,
    StatsResponse
)
from app.dependencies import get_current_user
from shapely.geometry import Point
from geopy.distance import geodesic

router = APIRouter()


def calculate_distance(points: List[RoutePointCreate]) -> float:
    """Calculate total distance in meters"""
    if len(points) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(1, len(points)):
        point1 = (points[i-1].latitude, points[i-1].longitude)
        point2 = (points[i].latitude, points[i].longitude)
        distance = geodesic(point1, point2).meters
        total_distance += distance
    
    return total_distance


def calculate_stats(points: List[RoutePointCreate]) -> dict:
    """Calculate drive statistics"""
    if not points:
        return {
            "distance": 0.0,
            "duration": 0,
            "average_speed": 0.0,
            "max_speed": 0.0
        }
    
    distance = calculate_distance(points)
    
    start_time = points[0].timestamp
    end_time = points[-1].timestamp
    duration = int((end_time - start_time).total_seconds())
    
    speeds = [p.speed for p in points if p.speed is not None and p.speed > 0]
    average_speed = sum(speeds) / len(speeds) if speeds else 0.0
    max_speed = max(speeds) if speeds else 0.0
    
    return {
        "distance": distance,
        "duration": duration,
        "average_speed": average_speed,
        "max_speed": max_speed
    }


@router.post("", response_model=DriveResponse, status_code=status.HTTP_201_CREATED)
async def create_drive(
    drive_data: DriveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Calculate statistics if route points provided
    stats = {}
    if drive_data.route_points:
        stats = calculate_stats(drive_data.route_points)
    
    # Create start location
    start_location = None
    if drive_data.route_points:
        first_point = drive_data.route_points[0]
        start_location = f"POINT({first_point.longitude} {first_point.latitude})"
    
    # Create drive
    drive = Drive(
        user_id=current_user.id,
        name=drive_data.name,
        start_time=drive_data.start_time,
        distance=stats.get("distance", 0.0),
        duration=stats.get("duration", 0),
        average_speed=stats.get("average_speed", 0.0),
        max_speed=stats.get("max_speed", 0.0),
        start_location=start_location
    )
    
    db.add(drive)
    db.flush()  # Get drive.id
    
    # Add route points
    if drive_data.route_points:
        for point_data in drive_data.route_points:
            route_point = RoutePoint(
                drive_id=drive.id,
                latitude=point_data.latitude,
                longitude=point_data.longitude,
                altitude=point_data.altitude,
                speed=point_data.speed,
                timestamp=point_data.timestamp,
                sequence=point_data.sequence
            )
            db.add(route_point)
    
    db.commit()
    db.refresh(drive)
    
    return drive


@router.get("", response_model=List[DriveSummary])
async def get_drives(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    drives = db.query(Drive).filter(
        Drive.user_id == current_user.id
    ).order_by(
        Drive.start_time.desc()
    ).offset(skip).limit(limit).all()
    
    return drives


@router.get("/{drive_id}", response_model=DriveResponse)
async def get_drive(
    drive_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    drive = db.query(Drive).filter(
        Drive.id == drive_id,
        Drive.user_id == current_user.id
    ).first()
    
    if not drive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drive not found"
        )
    
    return drive


@router.patch("/{drive_id}", response_model=DriveResponse)
async def update_drive(
    drive_id: UUID,
    drive_update: DriveUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    drive = db.query(Drive).filter(
        Drive.id == drive_id,
        Drive.user_id == current_user.id
    ).first()
    
    if not drive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drive not found"
        )
    
    # Update fields
    if drive_update.name is not None:
        drive.name = drive_update.name
    if drive_update.end_time is not None:
        drive.end_time = drive_update.end_time
    if drive_update.distance is not None:
        drive.distance = drive_update.distance
    if drive_update.duration is not None:
        drive.duration = drive_update.duration
    if drive_update.average_speed is not None:
        drive.average_speed = drive_update.average_speed
    if drive_update.max_speed is not None:
        drive.max_speed = drive_update.max_speed
    
    # Update route points if provided
    if drive_update.route_points:
        # Delete existing route points
        db.query(RoutePoint).filter(RoutePoint.drive_id == drive_id).delete()
        
        # Add new route points
        stats = calculate_stats(drive_update.route_points)
        drive.distance = stats.get("distance", drive.distance)
        drive.duration = stats.get("duration", drive.duration)
        drive.average_speed = stats.get("average_speed", drive.average_speed)
        drive.max_speed = stats.get("max_speed", drive.max_speed)
        
        # Update end location
        if drive_update.route_points:
            last_point = drive_update.route_points[-1]
            drive.end_location = f"POINT({last_point.longitude} {last_point.latitude})"
        
        for point_data in drive_update.route_points:
            route_point = RoutePoint(
                drive_id=drive.id,
                latitude=point_data.latitude,
                longitude=point_data.longitude,
                altitude=point_data.altitude,
                speed=point_data.speed,
                timestamp=point_data.timestamp,
                sequence=point_data.sequence
            )
            db.add(route_point)
    
    db.commit()
    db.refresh(drive)
    
    return drive


@router.delete("/{drive_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drive(
    drive_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    drive = db.query(Drive).filter(
        Drive.id == drive_id,
        Drive.user_id == current_user.id
    ).first()
    
    if not drive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drive not found"
        )
    
    db.delete(drive)
    db.commit()
    
    return None


@router.get("/stats/summary", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    drives = db.query(Drive).filter(Drive.user_id == current_user.id).all()
    
    total_drives = len(drives)
    total_distance = sum(d.distance for d in drives)
    total_duration = sum(d.duration for d in drives)
    average_distance = total_distance / total_drives if total_drives > 0 else 0.0
    average_duration = total_duration / total_drives if total_drives > 0 else 0.0
    
    return StatsResponse(
        total_drives=total_drives,
        total_distance=total_distance,
        total_duration=total_duration,
        average_distance=average_distance,
        average_duration=average_duration
    )

