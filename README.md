# Full-Stack Cab Booking & Ride-Hailing Platform

A full-stack ride-hailing application built with **FastAPI (Python)**, **PostgreSQL + PostGIS**, **Redis**, **Celery**, **python-socketio**, and **Next.js 14 (React & Tailwind CSS)**.

## Features
- **Spatial Nearest Driver Matching**: PostGIS `ST_DWithin` & `ST_DistanceSphere` queries.
- **Real-Time Telemetry & Status**: Socket.IO events backed by Redis for multi-instance pub/sub.
- **Dynamic Fare Calculation**: Routing calculations using Google Maps Matrix / Haversine fallback.
- **Payments & Receipts**: Stripe PaymentIntent orchestration with asynchronous Celery + WeasyPrint PDF receipt generation.
- **Authentication**: JWT token verification compatible with Clerk and Supabase auth.

## Quickstart (Docker Compose)
1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
2. Start all services:
   ```bash
   docker compose up --build
   ```
3. Open services:
   - Frontend Dashboard: [http://localhost:3000](http://localhost:3000)
   - Interactive OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
