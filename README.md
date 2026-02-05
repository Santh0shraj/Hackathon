# Hackathon Full-Stack App

## Structure
- **backend/** — Flask API: app, config, models, database, routes (workflows, runs), services (Unbound client, workflow executor, completion checker).
- **frontend/** — React app: src/pages, src/components, src/api, package.json.
- **README.md** — This file; add setup and run instructions here.

## Run (PowerShell)

Start the **backend first** (so the frontend proxy can reach it), then the frontend in a second terminal.

**Terminal 1 – Backend (Flask on port 5000):**
```powershell
cd backend
python app.py
```
Uses SQLite by default (`hackathon.db` in `backend/`). Set env `DATABASE_URI` for MySQL.

**Unbound API:** Create `backend/.env` with `UNBOUND_API_KEY=your_key` (see `backend/.env.example`). Optional: `UNBOUND_API_URL` (default: https://api.getunbound.ai/v1/chat/completions).

**Terminal 2 – Frontend (Vite on port 5173):**
```powershell
cd frontend
npm install
npm run dev
```
Then open http://localhost:5173/
