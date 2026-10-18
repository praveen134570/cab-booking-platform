from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
import math
from app.database import get_db
from app.models import Driver, Ride, RideStatus
from app.schemas import DriverLocationUpdate
from app.auth import get_current_user
from app.socket_server import sio

router = APIRouter(prefix="/api/drivers", tags=["drivers"])

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@router.post("/location")
async def update_location(
    loc: DriverLocationUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await db.execute(
        update(Driver)
        .where(Driver.user_id == current_user.id)
        .values(current_lat=loc.lat, current_lng=loc.lng)
    )
    await db.commit()
    return {"status": "success"}

@router.get("/nearby")
async def get_nearby_drivers(lat: float, lng: float, radius_km: float = 5.0, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Driver).where(Driver.is_active == True))
    active_drivers = result.scalars().all()

    nearby = []
    for d in active_drivers:
        if d.current_lat is not None and d.current_lng is not None:
            dist = haversine(lat, lng, d.current_lat, d.current_lng)
            if dist <= radius_km * 1000:
                nearby.append({
                    "id": d.id,
                    "user_id": d.user_id,
                    "vehicle_info": d.vehicle_info,
                    "distance": round(dist, 1)
                })

    nearby.sort(key=lambda x: x["distance"])
    return nearby

@router.post("/rides/{ride_id}/accept")
async def accept_ride(
    ride_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Driver).where(Driver.user_id == current_user.id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=403, detail="User is not registered as a driver")

    ride_res = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = ride_res.scalar_one_or_none()
    if not ride or ride.status != RideStatus.REQUESTED:
        raise HTTPException(status_code=400, detail="Ride is no longer available")

    ride.driver_id = driver.id
    ride.status = RideStatus.ACCEPTED
    await db.commit()

    await sio.emit("ride_status_updated", {"ride_id": ride_id, "status": RideStatus.ACCEPTED}, room=f"ride_{ride_id}")
    return {"status": "accepted"}