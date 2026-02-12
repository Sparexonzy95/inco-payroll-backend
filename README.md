# Inco Payroll Backend + Frontend

## Backend (Django API)

1. Create and activate a Python environment.
2. Install dependencies (Django, DRF, SimpleJWT, web3, eth-account, celery, python-dotenv, django-cors-headers).
3. Run migrations:
   - `python manage.py migrate`
4. Start API:
   - `python manage.py runserver 8000`

### Auth endpoints

- `POST /api/auth/nonce/` with `{ "wallet": "0x...", "chainId": 84532 }`
- `POST /api/auth/wallet-login/` with `{ "wallet": "0x...", "signature": "0x...", "nonce": "..." }`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `POST /api/auth/employer/register/` with `{ "name": "Acme", "email": "ops@acme.com" }`

### Role model

- Employer: wallet owner that must complete employer registration (`name` + `email`) before payroll management.
- Employee: any wallet included in a payroll run; employee does not need an employer profile.

### Payroll endpoint behavior

Employer payroll endpoints derive employer from authenticated wallet only (no `org_id` payload/query params).

## Frontend (React + Vite)

1. `cd frontend`
2. `npm install`
3. `npm run dev`

Frontend uses Vite proxy for `/api` to `http://127.0.0.1:8000`.

### Wallet login flow

1. Connect wallet in login page.
2. Frontend requests nonce from backend.
3. User signs backend message with `personal_sign`.
4. Frontend exchanges signature for JWT access/refresh.
5. Frontend fetches `/api/auth/me/`.
6. If employer profile is missing, frontend routes to employer onboarding page.
