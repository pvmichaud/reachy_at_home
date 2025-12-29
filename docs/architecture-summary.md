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
         │ HTTP/MJPEG               │                          │
         ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Reachy Mini    │      │  Web App        │      │  External APIs  │
│  (Robot)        │      │  (React)        │      │  - Claude       │
│  - MJPEG Bridge │      └─────────────────┘      │  - Cozi         │
│  - Motors (SDK) │                               └─────────────────┘
└─────────────────┘
```

## Component Details

### Assistant Service

The core service running continuously on the Jetson:

| Component | Technology | Purpose |
|-----------|------------|---------|
| Camera Access | MJPEG Bridge (HTTP) | Receive frames from Reachy's camera |
| Face Recognition | face_recognition (dlib) | Identify family members by face |
| Voice Recognition | resemblyzer | Identify speakers by voice |
| Wake Word | OpenWakeWord | Detect "Hey Reachy" |
| STT | faster-whisper | Convert speech to text |
| TTS | edge-tts | Convert text to speech |
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
| face_recognition (dlib) | ~30MB | CPU only | ~100ms/face |
| faster-whisper small | ~500MB | CPU only* | ~200ms/5s audio |
| resemblyzer | ~100MB | CPU only | ~50ms |
| edge-tts | Cloud | N/A | ~100ms/sentence |
| MiniLM-L6-v2 (embeddings) | ~80MB | ~200MB | ~10ms |

*Note: faster-whisper runs on CPU due to CTranslate2 not having CUDA support for aarch64.

**Total GPU Memory**: ~1GB (most processing on CPU due to ARM constraints)

## Deployment

### Services (systemd)

```
reachy-assistant.service  → Assistant main loop
reachy-api.service        → FastAPI server
postgresql.service        → Database
nginx.service             → Web frontend
```

### Network

| Port | Service | Location |
|------|---------|----------|
| 3000 | API (FastAPI) | Jetson |
| 80 | Web frontend (nginx) | Jetson |
| 5432 | PostgreSQL (localhost only) | Jetson |
| 8081 | MJPEG Camera Bridge | Reachy RPi |

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Database | PostgreSQL + pgvector | One system for structured + vector data |
| LLM | Claude API | Quality, safety, tool use |
| Speech | Local models | Privacy, latency |
| Camera Access | MJPEG over HTTP | Avoids GStreamer upgrade, simple protocol |
| Deployment | systemd | Simple, reliable, native GPU access |

See individual [ADR documents](adr/) for detailed rationale.
