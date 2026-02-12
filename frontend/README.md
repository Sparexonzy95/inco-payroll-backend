# Frontend

## Run

```bash
npm install
npm run dev
```

- App runs on `http://localhost:5173`
- `/api` requests proxy to `http://127.0.0.1:8000`

## Auth UX

- Wallet connect + nonce signing only (no username/password form)
- JWT tokens are stored in localStorage
- User selects an active organization after login when multiple org memberships exist
