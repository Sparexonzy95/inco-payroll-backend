# Inco Payroll Backend + Frontend

## Backend (Django API)

1. Create and activate a Python environment.
2. Install dependencies (Django, DRF, SimpleJWT, web3, eth-account, celery, python-dotenv, django-cors-headers).
3. Run migrations:
   - `python manage.py migrate`
4. Start API:
   - `python manage.py runserver 8000`

### Auth endpoints

- `POST /api/auth/nonce/` with `{ "wallet": "0x..." }`
- `POST /api/auth/wallet-login/` with `{ "wallet": "0x...", "signature": "0x...", "nonce": "..." }`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `POST /api/auth/set-active-org/` with `{ "org_id": <int> }`

### Payroll endpoints and org derivation

Employer endpoints now derive organization from the authenticated user's active org (set via `/api/auth/set-active-org/`). Frontend does not send `org_id` for payroll schedule/run operations.

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
5. Frontend fetches `/api/auth/me/` and prompts for org selection when needed.
