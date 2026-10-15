# Adaptive Memory Runtime

Adaptive Memory Runtime is a local-first memory service for AI agents. It stores memories in SQLite, searches text with FTS5, scores candidates deterministically, and limits the context sent back to an agent. Nebius, Tavily, and Deepgram are optional integrations; the core memory service does not need their API keys.

## What is included

- **Python / FastAPI backend** for storing, recalling, updating, and forgetting memories.
- **SQLite + FTS5** for local persistent storage and text search.
- **React + Vite + Tailwind frontend** for the assistant demo and memory tools.
- **Python SDK** for calling a running backend from an agent.
- Optional adapters for **Nebius** (LLM), **Tavily** (web search), and **Deepgram** (speech).
- Optional Docker Compose setup.

The memory service is the product. The assistant UI and external providers are integrations and demos around it.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer and npm
- Docker Desktop only if you want the container setup

## Run locally on Windows

Open two PowerShell windows in the project folder.

### 1. Set up and run the backend

In the first window:

```powershell
cd C:\Users\PANDURANG\OneDrive\Desktop\Arise
python -m venv .venv
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

If `.env` already exists, skip `Copy-Item` so you do not overwrite your local settings. Then install the backend and SDK and start the API:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m pip install -e sdk\python
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

This starts a local-only API and creates `adaptive_memory.db` in the project folder. You do not need to activate the virtual environment when using its Python executable directly.

### 2. Install and run the frontend

In the second PowerShell window:

```powershell
cd C:\Users\PANDURANG\OneDrive\Desktop\Arise\frontend
npm install --cache ..\.npm-cache
npm run dev
```

The cache option keeps npm's download cache inside the project. You can use plain `npm install` if your npm cache directory is writable.

### 3. Open and check the app

- Web app: [http://localhost:5173](http://localhost:5173)
- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

From PowerShell, check the backend and its SQLite storage:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://localhost:5173/api/health
```

Both responses should report `healthy`; the `/api/health` response should also report `storage_healthy: true`.

Check the frontend production build with:

```powershell
cd C:\Users\PANDURANG\OneDrive\Desktop\Arise\frontend
npm run build
```

## Connect an agent with the Python SDK

Install the SDK from this checkout into the same virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -e sdk\python
```

With the backend running, an agent can write and recall memory through a small client:

```python
from adaptive_memory_sdk import Memory

with Memory(base_url="http://127.0.0.1:8000") as memory:
    memory.remember(
        content="The device should keep responses under 300 tokens.",
        memory_type="long_term",
        user_id="my-agent",
        source="user",
        confidence=0.95,
    )
    result = memory.recall(
        query="What response limit should I use?",
        user_id="my-agent",
        max_memories=3,
        max_tokens=300,
    )
    print(result.model_dump())
```

The SDK is an HTTP client: the runtime service must be running at `base_url`. See [project.md](project.md) for the architecture, environment variables, edge-device setup, and connectivity options.

## Install-name question: `pip install adaptive-memory-runtime`

That command does **not** install this checkout today. `pip install` looks for a distribution with that name on the configured package index; it does not package the current folder automatically. This repository has no root Python package metadata or release published by this project under `adaptive-memory-runtime`. The Python distribution currently defined here is the SDK under `sdk/python`, named `adaptive-memory-sdk`, with the local install command shown above. If that PyPI name belongs to another project, pip could install that project's code instead.

For `pip install adaptive-memory-runtime` to work on another laptop, the runtime needs to be packaged as a Python distribution and published to PyPI under that exact name. Installing a published Python package downloads its Python code and declared Python dependencies; it does not automatically start a server or install/build this project's React frontend. The frontend and full deployment remain separate steps.

## Run with Docker (optional)

From the project root, make `.env` if needed and start the stack:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose up --build
```

The dashboard is served at [http://localhost:3000](http://localhost:3000), and the API at [http://localhost:8000](http://localhost:8000). Docker Compose keeps the SQLite database in its `sqlite_data` volume. Stop the services with `Ctrl+C`; use `docker compose down` to remove the containers.

## Tests

Run the Python test suite from the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest pytest-asyncio
.\.venv\Scripts\python.exe -m pytest
```

## Project guide

Read [project.md](project.md) for the project structure, memory flow, `.env` reference, edge-device deployment, and limitations to know before exposing the API to other devices.
