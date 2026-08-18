# AI To-Do List

Paste scattered work notes ("Finish PPT, check AWS logs, call client") and get back a
clean, structured to-do list — organized, prioritized (High / Medium / Low), and grouped
into categories (Work, Admin, Meetings, Technical, ...). Powered by the Claude API.

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env      # then paste your Anthropic API key into .env
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000

Without an `ANTHROPIC_API_KEY` set, the app still works — it falls back to a simple
built-in keyword parser so you can try the UI, but for real, nuanced results you need
the API key.

## Deploy

This is a standard FastAPI app, deployable anywhere that runs Python. Fastest path
to a live public URL is Render.com's free tier — takes about 2 minutes:

### Render.com (free tier, easiest — includes render.yaml blueprint)
1. Create a new GitHub repo and push this folder to it (or upload the zip via
   GitHub's web UI: New repo → "uploading an existing file").
2. Go to https://dashboard.render.com/blueprints → New Blueprint → connect the repo.
   Render will detect `render.yaml` automatically and set everything up.
3. When prompted, paste your Anthropic API key into the `ANTHROPIC_API_KEY` field
   (get one at https://console.anthropic.com/settings/keys).
4. Click Apply. Render builds and gives you a live `https://<name>.onrender.com` URL.

   (No blueprint? Manually: New → Web Service → connect repo → Build command
   `pip install -r requirements.txt` → Start command
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT` → add `ANTHROPIC_API_KEY` env var.)

### Railway.app
1. New Project → Deploy from GitHub repo.
2. Add the `ANTHROPIC_API_KEY` variable.
3. Railway auto-detects the `Procfile`.

### Docker (any host)
```bash
docker build -t ai-todo .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-... ai-todo
```

## Project structure

```
app/
  main.py           FastAPI backend (parsing + API routes)
  static/
    index.html      Single-page UI
    style.css
    app.js
requirements.txt
Procfile             for Render/Railway
Dockerfile
.env.example
```

## How it works

1. User pastes raw notes into the textarea and clicks "Organize my tasks".
2. The frontend POSTs the text to `/api/organize`.
3. The backend sends the notes to Claude with a system prompt instructing it to split
   the notes into atomic tasks, assign a priority (High/Medium/Low) and a category
   (Work/Admin/Meetings/Technical/...), and return strict JSON.
4. The frontend groups the returned tasks by category and sorts each group by priority.
