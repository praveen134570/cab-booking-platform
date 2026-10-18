import socketio
from app.config import settings

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    client_manager=socketio.AsyncRedisManager(settings.REDIS_URL) if settings.REDIS_URL else None
)

@sio.event
async def connect(sid, environ):
    pass

@sio.event
async def join_ride(sid, data):
    ride_id = data.get("ride_id")
    sio.enter_room(sid, f"ride_{ride_id}")

@sio.event
async def driver_location(sid, data):
    ride_id = data.get("ride_id")
    lat = data.get("lat")
    lng = data.get("lng")
    await sio.emit("location_update", {"lat": lat, "lng": lng}, room=f"ride_{ride_id}", skip_sid=sid)

@sio.event
async def disconnect(sid):
    pass
