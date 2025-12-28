# Reachy Home Assistant

A household assistant system combining a web application with a Reachy Mini robot to help a family of 4 manage schedules, tasks, and daily life through natural interaction.

## Features

- **Face Recognition**: Identifies family members on sight
- **Voice Recognition**: Knows who's speaking
- **Proactive Assistance**: Greets family members with relevant information
- **Schedule Management**: Integrates with Cozi family calendar
- **Task Tracking**: Homework, chores, and reminders
- **Natural Conversation**: Powered by Claude API
- **Web Dashboard**: Family-accessible app for schedules and tasks

## Architecture

```
┌─────────────┐         ┌─────────────────────────────┐
│ Reachy Mini │◀───────▶│ Jetson Orin NX              │
│ (robot)     │         │ ┌─────────────────────────┐ │
└─────────────┘         │ │ Assistant Service       │ │
                        │ │ - Face Recognition      │ │
┌─────────────┐         │ │ - Voice Recognition     │ │
│ Web App     │◀───────▶│ │ - Speech Processing     │ │
│ (React)     │         │ │ - Conversation Manager  │ │
└─────────────┘         │ ├─────────────────────────┤ │
                        │ │ PostgreSQL + pgvector   │ │
                        │ └─────────────────────────┘ │
                        └─────────────────────────────┘
```

## Hardware Requirements

- **Compute**: Seeed reComputer J4012 (Jetson Orin NX 16GB)
- **Robot**: Reachy Mini (wireless version)
- **Network**: Ethernet connection recommended

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-username/reachy-home-assistant.git
cd reachy-home-assistant
```

### 2. Run Setup Script (on Jetson)

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Add your credentials
```

### 4. Enroll Family Members

```bash
source venv/bin/activate
python scripts/enroll_family.py
```

### 5. Start Services

```bash
# Terminal 1: Assistant service
python -m assistant.main

# Terminal 2: API server
python -m api.main
```

## Project Structure

```
reachy-home-assistant/
├── docs/                    # Documentation
│   ├── adr/                 # Architecture Decision Records
│   ├── personas.md          # Family member personas
│   ├── architecture-summary.md
│   └── project-overview.md
├── src/
│   ├── assistant/           # Core assistant service
│   │   ├── recognition/     # Face/voice recognition
│   │   ├── speech/          # STT, TTS, wake word
│   │   ├── conversation/    # Dialogue management
│   │   ├── memory/          # Long-term memory
│   │   └── integrations/    # Claude, Cozi, Reachy
│   ├── api/                 # FastAPI backend
│   │   ├── routers/         # API endpoints
│   │   ├── models/          # Pydantic schemas
│   │   └── database/        # SQLAlchemy models
│   └── web/                 # React frontend (TBD)
├── scripts/                 # Setup and utility scripts
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── pyproject.toml           # Package configuration
```

## Documentation

- [Architecture Decision Records](docs/adr/) - Key technical decisions
- [Personas](docs/personas.md) - Family member profiles
- [Project Overview](docs/project-overview.md) - High-level project description
- [Architecture Summary](docs/architecture-summary.md) - Technical architecture

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, PostgreSQL + pgvector
- **ML**: faster-whisper, InsightFace, pyannote, Kokoro TTS
- **Frontend**: React, Tailwind CSS, shadcn/ui (planned)
- **External**: Claude API, Cozi integration
- **Hardware**: NVIDIA Jetson Orin NX, Reachy Mini

## Development

### Running Tests

```bash
source venv/bin/activate
pytest
```

### Code Style

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/
```

## License

MIT
