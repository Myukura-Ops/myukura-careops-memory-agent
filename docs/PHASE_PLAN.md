# Rollout Phase Plan

## Phase 0: Docs + Scaffold (Complete)
- Workspace structure.
- Base documents and Hackathon checklist.
- Minimal skeleton of API, Worker, and Web apps without complex logic.

## Phase 1: Async API/Worker Skeleton (Complete)
- Cloud Run-ready FastAPI endpoints for API and Worker.
- Mock queue dispatch using FastAPI Background Tasks.
- In-memory repository for `agent_runs` state and events.
- UI polling for agent lifecycle simulated updates.
- Standalone Worker placeholder.

## Phase 2: MongoDB State + Task Board
- Connect to MongoDB Atlas.
- Implement collections and state tracking for `agent_runs`.
- Connect React UI to API to view the task board.

## Phase 3: Gemini Orchestrator + Fallback
- Implement the AI agent using Gemini.
- Parse synthetic notes into operational tasks.

## Phase 4: MongoDB MCP/Tools Integration
- Integrate the MongoDB Partner MCP server.
- Allow the agent to use tools for richer context extraction.

## Phase 5: Safety, Hardening, Devpost
- Final safety verification.
- Audit trail completion.
- Devpost submission and demo video recording.
