# FastAPI Render Free

Minimal Python API without databases or external services.

## Local development

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
curl -i http://127.0.0.1:8000/health
```

Expected: HTTP 200 with `{"status":"ok"}`.

## Render settings

- Workspace: Dophmen's workspace
- Service: new Web Service, Python runtime
- Compute plan: **Free**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- HTTP health check path: `/health`
- No database, disk, worker, or paid resources required.

Free services can sleep when idle. The first request after sleep can be slow.
