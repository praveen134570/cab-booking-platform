from fastapi import APIRouter, Request, Header, HTTPException, Depends
import stripe
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models import Payment, Ride, RideStatus, User
from app.celery_worker import generate_and_send_receipt
from app.socket_server import sio

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook verification failed: {str(e)}")

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        ride_id = int(intent["metadata"]["ride_id"])

        res = await db.execute(select(Payment).where(Payment.ride_id == ride_id))
        payment = res.scalar_one_or_none()
        if payment:
            payment.status = "succeeded"

            ride_res = await db.execute(select(Ride).where(Ride.id == ride_id))
            ride = ride_res.scalar_one_or_none()
            if ride:
                ride.status = RideStatus.COMPLETED
                user_res = await db.execute(select(User).where(User.id == ride.rider_id))
                user = user_res.scalar_one_or_none()
                if user:
                    generate_and_send_receipt.delay(ride.id, payment.amount, user.email)

            await db.commit()
            await sio.emit("ride_status_updated", {"ride_id": ride_id, "status": RideStatus.COMPLETED}, room=f"ride_{ride_id}")

    return {"status": "success"}
