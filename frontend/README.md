# Inco Payroll Frontend

React + Vite frontend for the Inco Payroll Django API.

## Requirements
- Node.js 18+
- Backend running at `http://localhost:8000` (default)

## Environment
Create `.env` in `frontend/` if you want to override the API base URL:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Install

```bash
npm install
```

## Run (development)

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Sample login request

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

## Notes
- Access + refresh tokens are stored in `localStorage`.
- The API client automatically refreshes the access token once on 401 responses.
- Payroll endpoints are wired to the Django routes in `payroll/urls.py`.
