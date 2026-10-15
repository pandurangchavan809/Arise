# Demo Run Guide

## 1. Configure `.env`

Edit `.env` in the project root. Keep real keys private; `.env` is ignored by Git.

```dotenv
DATABASE_URL=sqlite:///./adaptive_memory.db
LOG_LEVEL=INFO

# Needed for real assistant replies
NEBIUS_API_KEY=your_key
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
NEBIUS_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct

# Optional integrations
TAVILY_API_KEY=your_key
DEEPGRAM_API_KEY=your_key

MAX_MEMORIES=10
MAX_CONTEXT_TOKENS=2000
MAX_LATENCY_MS=100
MAX_STORAGE_BYTES=104857600
EMBEDDING_ENABLED=false
EMBEDDING_PROVIDER=nebius
EMBEDDING_MODEL=text-embedding-3-small
```

Leave unused provider keys blank. Restart the backend after changing `.env`. Without a Nebius key, local memory works, but `/api/chat` returns a configuration fallback instead of an LLM answer. Tavily and Deepgram are optional.

## 2. Start the backend

PowerShell, from the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Check `http://127.0.0.1:8000/health` and open API docs at `http://127.0.0.1:8000/docs`.

## 3. Start the frontend

In a second PowerShell window:

```powershell
cd frontend
npm run dev
```

For a fresh checkout, run `npm install` in `frontend` first. Open `http://localhost:5173` and choose **Assistant**.

## 4. Demo chat and memory

In Assistant, send:

1. `I prefer concise reports with bullet points.`
2. `What report style do I prefer?`

The backend stores and recalls memories in local SQLite. With `NEBIUS_API_KEY`, replies come from the configured model; without it, the memory API still works but the chat answer is a fallback. Use a unique user ID in the UI for a clean demo.

## 5. Demo voice

Click the microphone in Assistant, allow microphone access, and speak a prompt. In Edge/Chrome, the current UI uses the browser's speech-recognition API, then sends the transcript through the same chat endpoint. The UI currently returns a text answer; it does not play TTS audio.

For Deepgram's API routes, set `DEEPGRAM_API_KEY` and restart the backend. The routes are listed in `/docs` as `POST /api/voice/transcribe` and `POST /api/voice/speak`. These routes are not currently wired to the Assistant microphone button. Without browser speech-recognition support, the button uses a demo transcript fallback.

## 6. Optional Python SDK demo

The SDK is only needed when a separate Python agent wants to call the backend. From the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -e sdk\python
```

Save this as `sdk_demo.py` and run `.\.venv\Scripts\python.exe sdk_demo.py`:

```python
from adaptive_memory_sdk import Memory

with Memory(base_url="http://127.0.0.1:8000") as memory:
    memory.remember(
        content="Demo agent prefers short answers.",
        memory_type="long_term",
        user_id="senior-demo",
        source="user",
        confidence=0.95,
    )
    print(memory.recall("What answer style?", user_id="senior-demo").model_dump())
```

## Quick health checks

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Keep the backend bound to `127.0.0.1` for a local demo. The API currently has no server-side authentication, so do not expose it to an untrusted network.
