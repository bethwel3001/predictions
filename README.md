# NASA TEMPO Air Quality Forecasting Platform 🌍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61DAFB.svg)](https://reactjs.org/)

> **NASA Space Apps Challenge 2025 Project**  
> Forecasting air quality using TEMPO satellite data, ground sensors, and machine learning

## 🚀 Quick Start (Focus: Backend API)

### Prerequisites

- Python 3.9+ (tested with 3.12+)
- UV package manager (optional but recommended)
- Node.js 18+ (for frontend, optional)

### Backend Setup (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/bethwel3001/predictions.git
cd predictions/predictions

# 2. Create virtual environment with UV (fast!)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
uv pip install fastapi uvicorn requests pyyaml pydantic pydantic-settings python-multipart python-dotenv

# 4. Start the backend server
cd backend
python3 src/api/main.py
```

**That's it!** 🎉

### Access Points

- **Backend API**: http://localhost:8000
- **API Docs (Interactive)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Test the New Endpoints

```bash
# Test OpenAQ (global ground monitoring)
curl "http://localhost:8000/api/v1/openaq/latest?country=US&limit=5"

# Test Pandora (NASA validation network)
curl "http://localhost:8000/api/v1/pandora/sites"

# Test Data Attribution
curl "http://localhost:8000/api/v1/attribution"
```

## 📁 Project Structure

**Focus: Backend API & Data Processing**

```
predictions/
├── backend/                  # Python backend (CORE)
│   └── src/
│       ├── data_ingestion/  # ⭐ Data fetchers (OpenAQ, Pandora, TEMPO, AirNow, PurpleAir)
│       ├── database/        # SQLAlchemy models
│       ├── ml_models/       # Forecasting models
│       ├── api/             # ⭐ FastAPI endpoints (14 endpoints)
│       ├── notifications/   # Alert system
│       ├── pipeline/        # Data orchestration
│       └── utils/           # Helper functions
├── frontend/                # React frontend (ready for integration)
│   ├── src/                 # React components
│   └── public/              # Static assets
├── config/                  # Configuration files
├── data/                    # Data storage (cache, raw, processed)
├── models/                  # Saved ML models
├── scripts/                 # Setup scripts
├── tests/                   # Test suites
├── docker-compose.yml       # Local development
└── requirements.txt         # Python dependencies
```

## 🛠️ Technology Stack

### Backend (Core Focus)

- **API Framework**: FastAPI 0.118+ with auto-generated OpenAPI docs
- **Data Fetchers**: 
  - OpenAQ (global ground monitoring)
  - Pandora (NASA satellite validation)
  - TEMPO (satellite data)
  - AirNow (EPA network)
  - PurpleAir (community sensors)
- **Data Processing**: pandas, numpy, xarray
- **Database**: PostgreSQL with PostGIS (optional)
- **Cache**: Redis (optional)
- **ML Models**: scikit-learn, TensorFlow (optional)

### Frontend (Pre-built, Ready to Integrate)

- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Icons**: React Icons

### Development

- **Package Manager**: UV (ultra-fast Python package manager)
- **Containers**: Docker & Docker Compose
- **Testing**: pytest

## 🌳 Development Workflow

### Branch Strategy
See [prompt.md](prompt.md) for detailed branching strategy.

```bash
# Create feature branch
git checkout -b feature/data-tempo-fetcher

# Make changes and commit
git add .
git commit -m "feat(data): implement TEMPO satellite data fetcher"

# Push and create PR
git push origin feature/data-tempo-fetcher
```

### Commit Convention
Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

## 🧪 Testing

```bash
# Run Python tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run frontend tests
cd frontend
npm test
```

## 📊 Data Sources

1. **NASA TEMPO**: Satellite air quality data
2. **EPA AirNow**: Ground-based sensor network
3. **PurpleAir**: Community air quality sensors
4. **OpenWeather**: Meteorological data

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

NASA Space Apps Challenge 2025 Team

## 🙏 Acknowledgments

- NASA for TEMPO satellite data
- EPA for AirNow API access
- PurpleAir for sensor data
- OpenWeather for meteorological data

## 📞 Support

For questions or issues, please open an issue on GitHub.

---

**Built with ❤️ for NASA Space Apps Challenge 2025**
