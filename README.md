# IT Inventory Management Web App

A Dockerized IT inventory management web app for tracking devices across ServiceNow, Intune, local office inventory, and webcam OCR scans.

## Stack

- Frontend: Next.js + TypeScript + Tailwind CSS
- Backend: FastAPI + Python
- Database: PostgreSQL
- ORM/Migrations: SQLAlchemy 2 + Alembic
- Background jobs: Redis + RQ
- Deployment: Docker Compose

## Quick start

1. Copy `.env.example` to `.env` and update the values.
2. Run `docker compose up --build`.
3. Open the frontend at http://localhost:3000 and the API docs at http://localhost:8001/docs.

## ServiceNow email sync

- Set `EMAIL_USERNAME` and `EMAIL_APP_PASSWORD` in `.env`. The app also accepts `EMAIL_USER`, `IMAP_HOST`, and `IMAP_PORT`.
- Set `EMAIL_TLS_VERIFY=false` when your IMAP setup requires the same behavior as `rejectUnauthorized: false`.
- Set `SEED_SAMPLE_DATA=false` to stop demo devices from being created in a fresh database.
- The scheduler checks the mailbox every `EMAIL_IMPORT_INTERVAL_HOURS` hours, defaulting to 12.
- Use the ServiceNow page in the frontend to run **Sync latest email** and inspect recent imports/assets.

## Project layout

- `backend/` FastAPI application
- `frontend/` Next.js application
- `docker-compose.yml` local runtime
