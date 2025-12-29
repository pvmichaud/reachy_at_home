# Reachy Home Assistant — Jetson Setup Tracker

## Hardware

| Item | Value |
|------|-------|
| Device | Seeed reComputer J4012 |
| Module | NVIDIA Jetson Orin NX 16GB |
| JetPack | R35.5.0 (JetPack 5.1.x) |
| Hostname | `gpu-ai-lab` |
| IP Address | `10.0.0.55` |
| Username | `pmichaud` |

## Network Access

| Method | Details |
|--------|---------|
| SSH | `ssh pmichaud@10.0.0.55` |
| Windows Shortcut | `SSH Jetson.bat` on desktop |

---

## Setup Status

### System Setup
| Task | Status | Notes |
|------|--------|-------|
| Initial boot & Ubuntu config | ✅ Done | |
| SSH enabled | ✅ Done | |
| System packages | ✅ Done | NVIDIA kernel packages held (see Known Issues) |
| Git repo cloned | ✅ Done | `~/reachy-assistant` |

### Database
| Task | Status | Notes |
|------|--------|-------|
| PostgreSQL installed | ✅ Done | Version 12.22 |
| pgvector extension | ✅ Done | Built from source (v0.5.1 for PG12 compatibility) |
| Database `reachy_db` created | ✅ Done | |
| User `reachy` created | ✅ Done | |
| uuid-ossp extension | ✅ Done | |

### Python Environment
| Task | Status | Notes |
|------|--------|-------|
| Python version | ✅ Done | 3.8.10 |
| Virtual environment | ✅ Done | `~/reachy-assistant/venv` |
| PyTorch (Jetson) | ✅ Done | 2.1.0a0+41361538.nv23.6, CUDA working |
| FastAPI, uvicorn, etc. | ✅ Done | |
| faster-whisper (STT) | ✅ Done | CPU mode only |
| face_recognition (face) | ✅ Done | Replaced insightface (ARM crash) |
| sentence-transformers | ✅ Done | all-MiniLM-L6-v2 |
| edge-tts (TTS) | ✅ Done | Replaced kokoro (Python 3.8 incompatible) |
| openwakeword | ✅ Done | |
| pyannote.audio (speaker ID) | ❌ Failed | torchaudio incompatible — using resemblyzer instead |
| resemblyzer (speaker ID) | ✅ Done | Alternative to pyannote.audio |
| py-cozi | ✅ Done | |
| reachy-sdk-api | ✅ Done | Package name differs from ADR |

### Configuration
| Task | Status | Notes |
|------|--------|-------|
| `.env` file created | ✅ Done | |
| DATABASE_URL configured | ✅ Done | |
| ANTHROPIC_API_KEY configured | ✅ Done | |
| COZI credentials configured | ✅ Done | |
| REACHY_HOST configured | ✅ Done | |

### ML Models Downloaded
| Model | Status | Notes |
|-------|--------|-------|
| Whisper small | ✅ Done | CPU mode only (CTranslate2 no CUDA on aarch64) |
| InsightFace buffalo_l | ❌ Failed | Crashes on ARM; using face_recognition instead |
| face_recognition (dlib) | ✅ Done | Replacement for InsightFace |
| sentence-transformers | ✅ Done | all-MiniLM-L6-v2 |

### Testing
| Task | Status | Notes |
|------|--------|-------|
| PyTorch CUDA verification | ✅ Done | `torch.cuda.is_available() = True` |
| Database connection test | ⏳ Pending | |
| Whisper transcription test | ⏳ Pending | |
| Face recognition test | ⏳ Pending | |
| Reachy connection test | ⏳ Pending | |
| Full integration test | ⏳ Pending | |

---

## Known Issues & Workarounds

### 1. NVIDIA L4T Kernel Packages
**Issue**: System upgrade fails on `nvidia-l4t-kernel` packages
**Workaround**: Packages held via `apt-mark hold`
```bash
sudo apt-mark hold nvidia-l4t-kernel nvidia-l4t-kernel-headers nvidia-l4t-display-kernel nvidia-l4t-kernel-dtbs
```
**Impact**: None — pre-installed kernel works fine

### 2. PostgreSQL 12 / pgvector Compatibility
**Issue**: Latest pgvector requires PostgreSQL 13+
**Workaround**: Installed pgvector v0.5.1 from source
```bash
cd ~/pgvector
git checkout v0.5.1
make && sudo make install
```
**Impact**: None — v0.5.1 has all features we need

### 3. Kokoro TTS Incompatible
**Issue**: Kokoro requires Python 3.9+ (spacy dependency)
**Workaround**: Using `edge-tts` instead
**Impact**: Requires internet for TTS; consider local alternative later

### 4. CTranslate2 No CUDA Support
**Issue**: faster-whisper's CTranslate2 package not compiled with CUDA for aarch64
**Workaround**: Using CPU mode (`device='cpu', compute_type='int8'`)
**Impact**: Slower transcription; see TODO for optimization

### 5. InsightFace Crashes on ARM
**Issue**: InsightFace crashes with assertion error on aarch64 (both CPU and CUDA modes)
**Workaround**: Using `face_recognition` library (dlib-based) instead
**Impact**: None — face_recognition works well

### 6. pyannote.audio / torchaudio Incompatibility
**Issue**: pyannote.audio requires torchaudio, but NVIDIA's Jetson PyTorch wheel doesn't have matching torchaudio available
**Error**: `undefined symbol: _ZNK5torch8autograd4Node4nameEv`
**Workaround**: Using `resemblyzer` library instead (simpler speaker embeddings, no torchaudio dependency)
**Impact**: None — resemblyzer provides speaker identification capabilities
**Note**: pyannote.audio has more advanced features (diarization); can revisit if needed

---

## TODO — Future Optimizations

### High Priority
| Task | Description | Effort |
|------|-------------|--------|
| Whisper GPU acceleration | Build CTranslate2 from source with CUDA, or use alternative (whisper.cpp, tensorrt) | Medium |
| Local TTS | Replace edge-tts with offline solution (piper, coqui) | Low |
| Advanced speaker diarization | If resemblyzer insufficient, revisit pyannote.audio with custom torchaudio build | Medium |

### Medium Priority
| Task | Description | Effort |
|------|-------------|--------|
| Auto-deploy script | Polling script to auto-pull and restart on git push | Low |
| systemd services | Create service files for auto-start on boot | Low |
| Static IP | Configure static IP instead of DHCP | Low |

### Low Priority
| Task | Description | Effort |
|------|-------------|--------|
| Upgrade PostgreSQL | Move to PG 14+ for latest pgvector | Medium |
| Screen/tmux setup | For long-running processes | Low |

---

## Useful Commands

### SSH Connection
```bash
# From Windows: run SSH Jetson.bat, or:
ssh pmichaud@10.0.0.55
```

### Activate Python Environment
```bash
cd ~/reachy-assistant
source venv/bin/activate
```

### Check Services
```bash
sudo systemctl status postgresql
pg_isready
```

### Git Operations
```bash
cd ~/reachy-assistant
git pull
```

### View GPU Usage
```bash
nvtop
```

### View System Resources
```bash
htop
```

---

## Credentials Reference (DO NOT COMMIT)

| Service | Location |
|---------|----------|
| Jetson password | (your memory) |
| Database password | `~/reachy-assistant/.env` |
| GitHub token | Stored via `git credential.helper store` |
| Anthropic API key | `~/reachy-assistant/.env` |
| Cozi credentials | `~/reachy-assistant/.env` |

---

## Session Log

### 2024-12-28: Initial Setup — COMPLETE ✅
- Completed first boot and SSH setup
- Created Windows batch file shortcut for SSH
- Cloned repository
- Encountered and resolved NVIDIA kernel package issue (held packages)
- Installed PostgreSQL 12 and pgvector 0.5.1 (built from source for PG12)
- Set up Python virtual environment
- Installed Jetson-optimized PyTorch 2.1.0 with CUDA
- Installed all required packages with multiple workarounds:
  - kokoro → edge-tts (Python 3.8 incompatible)
  - insightface → face_recognition (ARM crash)
  - pyannote.audio → resemblyzer (torchaudio incompatible)
- Configured .env file with database, API keys, Reachy IP
- Downloaded ML models (Whisper, face_recognition, sentence-transformers)
- Added LD_PRELOAD fix to .bashrc for ARM TLS issue

**Final Status**: All 9 core systems verified working
- PyTorch + CUDA ✅
- Speech-to-Text (Whisper) ✅
- Face Recognition ✅
- Sentence Transformers ✅
- TTS (edge-tts) ✅
- Wake Word (openwakeword) ✅
- Speaker ID (resemblyzer) ✅
- Web Framework (FastAPI) ✅
- Database (asyncpg) ✅
- Integrations (py-cozi) ✅

---

*Last updated: 2024-12-28*
