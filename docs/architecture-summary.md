# Reachy Home Assistant - Architecture Summary

This document provides a high-level overview of the system architecture. For detailed decisions, see the [ADR documents](adr/).

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Jetson Orin NX (16GB)                             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         Assistant Service                                ││
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               ││
│  │  │ Recognition   │  │ Speech        │  │ Conversation  │               ││
│  │  │ - Face        │  │ - Wake Word   │  │ - Manager     │               ││
│  │  │ - Voice       │  │ - STT         │  │ - Intents     │               ││
│  │  └───────────────┘  │ - TTS         │  └───────────────┘               ││
│  │         │           └───────────────┘          │                        ││
│  │         │                  │                   │                        ││
│  │         └──────────────────┼───────────────────┘                        ││
│  │                            ▼                                            ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │                    Memory System                                    │││
│  │  │  - Working Memory (in-process)                                      │││
│  │  │  - Episodic Memory (PostgreSQL)                                     │││
│  │  │  - Semantic Memory (pgvector)                                       │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         API Server (FastAPI)                            ││
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               ││
│  │  │ Users         │  │ Calendar      │  │ Tasks         │               ││
│  │  └───────────────┘  └───────────────┘  └───────────────┘               ││
│  │  ┌───────────────┐  ┌───────────────┐                                  ││
│  │  │ Chat          │  │ WebSocket     │                                  ││
│  │  └───────────────┘  └───────────────┘                                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      PostgreSQL + pgvector                              ││
│  │  - Users, Events, Tasks, Messages                                      ││
│  │  - Memories with vector embeddings                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Reachy Mini    │      │  Web App        │      │  External APIs  │
│  (Robot)        │      │  (React)        │      │  - Claude       │
└─────────────────┘      └─────────────────┘      │  - Cozi         │
                                                  └─────────────────┘
```

## Component Details

### Assistant Service

The core service running continuously on the Jetson:

| Component | Technology | Purpose |
|-----------|------------|---------|
| Face Recognition | InsightFace (buffalo_l) | Identify family members by face |
| Voice Recognition | pyannote.audio | Identify speakers by voice |
| Wake Word | OpenWakeWord | Detect "Hey Reachy" |
| STT | faster-whisper | Convert speech to text |
| TTS | Kokoro | Convert text to speech |
| Conversation | Custom + Claude | Manage dialogue flow |
| Memory | PostgreSQL + pgvector | Store and retrieve memories |

### API Server

FastAPI backend serving the web application:

| Endpoint | Purpose |
|----------|---------|
| `/api/users` | Family member management |
| `/api/calendar` | Calendar queries |
| `/api/tasks` | Task/chore management |
| `/api/chat` | Chat with Reachy |
| `/api/chat/ws` | Real-time WebSocket |

### Database Schema

```sql
-- Core tables
users (id, name, role, preferences)
events (id, user_id, title, start_time, end_time, source)
tasks (id, title, assignee_id, status, due_date)
messages (id, user_id, role, content, created_at)

-- Memory with vectors
memories (id, user_id, content, embedding vector(384), importance)
```

## Data Flow

### Voice Interaction Flow

```
1. Wake Word Detection
   └─▶ "Hey Reachy" detected

2. Audio Capture
   └─▶ Record until silence

3. Parallel Processing
   ├─▶ STT: Audio → Text
   └─▶ Speaker ID: Audio → User

4. Context Retrieval
   ├─▶ User profile
   ├─▶ Relevant memories
   └─▶ Calendar context

5. LLM Processing
   └─▶ Claude API → Response

6. Response Delivery
   ├─▶ TTS: Text → Audio
   └─▶ Robot: Expression
```

### Cozi Sync Flow

```
1. Scheduled Trigger (every 15 min)

2. Fetch from Cozi
   ├─▶ Calendar events
   ├─▶ Shopping list
   └─▶ Todo items

3. Upsert to PostgreSQL
   └─▶ Merge with existing data

4. Available for queries
```

## Model Details

| Model | Size | GPU Memory | Inference Time |
|-------|------|------------|----------------|
| InsightFace buffalo_l | ~500MB | ~1GB | ~50ms/face |
| faster-whisper small | ~500MB | ~1GB | ~100ms/5s audio |
| pyannote embedding | ~100MB | ~500MB | ~50ms |
| Kokoro TTS | ~500MB | ~1GB | ~200ms/sentence |
| MiniLM-L6-v2 (embeddings) | ~80MB | ~200MB | ~10ms |

**Total GPU Memory**: ~3-4GB (within Jetson's 16GB)

## Deployment

### Services (systemd)

```
reachy-assistant.service  → Assistant main loop
reachy-api.service        → FastAPI server
postgresql.service        → Database
nginx.service             → Web frontend
```

### Network

| Port | Service |
|------|---------|
| 3000 | API (FastAPI) |
| 80 | Web frontend (nginx) |
| 5432 | PostgreSQL (localhost only) |

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Database | PostgreSQL + pgvector | One system for structured + vector data |
| LLM | Claude API | Quality, safety, tool use |
| Speech | Local models | Privacy, latency |
| Deployment | systemd | Simple, reliable, native GPU access |

See individual [ADR documents](adr/) for detailed rationale.
