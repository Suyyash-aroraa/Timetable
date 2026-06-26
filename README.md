# Personal Status Page

A lightweight personal status system: a Flask app running locally with a public JSON endpoint via ngrok, and a static GitHub Pages frontend.

## Architecture

- **Flask app** (`app.py`): local editor UI on `localhost:3333`, public `/status` JSON endpoint
- **ngrok**: exposes `localhost:3333` to the internet
- **GitHub Pages** (`docs/`): static public status page that polls the ngrok URL

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your ngrok authtoken (first time only)

```bash
python -c "from pyngrok import ngrok; ngrok.set_auth_token('YOUR_NGROK_AUTH_TOKEN')"
```

Your static domain is already configured: `unwomanly-shame-pastime.ngrok-free.dev`

### 3. Run the Flask app

```bash
python app.py
```

The app will auto-start ngrok and open the tunnel. Open `http://localhost:3333` to edit your status.

### 4. Deploy GitHub Pages

The frontend already points to your static domain. In your GitHub repo, go to **Settings > Pages** and set the source to the `docs/` folder.

## Features

- Click schedule items to cycle: `upcoming` → `current` → `done` → `skipped`
- Global status: Available / Busy / Do not disturb / Away
- Custom note field
- Auto-saves on every change
- Daily reset at 12:00 AM (all tasks back to `upcoming`)
- Status persists across restarts in `status.json`
- GitHub Pages frontend caches last known status and shows it if the server is offline
- Frontend auto-refreshes every 30 minutes and resets at midnight

## Files

- `app.py` — Flask backend
- `templates/index.html` — Local editor UI
- `docs/index.html` — Public status page
- `docs/config.js` — ngrok URL config
- `requirements.txt` — Python dependencies
- `status.json` — Persisted status (auto-created)
