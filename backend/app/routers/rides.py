from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Ride, Payment, RideStatus
from app.schemas import EstimateRequest, EstimateResponse, RideCreateRequest, RideResponse
from app.auth import get_current_user
from app.services.maps import maps_service
from app.services.payments import payment_service
from app.socket_server import sio

router = APIRouter(prefix="/api/rides", tags=["rides"])

@router.post("/estimate", response_model=EstimateResponse)
async def get_estimate(req: EstimateRequest):
    try:
        distance, duration = maps_service.get_route_details(
            req.pickup_lat, req.pickup_lng, req.drop_lat, req.drop_lng
        )
        fare = maps_service.calculate_fare(distance, duration)
        return EstimateResponse(
            distance_meters=distance,
            duration_seconds=duration,
            fare_estimate=fare
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/request", response_model=RideResponse)
async def create_ride(
    req: RideCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    distance, duration = maps_service.get_route_details(
        req.pickup_lat, req.pickup_lng, req.drop_lat, req.drop_lng
    )
    fare = maps_service.calculate_fare(distance, duration)

    ride = Ride(
        rider_id=current_user.id,
        pickup_lat=req.pickup_lat,
        pickup_lng=req.pickup_lng,
        drop_lat=req.drop_lat,
        drop_lng=req.drop_lng,
        fare_estimate=fare,
        distance_meters=distance,
        duration_seconds=duration,
        status=RideStatus.REQUESTED
    )
    db.add(ride)
    await db.commit()
    await db.refresh(ride)

    intent_id = payment_service.create_intent(fare, ride.id)
    payment = Payment(
        ride_id=ride.id,
        stripe_payment_intent_id=intent_id,
        amount=fare,
        status="requires_payment_method"
    )
    db.add(payment)
    await db.commit()

    await sio.emit("new_ride_available", {
        "ride_id": ride.id,
        "pickup": [req.pickup_lat, req.pickup_lng],
        "drop": [req.drop_lat, req.drop_lng],
        "fare": fare
    })

    return ride

@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride_status(ride_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalar_one_or_none()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride