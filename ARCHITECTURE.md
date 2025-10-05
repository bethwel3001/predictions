# 🌍 NASA TEMPO Air Quality Forecasting Platform - Architecture Documentation

**Project**: NASA Space Apps Challenge 2025  
**Version**: 0.2.0  
**Last Updated**: October 5, 2025  
**Repository**: https://github.com/bethwel3001/predictions  
**Current Branch**: api-fe-be

---

## **Executive Summary**

This is a **NASA Space Apps Challenge 2025** project that creates an **air quality monitoring and forecasting platform** using:
- 🛰️ **NASA TEMPO satellite data** (real-time satellite measurements)
- 🌐 **Ground sensor networks** (OpenAQ, Pandora, AirNow, PurpleAir)
- 🤖 **Machine learning** for 24-hour air quality predictions
- 🗺️ **Interactive web interface** showing real-time air quality on a map

---

## **Table of Contents**

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [API Documentation](#api-documentation)
6. [Frontend Architecture](#frontend-architecture)
7. [Backend Architecture](#backend-architecture)
8. [Data Sources](#data-sources)
9. [File Structure](#file-structure)
10. [Setup & Deployment](#setup--deployment)
11. [Development Workflow](#development-workflow)
12. [Current Status](#current-status)
13. [Future Enhancements](#future-enhancements)
14. [Troubleshooting](#troubleshooting)

---

## **Architecture Overview**

### **High-Level System Design**

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                          │
│  React 19 + Vite + Tailwind CSS + Axios            │
│  Interactive UI, Maps, Charts, Forecasts           │
│  Port: 5173                                         │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP/REST API
                  │ JSON over HTTP
                  │
┌─────────────────▼───────────────────────────────────┐
│                    BACKEND                           │
│  FastAPI + Python 3.9+                              │
│  RESTful API with 14+ endpoints                     │
│  Port: 8000                                         │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         API Layer (FastAPI)                │    │
│  │  - Route handlers                          │    │
│  │  - Request validation (Pydantic)           │    │
│  │  - CORS middleware                         │    │
│  │  - Error handling                          │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │     Data Ingestion Layer                   │    │
│  │  - TEMPO Fetcher (satellite)               │    │
│  │  - OpenAQ Fetcher (ground sensors)         │    │
│  │  - Pandora Fetcher (NASA validation)       │    │
│  │  - AirNow Fetcher (EPA network)            │    │
│  │  - PurpleAir Fetcher (community)           │    │
│  │  - Weather Fetcher (meteorological)        │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │     Data Processing Layer                  │    │
│  │  - Data harmonization                      │    │
│  │  - AQI calculation                         │    │
│  │  - Spatial matching                        │    │
│  │  - Quality validation                      │    │
│  │  - NetCDF parsing                          │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │     ML & Forecasting Layer                 │    │
│  │  - Time-series forecasting                 │    │
│  │  - Pattern-based predictions               │    │
│  │  - Trend analysis                          │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │     Utility Services                       │    │
│  │  - Geocoding (OpenStreetMap)               │    │
│  │  - City discovery                          │    │
│  │  - Data attribution                        │    │
│  └────────────────────────────────────────────┘    │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ External API Calls
                  │
┌─────────────────▼───────────────────────────────────┐
│              EXTERNAL DATA SOURCES                   │
│                                                      │
│  🛰️ NASA EarthData (TEMPO Satellite)               │
│     - NO2, O3, HCHO, Aerosol data                   │
│     - NetCDF format                                 │
│     - Hourly updates                                │
│                                                      │
│  🌐 OpenAQ API (Global Ground Sensors)              │
│     - 10,000+ monitoring stations                   │
│     - Real-time data                                │
│     - PM2.5, PM10, NO2, O3, SO2, CO                 │
│                                                      │
│  🔬 Pandora Network (NASA Validation)               │
│     - ~100 ground-based sites                       │
│     - Column measurements                           │
│     - Satellite validation data                     │
│                                                      │
│  🏛️ EPA AirNow (Official US Data)                  │
│     - Official AQI values                           │
│     - US coverage                                   │
│     - Hourly updates                                │
│                                                      │
│  🌡️ OpenWeather API (Meteorological Data)          │
│     - Temperature, humidity, wind                   │
│     - Weather forecasts                             │
└─────────────────────────────────────────────────────┘
```

---

## **Technology Stack**

### **Backend Technologies**

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.9+ | Primary language |
| **FastAPI** | 0.104+ | Web framework (async, high-performance) |
| **Uvicorn** | 0.24+ | ASGI server |
| **Pydantic** | 2.5+ | Data validation & settings |
| **earthaccess** | 0.15+ | NASA EarthData API client |
| **netCDF4** | 1.6+ | Parse satellite data files |
| **requests** | 2.31+ | HTTP client |
| **numpy** | 1.24+ | Numerical computing |
| **pandas** | 2.1+ | Data processing (optional) |

### **Frontend Technologies**

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.1+ | UI library |
| **Vite** | 7.1+ | Build tool & dev server |
| **Tailwind CSS** | 4.1+ | Utility-first CSS framework |
| **Axios** | 1.12+ | HTTP client |
| **React Icons** | 5.5+ | Icon library |
| **React Toastify** | 11.0+ | Notifications |
| **Framer Motion** | 12.23+ | Animations |

### **Development Tools**

| Tool | Purpose |
|------|---------|
| **pytest** | Testing framework |
| **ESLint** | JavaScript linting |
| **Black** | Python code formatting |
| **Git** | Version control |
| **Docker** | Containerization (planned) |

---

## **System Components**

### **1. API Layer (FastAPI)**

**Location**: `backend/src/api/main.py`

**Responsibilities**:
- Handle HTTP requests/responses
- Route management (14+ endpoints)
- Request validation using Pydantic
- CORS configuration for frontend
- Error handling and logging
- Auto-generated OpenAPI documentation

**Key Features**:
- Async request handling for better performance
- Type-safe request/response models
- Interactive API docs at `/docs`
- Health check endpoint

### **2. Data Ingestion Layer**

**Location**: `backend/src/data_ingestion/`

**Components**:

#### **TEMPO Fetcher** (`tempo_fetcher.py`)
- Authenticates with NASA EarthData
- Searches for TEMPO satellite granules
- Downloads NetCDF files
- Parses NO2, O3, HCHO, Aerosol Index
- Supports temporal and spatial filtering

#### **OpenAQ Fetcher** (`openaq_fetcher.py`)
- Queries OpenAQ API v2
- Fetches latest measurements
- Supports location/country/city filtering
- Returns real-time ground sensor data

#### **Pandora Fetcher** (`pandora_fetcher.py`)
- Retrieves NASA validation network data
- Column measurements for satellite validation
- Site metadata and measurements
- Temporal queries

#### **Data Attribution** (`data_attribution.py`)
- Tracks data source usage
- Generates proper citations
- Maintains licensing information
- Web-friendly attribution display

### **3. Data Processing Layer**

**Location**: `backend/src/data_processing/`

**Functions**:
- Data harmonization (unit conversion, timestamp normalization)
- AQI calculation using EPA formulas
- Spatial matching (satellite ↔ ground stations)
- Quality validation
- NetCDF file parsing
- Coordinate transformations

### **4. ML & Forecasting Layer**

**Location**: `backend/src/ml_models/`

**Current Implementation**:
- Pattern-based forecasting using time-of-day patterns
- Trend analysis from recent measurements
- 24-hour predictions with AQI levels

**Planned Enhancements**:
- Prophet time-series forecasting
- Random Forest regression
- Feature engineering (weather, traffic, seasonal)

### **5. Utility Services**

**Location**: `backend/src/utils/`

#### **Geocoding** (`geocoding.py`)
- City name → coordinates conversion
- Uses OpenStreetMap Nominatim API
- Reverse geocoding support

#### **City Discovery** (`city_discovery.py`)
- Find cities with air quality monitoring
- Search functionality
- Popular cities list

---

## **Data Flow**

### **User Request Flow**

```
User Action (Frontend)
    ↓
1. User enters city name or allows geolocation
    ↓
2. Frontend sends GET request to /api/airquality
    ↓
3. Backend API receives request
    ↓
4. Geocoding (if city name provided)
    ↓
5. Data Fetching (parallel):
    - Search TEMPO NetCDF files locally
    - Query OpenAQ for ground sensors (optional)
    - Check Pandora sites nearby (optional)
    ↓
6. Data Processing:
    - Parse NetCDF files
    - Extract pollutant values for location
    - Calculate AQI
    - Generate trend from recent readings
    ↓
7. Forecasting:
    - Apply time-of-day patterns
    - Calculate 24-hour predictions
    - Assign AQI levels and colors
    ↓
8. Response Assembly:
    - Current AQI
    - Pollutant breakdown
    - Health recommendations
    - 24-hour forecast
    - Recent trend data
    - Nearby areas
    ↓
9. JSON response sent to frontend
    ↓
10. Frontend renders:
    - AQI dashboard
    - Forecast chart
    - Trend visualization
    - Health alerts
```

---

## **API Documentation**

### **Base URL**: `http://localhost:8000`

### **Core Endpoints**

#### **Health Check**
```http
GET /health
```
**Response**: `{"status": "healthy"}`

#### **Root**
```http
GET /
```
**Response**: API information and available endpoints

---

### **Air Quality Endpoints**

#### **Get Air Quality Data**
```http
GET /api/airquality?lat={lat}&lon={lon}
GET /api/airquality?city={city_name}
```

**Query Parameters**:
- `lat` (float, optional): Latitude
- `lon` (float, optional): Longitude
- `city` (string, optional): City name

**Response Example**:
```json
{
  "city": "Los Angeles",
  "coordinates": {"lat": 34.05, "lon": -118.24},
  "aqi": 85,
  "pollutants": {
    "no2": 45.2,
    "o3": 54.3,
    "pm25": 36.1
  },
  "recent": [78, 82, 85, 83, 85],
  "forecast": [
    {
      "hour": 14,
      "aqi": 88,
      "level": "Moderate",
      "color": "#ffff00",
      "timestamp": "2025-10-05T14:00:00"
    }
    // ... 23 more hours
  ],
  "recommendation": "Air quality is acceptable...",
  "alert_level": "low",
  "timestamp": "2025-10-05T13:45:00",
  "data_sources": ["NASA TEMPO Satellite", "Pattern-based Forecasting"],
  "status": "success"
}
```

#### **Get Nearby Areas**
```http
GET /api/nearby?lat={lat}&lon={lon}&radius={km}
```

**Query Parameters**:
- `lat` (float, required): Latitude
- `lon` (float, required): Longitude
- `radius` (int, optional): Search radius in km (default: 50)

---

### **OpenAQ Endpoints**

#### **Latest Measurements**
```http
GET /api/v1/openaq/latest?country={country}&city={city}&limit={limit}
```

**Query Parameters**:
- `country` (string): Two-letter country code
- `city` (string): City name
- `latitude` (float): Latitude
- `longitude` (float): Longitude
- `radius` (int): Search radius in meters (default: 25000)
- `parameter` (string): Pollutant (pm25, pm10, o3, no2, so2, co)
- `limit` (int): Max results (default: 100)

#### **Monitoring Locations**
```http
GET /api/v1/openaq/locations?country={country}
```

---

### **Pandora Endpoints**

#### **Site List**
```http
GET /api/v1/pandora/sites
```

#### **Site Data**
```http
GET /api/v1/pandora/sites/{site_id}?product={product}&date={date}
```

**Parameters**:
- `site_id` (string): Site identifier
- `product` (string): NO2, O3, HCHO, SO2, AOD
- `date` (string): YYYY-MM-DD format

#### **TEMPO Validation**
```http
GET /api/v1/pandora/tempo-validation/{site_id}?date={date}
```

---

### **TEMPO Satellite Endpoints**

#### **Latest TEMPO Data**
```http
GET /api/v1/tempo/latest?latitude={lat}&longitude={lon}&constituents={NO2,O3}
```

#### **Time Range Query**
```http
GET /api/v1/tempo/timerange?start={YYYY-MM-DD}&end={YYYY-MM-DD}&latitude={lat}&longitude={lon}
```

---

### **City & Location Endpoints**

#### **Search Cities**
```http
GET /api/v1/cities/search?q={query}&limit={limit}
```

#### **Popular Cities**
```http
GET /api/v1/cities/popular?limit={limit}
```

#### **Geocode Location**
```http
GET /api/v1/geocode?location={location}&country={country}
```

---

### **Attribution Endpoints**

#### **All Attributions**
```http
GET /api/v1/attribution
```

#### **Specific Source**
```http
GET /api/v1/attribution/{source}
```

#### **Web Display Format**
```http
GET /api/v1/attribution/web-display?sources={source1,source2}
```

#### **Citation Text**
```http
GET /api/v1/attribution/citation?sources={source1,source2}
```

---

## **Frontend Architecture**

### **Component Hierarchy**

```
App.jsx (Root Component)
├── ErrorBoundary (Error handling wrapper)
├── ToastContainer (Notifications)
├── WorldMapBackground (Animated background)
├── Header
│   ├── Logo & Title
│   ├── Notification Bell
│   ├── Location Input
│   ├── Search Button
│   ├── Refresh Button
│   └── Data Sources Button
├── DataAttribution (Conditional)
└── Main Content
    ├── HeroLoadingOverlay (When loading)
    ├── ErrorDisplay (When error)
    ├── AQI Summary Card
    ├── Recommendation Card
    ├── 24-Hour Forecast Chart
    ├── Recent Trend Graph
    ├── Pollutant Breakdown
    └── Nearby Areas Grid
```

### **State Management**

The app uses React hooks for state management:

```javascript
// Location & Input
const [locationInput, setLocationInput] = useState("");
const [autoDetected, setAutoDetected] = useState(false);

// Data State
const [aqiData, setAqiData] = useState(null);
const [nearbyAreas, setNearbyAreas] = useState([]);

// Loading States
const [loading, setLoading] = useState(false);
const [refreshing, setRefreshing] = useState(false);
const [initialLoading, setInitialLoading] = useState(true);

// Error States
const [error, setError] = useState("");
const [locationError, setLocationError] = useState("");

// Alert State
const [severe, setSevere] = useState(false);

// UI State
const [showAttribution, setShowAttribution] = useState(false);
```

### **Key Frontend Features**

1. **Responsive Design**: Mobile-first approach, works on all screen sizes
2. **Loading States**: Smooth animations with hourglass loader
3. **Error Handling**: User-friendly error messages with retry options
4. **Geolocation**: Browser geolocation API integration
5. **Real-time Updates**: Auto-refresh capability
6. **Data Visualization**: Color-coded AQI, forecast charts, trend graphs
7. **Accessibility**: Proper ARIA labels, keyboard navigation

---

## **Backend Architecture**

### **Directory Structure**

```
backend/src/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── main.py                    # FastAPI application
├── data_ingestion/
│   ├── __init__.py
│   ├── tempo_fetcher.py           # NASA TEMPO satellite
│   ├── openaq_fetcher.py          # Ground sensors
│   ├── pandora_fetcher.py         # NASA validation
│   ├── airnow_fetcher.py          # EPA AirNow
│   ├── purpleair_fetcher.py       # Community sensors
│   ├── weather_fetcher.py         # Weather data
│   └── data_attribution.py        # Data citations
├── data_processing/
│   ├── __init__.py
│   └── (harmonization modules)
├── database/
│   ├── __init__.py
│   └── (database models)
├── ml_models/
│   ├── __init__.py
│   └── (forecasting models)
├── notifications/
│   ├── __init__.py
│   └── (alert system)
├── pipeline/
│   ├── __init__.py
│   └── (data orchestration)
└── utils/
    ├── __init__.py
    ├── geocoding.py               # Location services
    └── city_discovery.py          # City search
```

### **Design Patterns**

1. **Fetcher Pattern**: Each data source has a dedicated fetcher class
2. **Singleton**: Attribution manager, geocoding service
3. **Factory**: Data source instantiation
4. **Repository**: Data access abstraction (planned)
5. **Dependency Injection**: FastAPI's dependency system

### **Error Handling**

```python
# HTTP Exceptions
raise HTTPException(
    status_code=404,
    detail="City not found"
)

# Logging
logger.error(f"Error fetching data: {e}")

# Try-Except Blocks
try:
    data = fetch_data()
except RequestException as e:
    logger.error(f"Request failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

---

## **Data Sources**

### **1. NASA TEMPO Satellite**

**What it is**: NASA's Tropospheric Emissions: Monitoring of Pollution satellite instrument

**Data Provided**:
- Nitrogen Dioxide (NO2)
- Ozone (O3)
- Formaldehyde (HCHO)
- Aerosol Index (AI)

**Coverage**: North America (from space)

**Temporal Resolution**: Hourly during daylight

**Spatial Resolution**: ~5x5 km at nadir

**Data Format**: NetCDF (Network Common Data Form)

**Access**: NASA EarthData portal (requires free account)

**Attribution**: 
```
NASA TEMPO mission data provided by NASA Langley Research Center 
Atmospheric Science Data Center (ASDC DAAC)
```

---

### **2. OpenAQ (Global Ground Sensors)**

**What it is**: Open-source air quality data aggregator

**Data Provided**:
- PM2.5 (Fine particulate matter)
- PM10 (Coarse particulate matter)
- NO2 (Nitrogen dioxide)
- O3 (Ozone)
- SO2 (Sulfur dioxide)
- CO (Carbon monoxide)

**Coverage**: Global (10,000+ monitoring stations)

**Temporal Resolution**: Real-time to hourly

**Data Format**: JSON via REST API

**Access**: Free, no authentication required

**Attribution**:
```
Data provided by OpenAQ (https://openaq.org/)
Aggregated from government, research, and community monitoring networks
```

---

### **3. Pandora Network (NASA Validation)**

**What it is**: NASA's ground-based spectroscopy validation network

**Data Provided**:
- Column measurements (total atmospheric column)
- NO2, O3, HCHO, SO2, AOD
- Quality-assured validation data

**Coverage**: ~100 sites globally

**Purpose**: Validate satellite measurements

**Temporal Resolution**: Hourly to daily

**Data Format**: CSV/JSON

**Access**: Public NASA data portal

**Attribution**:
```
Pandora Project data provided by NASA/ESA
https://www.pandonia-global-network.org/
```

---

### **4. EPA AirNow**

**What it is**: US EPA's official air quality reporting system

**Data Provided**:
- Official AQI values
- Pollutant concentrations
- Forecasts

**Coverage**: United States

**Temporal Resolution**: Hourly

**Data Format**: JSON/XML via API

**Access**: Free API key required

**Attribution**:
```
Data provided by the U.S. Environmental Protection Agency AirNow program
https://www.airnow.gov/
```

---

## **File Structure**

### **Complete Project Tree**

```
predictions/
├── .venv/                         # Virtual environment
├── .git/                          # Git repository
├── .gitignore                     # Git ignore rules
│
├── README.md                      # Main documentation
├── ARCHITECTURE.md                # This file
├── TEAM_QUICK_START.md           # Team setup guide
├── SPRINT_8HR_PLAN.md            # 8-hour sprint plan
├── SPRINT_SUMMARY.md             # Sprint results
├── DEMO_SCRIPT.md                # Demo presentation
├── GITHUB_ISSUES.md              # Issue templates
│
├── pyproject.toml                # Python project config
├── setup.py                      # Python package setup
├── requirements.txt              # Python dependencies
├── conftest.py                   # Pytest configuration
│
├── backend/                      # Python backend
│   ├── requirements.txt          # Backend dependencies
│   └── src/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── main.py           # 🔥 FastAPI application
│       ├── data_ingestion/
│       │   ├── __init__.py
│       │   ├── tempo_fetcher.py
│       │   ├── openaq_fetcher.py
│       │   ├── pandora_fetcher.py
│       │   ├── airnow_fetcher.py
│       │   ├── purpleair_fetcher.py
│       │   ├── weather_fetcher.py
│       │   └── data_attribution.py
│       ├── data_processing/
│       │   └── __init__.py
│       ├── database/
│       │   └── __init__.py
│       ├── ml_models/
│       │   └── __init__.py
│       ├── notifications/
│       │   └── __init__.py
│       ├── pipeline/
│       │   └── __init__.py
│       └── utils/
│           ├── __init__.py
│           ├── geocoding.py
│           └── city_discovery.py
│
├── frontend/                     # React frontend
│   ├── package.json              # Node dependencies
│   ├── package-lock.json
│   ├── index.html                # Entry HTML
│   ├── vite.config.js            # Vite config
│   ├── eslint.config.js          # ESLint config
│   ├── WORLD_MAP_GUIDE.md        # Map component docs
│   ├── public/                   # Static assets
│   │   ├── vite.svg
│   │   ├── image.png
│   │   ├── profile.png
│   │   └── bethwel3001-card.png
│   └── src/
│       ├── main.jsx              # React entry point
│       ├── App.jsx               # 🔥 Main app component
│       ├── index.css             # Global styles
│       └── components/
│           ├── DataAttribution.jsx
│           ├── HourglassLoader.jsx
│           ├── WorldGlobe.jsx
│           └── WorldMapBackground.jsx
│
├── scripts/                      # Utility scripts
│   ├── convert_tempo_to_csv.py   # TEMPO converter
│   ├── quick_convert.py          # Quick conversion
│   ├── setup.sh                  # Environment setup
│   ├── setup_uv.sh               # UV package manager setup
│   ├── how_to_convert.sh         # Conversion guide
│   ├── init_db.sql               # Database initialization
│   ├── CONVERSION_SUMMARY.md     # Conversion docs
│   └── TEMPO_CSV_CONVERTER_README.md
│
├── tests/                        # Test suites
│   ├── test_tempo_fetcher.py     # TEMPO tests
│   └── test_tempo_quick.py       # Quick tests
│
├── tempo_data_downloads/         # Downloaded TEMPO files
│   ├── TEMPO_NO2_L2_*.nc         # NO2 granules
│   └── TEMPO_HCHO_L2_*.nc        # HCHO granules
│
├── src/                          # Additional components
│   └── components/
│       ├── AQIChart.jsx
│       ├── NotificationToast.jsx
│       └── RecommendationCard.jsx
│
├── NASA_TEMPO_Data_Import_for_Model_Training.ipynb  # Jupyter notebook
└── api.log                       # API logs
```

---

## **Setup & Deployment**

### **Development Setup**

#### **Prerequisites**
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn
- Git
- NASA EarthData account (optional, for live TEMPO data)

#### **Backend Setup**

```bash
# 1. Navigate to project root
cd /home/ogembo/predictions/predictions

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# 4. Install core dependencies
pip install -r backend/requirements.txt

# 5. Optional: Install full dependencies
pip install netCDF4 earthaccess pandas numpy

# 6. Set environment variables (optional)
export EARTHDATA_USERNAME="your_username"
export EARTHDATA_PASSWORD="your_password"

# 7. Start backend server
cd backend
python3 src/api/main.py
```

**Backend runs at**: `http://localhost:8000`

#### **Frontend Setup**

```bash
# 1. Navigate to frontend directory
cd /home/ogembo/predictions/predictions/frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

**Frontend runs at**: `http://localhost:5173`

---

### **Environment Variables**

Create a `.env` file in project root:

```bash
# NASA EarthData Credentials (optional)
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password

# API Keys (optional)
AIRNOW_API_KEY=your_airnow_key
OPENWEATHER_API_KEY=your_openweather_key

# Database (if using)
DATABASE_URL=postgresql://user:password@localhost:5432/airquality

# Redis (if using)
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
DEBUG=true
```

---

### **Docker Deployment (Planned)**

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - EARTHDATA_USERNAME=${EARTHDATA_USERNAME}
      - EARTHDATA_PASSWORD=${EARTHDATA_PASSWORD}
    volumes:
      - ./tempo_data_downloads:/app/tempo_data_downloads
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## **Development Workflow**

### **Git Workflow**

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Push to remote
git push origin feature/new-feature

# 4. Create Pull Request on GitHub

# 5. After review, merge to main
```

### **Commit Convention**

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

**Examples**:
```bash
git commit -m "feat(api): add TEMPO satellite endpoint"
git commit -m "fix(frontend): resolve map rendering issue"
git commit -m "docs: update API documentation"
```

---

### **Testing**

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tempo_fetcher.py -v

# Run with coverage
pytest --cov=backend/src tests/

# Run frontend tests (when implemented)
cd frontend
npm test
```

---

## **Current Status**

### **✅ Completed Features**

1. **Backend API**
   - [x] FastAPI application with 14+ endpoints
   - [x] OpenAQ integration (fully working)
   - [x] Pandora integration (fully working)
   - [x] TEMPO fetcher (downloads NetCDF files)
   - [x] Data attribution system
   - [x] Geocoding service
   - [x] City discovery
   - [x] Air quality endpoint with forecasting
   - [x] Health recommendations
   - [x] Error handling and logging

2. **Frontend**
   - [x] React application with modern UI
   - [x] Responsive design (mobile + desktop)
   - [x] Real-time data display
   - [x] 24-hour forecast visualization
   - [x] AQI trend charts
   - [x] Pollutant breakdown
   - [x] Health recommendations
   - [x] Loading states with animations
   - [x] Error handling with retry
   - [x] Geolocation support
   - [x] City search
   - [x] Data attribution page

3. **Data Processing**
   - [x] NetCDF file parsing
   - [x] AQI calculation (EPA formula)
   - [x] Pattern-based forecasting
   - [x] Trend analysis
   - [x] Coordinate matching

4. **Documentation**
   - [x] Comprehensive README
   - [x] Team quick start guide
   - [x] 8-hour sprint plan
   - [x] Architecture documentation
   - [x] API documentation (auto-generated)

---

### **🚧 In Progress / Planned**

1. **Backend Enhancements**
   - [ ] Real-time TEMPO data streaming
   - [ ] AirNow API integration (code ready, needs API key)
   - [ ] PurpleAir integration
   - [ ] Database persistence (PostgreSQL)
   - [ ] Caching layer (Redis)
   - [ ] Rate limiting
   - [ ] Background tasks (Celery)

2. **Frontend Enhancements**
   - [ ] Interactive map with markers (Leaflet/Mapbox)
   - [ ] Historical data charts
   - [ ] Compare locations feature
   - [ ] Export data (PDF/CSV)
   - [ ] User preferences
   - [ ] Push notifications
   - [ ] Offline mode (PWA)

3. **ML & Forecasting**
   - [ ] Prophet time-series model
   - [ ] Random Forest regression
   - [ ] Feature engineering (weather, traffic)
   - [ ] Model training pipeline
   - [ ] Accuracy metrics tracking

4. **DevOps**
   - [ ] Docker containerization
   - [ ] CI/CD pipeline (GitHub Actions)
   - [ ] Automated testing
   - [ ] Production deployment
   - [ ] Monitoring (Prometheus/Grafana)

---

## **Future Enhancements**

### **Phase 1: Core Improvements** (1-2 weeks)
- Interactive map with real-time markers
- Complete AirNow and PurpleAir integration
- Database persistence
- Improved ML forecasting models

### **Phase 2: Advanced Features** (2-4 weeks)
- User accounts and authentication
- Personalized alerts (email/SMS)
- Historical data analysis
- Mobile app (React Native)
- API rate limiting and caching

### **Phase 3: Scale & Optimize** (1-2 months)
- Microservices architecture
- Real-time data streaming (WebSockets)
- Global coverage expansion
- Advanced ML models (LSTM, GRU)
- Performance optimization

---

## **Troubleshooting**

### **Common Issues**

#### **1. Backend won't start**

**Problem**: `Port 8000 already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8001
```

---

#### **2. Frontend can't connect to backend**

**Problem**: `Failed to connect to server`

**Solution**:
- Ensure backend is running: `http://localhost:8000/health`
- Check CORS settings in `backend/src/api/main.py`
- Verify API_BASE URL in `frontend/src/App.jsx`

---

#### **3. No TEMPO data available**

**Problem**: `No TEMPO data available for location`

**Solution**:
- Current downloaded files only cover Los Angeles area
- Use coordinates: `lat=34.05, lon=-118.24`
- Download more data:
  ```bash
  python3 backend/src/data_ingestion/tempo_fetcher.py
  ```

---

#### **4. Module not found errors**

**Problem**: `ModuleNotFoundError: No module named 'netCDF4'`

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install missing package
pip install netCDF4

# Or install all dependencies
pip install -r backend/requirements.txt
```

---

#### **5. NASA EarthData authentication fails**

**Problem**: `Earthaccess authentication failed`

**Solution**:
- Create account at https://urs.earthdata.nasa.gov/
- Set environment variables:
  ```bash
  export EARTHDATA_USERNAME="your_username"
  export EARTHDATA_PASSWORD="your_password"
  ```
- Or use `earthaccess.login()` interactive prompt

---

#### **6. Frontend build fails**

**Problem**: `npm install` errors

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try with --legacy-peer-deps if needed
npm install --legacy-peer-deps
```

---

## **Performance Considerations**

### **Backend Optimization**

1. **Caching**:
   - Cache API responses for 5-10 minutes
   - Cache TEMPO data lookups
   - Redis for distributed caching

2. **Async Operations**:
   - Use FastAPI's async/await
   - Parallel data fetching from multiple sources
   - Background tasks for heavy processing

3. **Database**:
   - Index frequently queried fields
   - Connection pooling
   - Query optimization

### **Frontend Optimization**

1. **Code Splitting**:
   - Lazy load components
   - Route-based code splitting

2. **Asset Optimization**:
   - Image compression
   - SVG instead of PNG where possible
   - Minification and bundling

3. **Render Optimization**:
   - React.memo for expensive components
   - useMemo/useCallback hooks
   - Virtual scrolling for large lists

---

## **Security Considerations**

1. **API Keys**: Store in environment variables, never commit to Git
2. **CORS**: Restrict to known frontend origins
3. **Input Validation**: Validate all user inputs using Pydantic
4. **Rate Limiting**: Implement per-IP rate limits
5. **HTTPS**: Use HTTPS in production
6. **Authentication**: JWT tokens for user authentication (when implemented)

---

## **License**

This project is licensed under the MIT License.

---

## **Contributors**

NASA Space Apps Challenge 2025 Team

---

## **Acknowledgments**

- **NASA** for TEMPO satellite data and mission
- **OpenAQ** for global air quality data aggregation
- **EPA** for AirNow data and AQI standards
- **Pandora Project** for validation network data
- **OpenStreetMap** for geocoding services

---

## **Contact & Support**

- **GitHub Repository**: https://github.com/bethwel3001/predictions
- **Issues**: https://github.com/bethwel3001/predictions/issues

---

**Last Updated**: October 5, 2025  
**Version**: 0.2.0  
**Status**: Active Development

---

*Built with ❤️ for NASA Space Apps Challenge 2025*
