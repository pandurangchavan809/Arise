# Live Demo Questions

A short walkthrough for showing memory capture, recall, and persistence to project viewers.

## Before the demo

1. Start the backend from the project root:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
   ```

2. In a second terminal, start the frontend:

   ```powershell
   cd frontend
   npm run dev
   ```

3. Open `http://localhost:5173/app/assistant` and use user ID `usr_default` for the whole demo.
4. The chat calls the LLM configured for the backend. This project currently uses its Nebius provider; make sure its key and model are configured before the demo, then restart the backend after `.env` changes. Ollama running separately is not automatically connected to this web chat.

## Demo flow

### 1. Teach a permanent preference

Send:

> I prefer concise, practical Python FastAPI answers with short examples. Please remember this preference.

The chat extractor recognizes the phrase `I prefer` and saves a long-term memory.

### 2. Recall it

Ask:

> What Python FastAPI answer style do I prefer?

Show the memory used under the answer. Click **Inspect** to show which stored memory informed the response.

### 3. Show persistence across sessions

Click **New Session**, then ask the same recall question again. The long-term preference should still be available for the same user.

### 4. Save and recall a reminder

Send:

> Remind me to show the Arise adaptive-memory demo to the senior reviewers on Friday.

Then ask:

> What Arise demo reminder did I ask you to save?

The phrase `Remind me to` is recognized as a prospective memory. This saves the reminder as memory; it does not schedule a notification.

### 5. Inspect the memory tiers

Open **Memory Browser** and show:

- **Long-Term:** the Python FastAPI preference.
- **Prospective:** the Arise demo reminder.
- **Session:** recent chat turns.

### 6. Optional voice input

Return to **Agent Assistant**, allow microphone access, and speak:

> What Python FastAPI answer style do I prefer?

Voice input depends on browser speech-recognition support. If voice is part of the senior demo, try the microphone once before presenting.

## Demo tips

- Keep the same user ID throughout; memories are scoped to a user.
- Use the same key terms in recall questions as in the saved memory. Current retrieval is keyword-based.
- Avoid promising that the assistant will list every memory in a normal chat answer. Use the Memory Browser tier tabs to inspect stored records.
- If chat reports that the Nebius key is not configured, check the backend configuration and restart the backend before continuing.
