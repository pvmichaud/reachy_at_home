#!/bin/bash
set -e

echo "============================================"
echo "Reachy Home Assistant - Jetson Setup Script"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    print_warning "This doesn't appear to be a Jetson device. Continuing anyway..."
fi

echo ""
echo "Phase 1: System Update"
echo "----------------------"
sudo apt update && sudo apt upgrade -y
print_status "System updated"

echo ""
echo "Phase 2: System Dependencies"
echo "----------------------------"
sudo apt install -y \
    postgresql postgresql-contrib libpq-dev \
    python3-pip python3-venv python3-dev \
    ffmpeg libsndfile1 portaudio19-dev \
    git curl wget htop nvtop \
    build-essential cmake
print_status "System dependencies installed"

echo ""
echo "Phase 3: PostgreSQL Setup"
echo "-------------------------"
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Check if database already exists
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw reachy_db; then
    print_warning "Database 'reachy_db' already exists, skipping creation"
else
    echo "Enter a password for the database user 'reachy':"
    read -s DB_PASSWORD

    sudo -u postgres psql << EOF
CREATE USER reachy WITH PASSWORD '${DB_PASSWORD}';
CREATE DATABASE reachy_db OWNER reachy;
\c reachy_db
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF
    print_status "PostgreSQL configured with pgvector"
fi

echo ""
echo "Phase 4: Python Environment"
echo "---------------------------"
cd ~/reachy-assistant

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

source venv/bin/activate
pip install --upgrade pip wheel setuptools
print_status "Pip upgraded"

echo ""
echo "Phase 5: PyTorch (Jetson-specific)"
echo "----------------------------------"
# Check JetPack version and install appropriate PyTorch
if [ -f /etc/nv_tegra_release ]; then
    pip install torch torchvision torchaudio \
        --index-url https://developer.download.nvidia.com/compute/redist/jp/v51/pytorch/
    print_status "Jetson-optimized PyTorch installed"
else
    pip install torch torchvision torchaudio
    print_status "Standard PyTorch installed"
fi

echo ""
echo "Phase 6: Python Dependencies"
echo "----------------------------"
pip install -r requirements.txt
print_status "Python dependencies installed"

echo ""
echo "Phase 7: Model Downloads"
echo "------------------------"
print_warning "This may take 20-30 minutes..."

python3 << 'PYTHON'
import sys

def download_models():
    print("Downloading Whisper model...")
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("small", device="cuda", compute_type="float16")
        del model
        print("  ✓ Whisper downloaded")
    except Exception as e:
        print(f"  ! Whisper download issue: {e}")

    print("Downloading InsightFace model...")
    try:
        from insightface.app import FaceAnalysis
        app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider'])
        app.prepare(ctx_id=0)
        del app
        print("  ✓ InsightFace downloaded")
    except Exception as e:
        print(f"  ! InsightFace download issue: {e}")

    print("Downloading sentence-transformers model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        del model
        print("  ✓ sentence-transformers downloaded")
    except Exception as e:
        print(f"  ! sentence-transformers download issue: {e}")

    print("\nModel downloads complete!")

download_models()
PYTHON

print_status "Models downloaded"

echo ""
echo "Phase 8: Environment File"
echo "-------------------------"
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Created .env from .env.example - please edit with your credentials"
else
    print_warning ".env already exists"
fi

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials:"
echo "   nano .env"
echo ""
echo "2. Run the enrollment script:"
echo "   python scripts/enroll_family.py"
echo ""
echo "3. Start the assistant:"
echo "   python -m assistant.main"
echo ""
echo "4. Start the API server:"
echo "   python -m api.main"
echo ""
