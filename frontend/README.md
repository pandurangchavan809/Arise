# Adaptive Memory Runtime — Frontend

Plug-and-play memory intelligence for AI agents.

## Core Principle
> **The Memory Runtime IS the product.**  
> Chat and voice interfaces are merely live demonstration harnesses.

## Features
- **Landing Page**: Prominently features the complete Architecture Diagram, Four Pillars of Memory Intelligence, 4-Tier Memory Topology, and Multi-Provider Integrations.
- **Agent Assistant (`/app/assistant`)**: Live multi-turn interaction console with dynamic memory injection badges, microphone voice input, external citations, and reinforcement outcome scoring (Helpful/Unhelpful).
- **Memory Browser (`/app/memory`)**: Tabbed management for Session, Long-Term, Experience (RL), and Prospective memory tiers with interactive search, status filtering, and modal memory authoring.
- **Memory Quality Inspector (`/app/quality`)**: Real-time recall simulator showing candidate scoring, breakdown progress bars (relevance, utility, confidence, conflict risk), and hard edge token budgeting meters.
- **Developer Documentation (`/app/developer`)**: Python SDK quickstarts, zero-bloat local SLM loops, OpenAI wrappers, and REST API specification.

## Tech Stack
- **Framework**: React 18+ with Vite
- **Styling**: Tailwind CSS v4
- **Routing**: React Router DOM v6
- **Icons**: Lucide React
- **Markdown**: React Markdown

## Getting Started
```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173` and proxies `/api` calls to `http://localhost:8000`.
