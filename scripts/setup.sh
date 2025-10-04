#!/bin/bash
# Setup script for NASA TEMPO Air Quality Platform

set -e

echo "🚀 NASA TEMPO Air Quality Platform Setup"
echo "=========================================="

# Check if .env exists
if [ ! -f config/.env ]; then
    echo "📋 Creating .env from template..."
    cp config/.env.example config/.env
    echo "⚠️  Please edit config/.env with your actual credentials"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/raw
mkdir -p data/processed
mkdir -p models/saved
mkdir -p notebooks

# Pull Docker images
echo "🐳 Pulling Docker images..."
docker-compose pull

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo "🎬 Starting services..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T postgres psql -U postgres -d tempo_air_quality < scripts/init_db.sql

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
