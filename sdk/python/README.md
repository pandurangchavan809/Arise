# Adaptive Memory Python SDK

Official Python client for the **Adaptive Memory Runtime**, providing intelligent memory persistence, quality-scored recall, context budget optimization, and memory lifecycle management.

---

## Installation

Install via pip:

```bash
pip install adaptive-memory-sdk
```

Or install in development mode from the SDK folder:

```bash
cd sdk/python
pip install -e .
```

---

## Quick Start

```python
from adaptive_memory_sdk import Memory

# Initialize client (defaults to http://localhost:8000)
client = Memory(base_url="http://localhost:8000")

# Check server status
health = client.health()
print(f"Service status: {health}")

# Store a memory
memory = client.remember(
    content="User prefers Python and FastAPI for backend development",
    memory_type="long_term",
    user_id="user_123",
    confidence=0.9,
    importance=0.8,
)
print(f"Stored memory ID: {memory['id']}")

# Recall memories with quality scoring and budget enforcement
recall_result = client.recall(
    query="What tech stack should we recommend?",
    user_id="user_123",
    max_memories=5,
    max_tokens=500,
)

print(f"Recalled {len(recall_result.memories)} memories:")
for mem in recall_result.memories:
    print(f"- {mem.content}")

# Provide utility feedback to calibrate memory scores
client.record_outcome(
    memory_ids=[memory["id"]],
    outcome="helpful",  # 'helpful', 'irrelevant', or 'misleading'
    user_id="user_123",
)
```

---

## Core Capabilities

### 1. Memory Types

The SDK supports four lifespan classifications:
- **`session`**: Ephemeral conversational context that expires with session end.
- **`long_term`**: Persistent facts, user profile details, and domain knowledge.
- **`experience`**: Operational knowledge synthesized from past actions and outcomes.
- **`prospective`**: Future tasks, reminders, and scheduled agent actions.

```python
# Session memory
client.remember("Currently editing docker-compose.yml", memory_type="session", user_id="user_123")

# Long-term memory
client.remember("User timezone is UTC-5", memory_type="long_term", user_id="user_123")

# Experience memory
client.remember("Using multi-stage Docker builds reduced image size by 70%", memory_type="experience", user_id="user_123")

# Prospective memory
client.remember("Review API security checklist tomorrow", memory_type="prospective", user_id="user_123")
```

### 2. Context Budget & Recall Control

During recall, candidates are ranked deterministically by relevance, utility, confidence, recency, and conflict penalties:

```python
result = client.recall(
    query="Deployment best practices",
    user_id="user_123",
    max_memories=3,
    max_tokens=800,
    memory_types=["experience", "long_term"],
)

for candidate in result.selected:
    score = candidate.score
    print(f"Content: {candidate.memory.content}")
    print(f"Total Score: {score.total:.2f} | Relevance: {score.relevance:.2f} | Utility: {score.utility:.2f}")
```

### 3. Lifecycle Operations: Forget & Archive

```python
# Suppress a memory from future recalls
client.forget(memory_id="mem_abc123", user_id="user_123")

# Archive an inactive or superseded memory
client.archive(memory_id="mem_xyz789", user_id="user_123")

# Permanently delete
client.delete_memory(memory_id="mem_xyz789")
```

### 4. Grounded Chat & Web Search

```python
# Chat with automatic memory recall injection
response = client.chat(
    message="Can you summarize my preferences?",
    user_id="user_123",
    use_memory=True,
    use_search=False,
)
print(response["response"])

# Search the web using integrated Tavily API
search_results = client.search(query="FastAPI 0.115 new features", max_results=3)
```

---

## Error Handling

The SDK raises structured exceptions derived from `AdaptiveMemoryError`:

```python
from adaptive_memory_sdk import Memory
from adaptive_memory_sdk.exceptions import (
    AdaptiveMemoryError,
    ConnectionError,
    NotFoundError,
    ValidationError,
)

client = Memory()

try:
    memory = client.get_memory("nonexistent-id")
except NotFoundError as e:
    print(f"Memory not found: {e.message}")
except ConnectionError as e:
    print(f"Could not reach server: {e.message}")
except ValidationError as e:
    print(f"Invalid parameters: {e.message}")
except AdaptiveMemoryError as e:
    print(f"General error: {e.message}")
```

---

## License

MIT License. See [LICENSE](../../LICENSE) for details.
