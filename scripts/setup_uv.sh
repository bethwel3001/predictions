#!/bin/bash
# Quick setup script using UV package manager
# NASA TEMPO Air Quality Platform

set -e

echo "🚀 NASA TEMPO Air Quality Platform - Quick Setup with UV"
echo "=========================================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ UV installed successfully"
else
    echo "✅ UV is already installed ($(uv --version))"
fi

# Check if .env exists
if [ ! -f config/.env ]; then
    echo "📋 Creating .env from template..."
    cp config/.env.example config/.env
    echo "⚠️  Please edit config/.env with your actual credentials"
fi

# Create virtual environment
echo "🔨 Creating virtual environment with UV..."
uv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
echo ""
echo "Choose installation profile:"
echo "1) Minimal (FastAPI only - fastest, ~5 seconds)"
echo "2) Full (Everything including ML - ~2-3 minutes)"
echo "3) Dev (Full + development tools)"
echo ""
read -p "Enter choice [1-3] (default: 1): " choice
choice=${choice:-1}

case $choice in
    1)
        echo "📦 Installing minimal dependencies..."
        uv pip install -e ".[minimal]"
        ;;
    2)
        echo "📦 Installing full dependencies..."
        uv pip install -e "."
        ;;
    3)
        echo "📦 Installing development dependencies..."
        uv pip install -e ".[dev]"
        ;;
    *)
        echo "Invalid choice. Installing minimal..."
        uv pip install -e ".[minimal]"
        ;;
esac

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/raw
mkdir -p data/processed
mkdir -p models/saved

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
if command -v npm &> /dev/null; then
    npm install
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  npm not found. Please install Node.js to run frontend"
fi
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "Backend:"
echo "  source .venv/bin/activate"
echo "  uvicorn backend.src.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Frontend (in another terminal):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "📚 For more info, see UV_GUIDE.md"
