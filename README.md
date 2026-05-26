# Breathe ESG — Emissions Ingestion & Review Prototype

Production-quality prototype for ingesting SAP fuel/procurement, utility electricity, and corporate travel data, normalizing emissions, and supporting analyst review with full audit trails.

## Architecture
- **Backend**: Django + DRF, JWT auth, PostgreSQL, Celery + Redis for async ingestion.
- **Frontend**: React + Vite, Tailwind, React Query, React Router, Recharts.
- **Storage**: Raw rows + normalized records + immutable audit logs.
- **Multi-tenancy**: All business records scoped to `organization_id`.

## Repository structure
```
backend/       Django + DRF API
frontend/      React client
docs/          MODEL.md, DECISIONS.md, TRADEOFFS.md, SOURCES.md
sample-data/   CSV samples (100+ rows per source)
docker/        Dockerfiles + nginx config
scripts/       Sample data generator
```

## Quick start (local)
1. **Backend**
```bash
python -m pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py seed_reference_data
python backend/manage.py seed_demo
python backend/manage.py runserver
```
Ensure Redis is running at `redis://localhost:6379/0` for ingestion jobs.

2. **Celery worker**
```bash
celery -A config worker -l info
```

3. **Frontend**
```bash
cd frontend
npm install
npm run dev
```

### Demo credentials
- **Analyst**: `analyst / breathe123`
- **Admin**: `admin / breathe123`
- **Viewer**: `viewer / breathe123`

## Environment variables
See `.env.example` for full list. Key values:
- `DATABASE_URL` (PostgreSQL connection)
- `CELERY_BROKER_URL` (Redis)
- `VITE_API_URL` (frontend API base)

## API documentation
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Ingestion flow
1. Upload CSV (per source system)
2. Async Celery job parses rows
3. Normalization + unit conversion
4. Anomaly detection
5. Analyst review + approvals
6. Audit lock after approval

## Sample data
Generated files are in `sample-data/`:
- `sap_fuel_procurement.csv`
- `utility_electricity.csv`
- `corporate_travel.csv`

Regenerate with:
```bash
powershell -ExecutionPolicy Bypass -File scripts/generate-sample-data.ps1 -Rows 120
```

## Docker
```bash
docker-compose up --build
```
Frontend: `http://localhost:5173`  
Backend: `http://localhost:8000`

## Deployment
### Backend (Render/Railway/Fly.io)
- Build command: `pip install -r backend/requirements.txt`
- Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`
- Set `DATABASE_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `SECRET_KEY`

### Frontend (Vercel/Netlify)
- Build command: `npm run build`
- Output directory: `dist`
- Env var: `VITE_API_URL=https://<your-backend>/api`

## Documentation
- **MODEL.md**: schema + audit strategy
- **DECISIONS.md**: architectural decisions and assumptions
- **TRADEOFFS.md**: deliberate scope tradeoffs
- **SOURCES.md**: source research notes and sample data rationale

## Screenshots
Capture the following UI views after running locally or on your deployed URL:
- Dashboard (cards + charts)
- Upload Center (batch list)
- Analyst Review Queue
- Audit Logs
