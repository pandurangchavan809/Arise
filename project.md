# Project Guide

This guide explains the Adaptive Memory Runtime architecture, local configuration, agent connection, and edge-device deployment. The short installation and launch path is in [readme.md](readme.md).

## Purpose

Adaptive Memory Runtime is a memory layer for AI agents. It decides which stored memories are relevant and safe to return, limits the amount of context returned, and accepts outcome feedback so memory utility can change over time.

It is not an LLM. The core can run without a model, external API credentials, a vector database, or Docker. The default retrieval path is deterministic text search and scoring backed by SQLite FTS5.

## How a request moves through the system

```text
Agent application
    |
    +-- Python SDK (HTTP client)
    |
    v
FastAPI backend
    |
    +-- Memory Quality Manager: filter, score, resolve conflicts, apply budget
    +-- SQLite + FTS5: persist records and search text
    +-- Optional adapters: Nebius, Tavily, Deepgram
```

The React frontend is a demo and inspection interface. An agent can use the API/SDK without running the frontend.

## Memory categories

| Type | Intended use | Lifetime |
| --- | --- | --- |
| `session` | Current task or conversation state | Temporary; can expire |
| `long_term` | Stable facts, constraints, and preferences | Persistent until changed or forgotten |
| `experience` | Prior task outcomes and lessons | Persistent and adjusted with outcome feedback |
| `prospective` | Reminders and future intentions | Until completed, expired, or forgotten |

Each record can hold its owner, content, type, source, timestamps, confidence, utility, importance, risk tier, status, and metadata. Embeddings are optional; the baseline does not need them.

## Project structure

```text
adaptive_memory/
  core/                    Memory quality, ranking, budgets, conflicts, lifecycle
  integrations/            Nebius, Tavily, and Deepgram adapters
  memory_types/            Memory-category helpers
  storage/                 SQLite storage interface and implementation
  config.py                Environment-backed settings
  models.py                Core records and enums
backend/
  app.py                   FastAPI application and health endpoints
  run.py                   Development runner
  dependencies.py          Storage, manager, and provider wiring
  routes/                  Memory, recall, assistant, and system APIs
  schemas.py               API request and response schemas
frontend/
  src/                     React pages, components, and API client
  package.json             Vite, React, Tailwind, and frontend scripts
sdk/python/
  adaptive_memory_sdk/     Synchronous HTTP client for a running API
  setup.py                 Local SDK package metadata (adaptive-memory-sdk)
tests/
  unit/                    Core and SDK tests
  integration/             API integration tests
docker/
  Dockerfile.backend       Python API image
  Dockerfile.frontend      Frontend build and web server image
  nginx.conf               Frontend/API reverse proxy
.env.example               Safe local configuration template
docker-compose.yml         Optional two-service deployment
```

## Environment setup

The app reads settings from `.env` in the project root. `.env` contains local settings and must not be committed. It is ignored by Git. The committed `.env.example` has the same setting names and blank provider keys; copy it only when a local `.env` does not already exist.

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

| Variable | Local default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./adaptive_memory.db` | SQLite database path; relative paths use the process working directory |
| `LOG_LEVEL` | `INFO` | Backend log detail |
| `NEBIUS_API_KEY` | blank | Enables optional Nebius chat completions |
| `NEBIUS_BASE_URL` | `https://api.tokenfactory.nebius.com/v1` | Nebius OpenAI-compatible endpoint |
| `NEBIUS_MODEL` | `meta-llama/Meta-Llama-3.1-70B-Instruct` | Default chat model |
| `TAVILY_API_KEY` | blank | Enables optional Tavily web search |
| `DEEPGRAM_API_KEY` | blank | Enables optional Deepgram speech-to-text and text-to-speech |
| `MAX_MEMORIES` | `10` | Default maximum memories returned by recall |
| `MAX_CONTEXT_TOKENS` | `2000` | Default recall context budget |
| `MAX_LATENCY_MS` | `100` | Recall latency budget setting |
| `MAX_STORAGE_BYTES` | `104857600` | Storage budget setting (100 MiB) |
| `EMBEDDING_ENABLED` | `false` | Embeddings are off by default |
| `EMBEDDING_PROVIDER` | `nebius` | Optional provider setting for future/optional embedding use |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Optional embedding model name |

Only add real provider keys when you want to use that integration. Never put credentials in source code, screenshots, or a committed `.env.example`. Local SQLite memory storage and retrieval do not need provider keys.

The backend currently configures CORS in `backend/app.py`; `HOST`, `PORT`, and `CORS_ORIGINS` in `.env` are not runtime settings. Choose the bind address and port on the Uvicorn command line.

## Run and verify locally

The complete Windows PowerShell commands are maintained in [readme.md](readme.md). In brief:

1. Create `.venv` and install `backend/requirements.txt`.
2. Install the SDK from `sdk/python` into that environment.
3. Start Uvicorn at `127.0.0.1:8000` from the project root.
4. In a second terminal, install and start the Vite frontend in `frontend`.
5. Open `http://localhost:5173` and `http://127.0.0.1:8000/docs`.

Check the service and storage:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

`/health` reports that the API process is responding. `/api/health` also checks storage and reports which optional providers have credentials. With blank provider keys, storage can be healthy while those integrations report unavailable; that is expected.

## Connect an agent with a few lines

The SDK is an HTTP client for the service. Install it from this checkout with:

```powershell
.\.venv\Scripts\python.exe -m pip install -e sdk\python
```

Then, while the backend is running:

```python
from adaptive_memory_sdk import Memory

with Memory(base_url="http://127.0.0.1:8000") as memory:
    memory.remember(
        content="The user prefers concise status updates.",
        memory_type="long_term",
        user_id="assistant-1",
        source="user",
        confidence=0.95,
    )
    context = memory.recall(
        query="How should I write status updates?",
        user_id="assistant-1",
        max_memories=3,
        max_tokens=300,
    )
    print(context.model_dump())
```

The agent decides when to save a useful fact and when to request memories. The SDK returns candidates and quality information; the agent can then add selected memories to its own prompt. Nebius is only required if this application also wants this backend's optional `/api/chat` route to call an LLM.

## Edge-device operation

The simplest edge setup is to run the Python backend and SQLite database on the same device as the agent. Install the Python dependencies once, then run the API locally:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Point the SDK at `http://127.0.0.1:8000`. The memory path uses the device's CPU, SQLite file, and local FTS5 search. It does not download an LLM or send memory data to a cloud provider by default. Once installed, the core memory operations can run without internet access. Provider-backed features need internet access and their corresponding API keys.

The frontend is optional on an edge device. Docker is optional too. Stop the backend before copying the SQLite database file for a simple backup, and keep enough persistent disk space for the configured storage budget.

### Let another device on a trusted LAN connect

Run the service bound to the device's LAN interfaces:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Then use the edge device's LAN address in the client, for example `Memory(base_url="http://192.168.1.23:8000")`. Replace that example address with the device's actual address.

**Network limitation:** this API does not currently enforce authentication or authorization. The SDK accepts an `api_key` argument, but the server does not validate it. Bind to `127.0.0.1` for same-device access. Before allowing other devices to connect, restrict access with a trusted network and firewall; do not expose this API directly to the public internet.

## Optional integrations

- **Nebius:** configured by `NEBIUS_API_KEY`, `NEBIUS_BASE_URL`, and `NEBIUS_MODEL`; used for assistant chat and embedding adapter calls.
- **Tavily:** configured by `TAVILY_API_KEY`; used by the optional search route.
- **Deepgram:** configured by `DEEPGRAM_API_KEY`; used for speech transcription and synthesis.

These adapters are separate from SQLite and the memory quality manager. If a key is missing, the corresponding adapter reports unavailable. The basic store and recall path remains local.

## HTTP API

The interactive and machine-readable API reference is at `/docs` while the backend is running. Main route groups include:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Process health |
| `GET` | `/api/health` | Storage and provider availability |
| `POST`, `GET` | `/api/memories` | Create and list memories |
| `GET`, `PATCH`, `DELETE` | `/api/memories/{memory_id}` | Read, update, or delete a memory |
| `POST` | `/api/memory/recall` | Find, score, and budget relevant memories |
| `POST` | `/api/memory/outcome` | Update utility from feedback |
| `POST` | `/api/memory/forget` | Forget a memory |
| `POST` | `/api/memory/archive` | Archive a memory |
| `GET` | `/api/memory/session`, `/long-term`, `/experience`, `/prospective` | List by memory type |
| `POST` | `/api/chat` | Optional memory-grounded assistant route |
| `POST` | `/api/search` | Optional Tavily search route |

## Python package and deployment model

`pip install adaptive-memory-runtime` is not a supported install path for this checkout: the root project is not packaged, and this project has not published a release under that name. The current local package is the SDK, installed from `sdk/python`. An SDK install alone does not include or launch the API service. Check the package index and publisher before installing a same-named distribution.

To make that one-line public install available later, the runtime needs root package metadata, a buildable wheel containing the intended Python modules, tested dependency declarations, a unique PyPI project name, and a release uploaded to PyPI. Publishing a Python package would distribute Python code and dependencies; it would not by itself deploy a running web service or the React frontend.

For full deployment, `docker compose up --build` runs the backend and frontend containers. The Compose file persists SQLite in the `sqlite_data` volume and serves the web UI on port `3000` and API on port `8000`.

## Tests and build checks

From the project root, run Python tests with:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest pytest-asyncio
.\.venv\Scripts\python.exe -m pytest
```

Build the frontend with:

```powershell
cd frontend
npm run build
```

## Known limits to account for

- The API currently has no server-side authentication or authorization.
- The Python SDK is a client for a running HTTP service, not a standalone memory database.
- A PyPI release named `adaptive-memory-runtime` has not been prepared by this checkout.
- The optional integrations require network access and valid provider credentials; the core memory store does not.
