"use client";

import React, { useState, useEffect } from "react";
import { socket } from "@/lib/socket";
import { Car, Navigation, DollarSign, Clock, ShieldCheck, MapPin } from "lucide-react";

interface Estimate {
  distance_meters: number;
  duration_seconds: number;
  fare_estimate: number;
}

export default function BookingPortal() {
  const [pickup, setPickup] = useState({ lat: 37.7749, lng: -122.4194 });
  const [drop, setDrop] = useState({ lat: 37.7849, lng: -122.4094 });
  const [estimate, setEstimate] = useState<Estimate | null>(null);
  const [rideId, setRideId] = useState<number | null>(null);
  const [rideStatus, setRideStatus] = useState<string>("IDLE");
  const [driverLoc, setDriverLoc] = useState<{ lat: number; lng: number } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    socket.connect();

    socket.on("ride_status_updated", (data: { ride_id: number; status: string }) => {
      if (data.ride_id === rideId) {
        setRideStatus(data.status);
      }
    });

    socket.on("location_update", (coords: { lat: number; lng: number }) => {
      setDriverLoc(coords);
    });

    return () => {
      socket.disconnect();
    };
  }, [rideId]);

  const fetchEstimate = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/rides/estimate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pickup_lat: pickup.lat,
          pickup_lng: pickup.lng,
          drop_lat: drop.lat,
          drop_lng: drop.lng
        })
      });
      const data = await res.json();
      setEstimate(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const requestRide = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/rides/request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer dev_mock_token"
        },
        body: JSON.stringify({
          pickup_lat: pickup.lat,
          pickup_lng: pickup.lng,
          drop_lat: drop.lat,
          drop_lng: drop.lng
        })
      });
      const ride = await res.json();
      setRideId(ride.id);
      setRideStatus(ride.status);
      socket.emit("join_ride", { ride_id: ride.id });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <Car className="h-7 w-7 text-indigo-400" />
            <h1 className="text-xl font-bold">Ride-Hailing Dispatch</h1>
          </div>
          <span className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-1 rounded-full">
            <ShieldCheck className="h-3.5 w-3.5" /> FastAPI Live
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium mb-1">
              <MapPin className="h-3.5 w-3.5 text-indigo-400" /> Pickup (Lat / Lng)
            </div>
            <div className="text-sm font-mono text-slate-200">{pickup.lat}, {pickup.lng}</div>
          </div>
          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium mb-1">
              <Navigation className="h-3.5 w-3.5 text-rose-400" /> Destination (Lat / Lng)
            </div>
            <div className="text-sm font-mono text-slate-200">{drop.lat}, {drop.lng}</div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={fetchEstimate}
            disabled={loading}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 py-2.5 rounded-lg font-medium transition cursor-pointer"
          >
            {loading ? "Calculating..." : "Calculate Fare Estimate"}
          </button>
          {estimate && (
            <button
              onClick={requestRide}
              disabled={loading || rideStatus !== "IDLE"}
              className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-lg font-medium transition shadow-lg shadow-indigo-600/30 cursor-pointer"
            >
              Confirm & Book Ride
            </button>
          )}
        </div>

        {estimate && (
          <div className="grid grid-cols-3 gap-3 bg-slate-800/30 p-4 rounded-xl border border-slate-800 text-center">
            <div>
              <DollarSign className="h-4 w-4 mx-auto text-emerald-400 mb-1" />
              <div className="text-xs text-slate-400">Est. Fare</div>
              <div className="text-lg font-semibold">${estimate.fare_estimate.toFixed(2)}</div>
            </div>
            <div>
              <Clock className="h-4 w-4 mx-auto text-amber-400 mb-1" />
              <div className="text-xs text-slate-400">Duration</div>
              <div className="text-lg font-semibold">{Math.ceil(estimate.duration_seconds / 60)} min</div>
            </div>
            <div>
              <Navigation className="h-4 w-4 mx-auto text-sky-400 mb-1" />
              <div className="text-xs text-slate-400">Distance</div>
              <div className="text-lg font-semibold">{(estimate.distance_meters / 1000).toFixed(1)} km</div>
            </div>
          </div>
        )}

        {rideId && (
          <div className="border border-indigo-500/30 bg-indigo-950/20 rounded-xl p-4 space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400">Active Ride Session:</span>
              <span className="font-mono text-indigo-400 font-bold">#{rideId}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400">Dispatch Status:</span>
              <span className="capitalize font-semibold text-emerald-400">{rideStatus}</span>
            </div>
            {driverLoc && (
              <div className="text-xs text-slate-400 mt-2 font-mono">
                Driver Telemetry: {driverLoc.lat.toFixed(4)}, {driverLoc.lng.toFixed(4)}
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
