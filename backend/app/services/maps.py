import googlemaps
from app.config import settings

class MapsService:
    def __init__(self):
        if settings.GOOGLE_MAPS_API_KEY != "google_key_placeholder":
            self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        else:
            self.client = None

    def get_route_details(self, p_lat: float, p_lng: float, d_lat: float, d_lng: float):
        if not self.client:
            import math
            R = 6371000
            phi1, phi2 = math.radians(p_lat), math.radians(d_lat)
            dphi = math.radians(d_lat - p_lat)
            dlambda = math.radians(d_lng - p_lng)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            meters = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            seconds = int((meters / 1000) / 30 * 3600)
            return meters, max(seconds, 60)

        result = self.client.distance_matrix(
            origins=[(p_lat, p_lng)],
            destinations=[(d_lat, d_lng)],
            mode="driving"
        )
        element = result["rows"][0]["elements"][0]
        if element["status"] != "OK":
            raise ValueError("Unable to calculate route via Google Maps")
        return element["distance"]["value"], element["duration"]["value"]

    def calculate_fare(self, distance_meters: float, duration_seconds: int) -> float:
        base_fare = 2.50
        per_km_rate = 1.20
        per_min_rate = 0.25
        distance_km = distance_meters / 1000.0
        duration_minutes = duration_seconds / 60.0
        return round(base_fare + (distance_km * per_km_rate) + (duration_minutes * per_min_rate), 2)

maps_service = MapsService()
