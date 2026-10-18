from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EstimateRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float

class EstimateResponse(BaseModel):
    distance_meters: float
    duration_seconds: int
    fare_estimate: float

class RideCreateRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float

class RideResponse(BaseModel):
    id: int
    rider_id: int
    driver_id: Optional[int] = None
    status: str
    fare_estimate: float
    distance_meters: float
    duration_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True

class DriverLocationUpdate(BaseModel):
    lat: float
    lng: float

class DriverStatusUpdate(BaseModel):
    is_active: bool
