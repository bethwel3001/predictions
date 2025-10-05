import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import React from "react";
import {
  FiMapPin,
  FiBell,
  FiAlertTriangle,
  FiLoader,
  FiCloud,
  FiRefreshCcw,
  FiActivity,
  FiSearch,
} from "react-icons/fi";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// =============================================================================
// BACKEND API CONFIGURATION
// =============================================================================
// UPDATE THESE FOR PRODUCTION
const CONFIG = {
  // Base URL for all API endpoints - update this to your backend server
  API_BASE: "http://localhost:8000/api",
  APP_NAME: "Predictors",
  MAX_AQI_THRESHOLD: 200,
  GEOLOCATION_TIMEOUT: 8000,
  REQUEST_TIMEOUT: 10000
};

// =============================================================================
// EXPECTED BACKEND API ENDPOINT STRUCTURES
// =============================================================================

/*
// ENDPOINT 1: Get Air Quality Data by Coordinates
// URL: GET /api/airquality?lat={latitude}&lon={longitude}
// Expected Response Format:
{
  "city": "New York",
  "aqi": 45,
  "coordinates": {
    "lat": 40.7128,
    "lon": -74.0060
  },
  "timestamp": "2025-01-15T10:30:00Z",
  "pollutants": {
    "pm2_5": 12.5,
    "pm10": 23.1,
    "no2": 18.7,
    "o3": 45.2,
    "so2": 5.1,
    "co": 0.8
  },
  "recent": [42, 44, 46, 43, 45] // Last 5 hours AQI values
}

// ENDPOINT 2: Get Air Quality Data by City Name
// URL: GET /api/airquality?city={cityName}
// Expected Response Format: Same as above

// ENDPOINT 3: Get Nearby Areas
// URL: GET /api/nearby?lat={latitude}&lon={longitude}&radius={radiusInKm}
// Expected Response Format:
[
  {
    "name": "Brooklyn",
    "aqi": 48,
    "safe": true,
    "distance": 8.5
  },
  {
    "name": "Queens", 
    "aqi": 52,
    "safe": true,
    "distance": 12.3
  },
  {
    "name": "Jersey City",
    "aqi": 65,
    "safe": true,
    "distance": 6.7
  }
]

// ENDPOINT 4: Get AQI Forecast (Optional Enhancement)
// URL: GET /api/forecast?lat={lat}&lon={lon}&days=3
// Expected Response Format:
{
  "city": "New York",
  "forecast": [
    {
      "date": "2025-01-15",
      "aqi": 45,
      "status": "Good",
      "pollutants": { ... }
    },
    {
      "date": "2025-01-16", 
      "aqi": 68,
      "status": "Moderate",
      "pollutants": { ... }
    }
  ]
}

// ENDPOINT 5: Get Historical Data (Optional Enhancement)  
// URL: GET /api/history?lat={lat}&lon={lon}&days=7
// Expected Response Format:
{
  "city": "New York",
  "historical": [
    {
      "date": "2025-01-08",
      "aqi": 42,
      "dominant_pollutant": "pm2_5"
    },
    // ... more days
  ]
}
*/

// =============================================================================
// AQI CONSTANTS AND UTILITIES
// =============================================================================

// AQI Constants
const AQI_THRESHOLDS = {
  GOOD: 50,
  MODERATE: 100,
  UNHEALTHY_SENSITIVE: 150,
  UNHEALTHY: 200,
  VERY_UNHEALTHY: 300,
  HAZARDOUS: 301
};

const AQI_STATUS = {
  0: "Good",
  1: "Moderate", 
  2: "Unhealthy for Sensitive Groups",
  3: "Unhealthy",
  4: "Very Unhealthy",
  5: "Hazardous"
};

const AQI_COLORS = {
  GOOD: "text-green-600",
  MODERATE: "text-yellow-600",
  UNHEALTHY_SENSITIVE: "text-orange-600",
  UNHEALTHY: "text-red-600",
  VERY_UNHEALTHY: "text-red-700",
  HAZARDOUS: "text-purple-600"
};

const AQI_BG_COLORS = {
  GOOD: "bg-green-500",
  MODERATE: "bg-yellow-500",
  UNHEALTHY_SENSITIVE: "bg-orange-500",
  UNHEALTHY: "bg-red-500",
  VERY_UNHEALTHY: "bg-red-600",
  HAZARDOUS: "bg-purple-600"
};

// Utility Functions
const sanitizeInput = (input) => {
  if (!input || typeof input !== 'string') return '';
  return input.trim().replace(/[^a-zA-Z\s,-]/g, '');
};

const validateCityName = (city) => {
  if (!city || typeof city !== 'string') return false;
  
  const trimmed = city.trim();
  if (trimmed.length < 1 || trimmed.length > 100) return false;
  
  const validPattern = /^[a-zA-Z\s,-]+$/;
  return validPattern.test(trimmed);
};

const getAQIStatus = (aqi) => {
  if (aqi <= AQI_THRESHOLDS.GOOD) return AQI_STATUS[0];
  if (aqi <= AQI_THRESHOLDS.MODERATE) return AQI_STATUS[1];
  if (aqi <= AQI_THRESHOLDS.UNHEALTHY_SENSITIVE) return AQI_STATUS[2];
  if (aqi <= AQI_THRESHOLDS.UNHEALTHY) return AQI_STATUS[3];
  if (aqi <= AQI_THRESHOLDS.VERY_UNHEALTHY) return AQI_STATUS[4];
  return AQI_STATUS[5];
};

const getAQIColor = (aqi) => {
  if (aqi <= AQI_THRESHOLDS.GOOD) return AQI_COLORS.GOOD;
  if (aqi <= AQI_THRESHOLDS.MODERATE) return AQI_COLORS.MODERATE;
  if (aqi <= AQI_THRESHOLDS.UNHEALTHY_SENSITIVE) return AQI_COLORS.UNHEALTHY_SENSITIVE;
  if (aqi <= AQI_THRESHOLDS.UNHEALTHY) return AQI_COLORS.UNHEALTHY;
  if (aqi <= AQI_THRESHOLDS.VERY_UNHEALTHY) return AQI_COLORS.VERY_UNHEALTHY;
  return AQI_COLORS.HAZARDOUS;
};

const getAQIBgColor = (aqi) => {
  if (aqi <= AQI_THRESHOLDS.GOOD) return AQI_BG_COLORS.GOOD;
  if (aqi <= AQI_THRESHOLDS.MODERATE) return AQI_BG_COLORS.MODERATE;
  if (aqi <= AQI_THRESHOLDS.UNHEALTHY_SENSITIVE) return AQI_BG_COLORS.UNHEALTHY_SENSITIVE;
  if (aqi <= AQI_THRESHOLDS.UNHEALTHY) return AQI_BG_COLORS.UNHEALTHY;
  if (aqi <= AQI_THRESHOLDS.VERY_UNHEALTHY) return AQI_BG_COLORS.VERY_UNHEALTHY;
  return AQI_BG_COLORS.HAZARDOUS;
};

const isSevereAQI = (aqi) => {
  return aqi > AQI_THRESHOLDS.UNHEALTHY;
};

// =============================================================================
// UI COMPONENTS
// =============================================================================

// Hero Loading Overlay Component
const HeroLoadingOverlay = ({ message = "Loading air quality data..." }) => {
  return (
    <div className="absolute inset-0 bg-white bg-opacity-90 backdrop-blur-sm flex items-center justify-center rounded-xl z-10">
      <div className="text-center space-y-4">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">{message}</p>
          <p className="text-xs text-gray-500">Please wait while we fetch the latest data</p>
        </div>
      </div>
    </div>
  );
};

// Initial Loading Animation Component
const InitialLoadingAnimation = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="text-center space-y-4">
        <div className="mb-4">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-3 shadow-lg">
            <FiActivity className="text-white text-xl" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Predictors
          </h1>
        </div>

        <div className="space-y-3">
          <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-gray-500 font-medium">Initializing air quality monitor...</p>
        </div>
      </div>
    </div>
  );
};

// Enhanced Skeleton Loading Component
const AQISkeleton = () => {
  return (
    <div className="w-full flex flex-col gap-6 animate-pulse">
      {/* AQI Summary Skeleton */}
      <section className="bg-white rounded-xl shadow-sm p-5 flex flex-col md:flex-row items-center justify-between gap-5">
        <div className="flex-1">
          <div className="h-5 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/4"></div>
        </div>
        <div className="text-center">
          <div className="h-3 bg-gray-200 rounded w-16 mb-2 mx-auto"></div>
          <div className="h-10 bg-gray-200 rounded w-20 mx-auto mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-12 mx-auto"></div>
        </div>
      </section>

      {/* Recommendation Skeleton */}
      <section className="rounded-xl shadow-sm p-5 bg-gray-200">
        <div className="h-5 bg-gray-300 rounded w-3/4 mx-auto"></div>
      </section>

      {/* Graph Skeleton */}
      <section className="bg-white rounded-xl shadow-sm p-5">
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="w-full h-32 flex items-end justify-between gap-1">
          {[...Array(5)].map((_, idx) => (
            <div
              key={idx}
              className="flex-1 bg-gray-200 rounded-t-lg"
              style={{ height: `${Math.random() * 70 + 20}%` }}
            ></div>
          ))}
        </div>
      </section>

      {/* Nearby Areas Skeleton */}
      <section>
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-3"></div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {[...Array(4)].map((_, idx) => (
            <div key={idx} className="p-3 rounded-lg bg-gray-200 text-center">
              <div className="h-4 bg-gray-300 rounded w-3/4 mx-auto mb-1"></div>
              <div className="h-3 bg-gray-300 rounded w-1/2 mx-auto"></div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center max-w-md mx-auto p-6">
            <FiAlertTriangle className="text-5xl text-red-500 mx-auto mb-3" />
            <h2 className="text-lg font-semibold text-gray-800 mb-2">
              Application Error
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Something unexpected occurred. Please refresh the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-500 text-white px-5 py-2 rounded-lg hover:bg-blue-600 transition text-sm"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Enhanced Error Display Component
const ErrorDisplay = ({ error, onRetry, onDismiss }) => {
  return (
    <div className="w-full max-w-2xl mx-auto text-center flex flex-col items-center gap-4">
      <FiAlertTriangle className="text-4xl text-red-500" />
      <div className="space-y-2">
        <p className="text-sm font-medium text-red-600">{error}</p>
        <p className="text-xs text-gray-500">
          Please check your connection and try again.
        </p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={onRetry}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-600 transition flex items-center gap-2"
        >
          <FiRefreshCcw className="text-sm" />
          Try Again
        </button>
        <button
          onClick={onDismiss}
          className="bg-gray-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-600 transition"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
};

// =============================================================================
// MAIN APP COMPONENT WITH BACKEND INTEGRATION
// =============================================================================

// Main App Component
function App() {
  const [locationInput, setLocationInput] = useState("");
  const [aqiData, setAqiData] = useState(null);
  const [nearbyAreas, setNearbyAreas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [locationError, setLocationError] = useState("");
  const [severe, setSevere] = useState(false);
  const [autoDetected, setAutoDetected] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  
  const searchTimeoutRef = useRef(null);

  // Combined error state
  const displayError = error || locationError;

  // Detect location on load with initial loading animation
  useEffect(() => {
    const initApp = async () => {
      try {
        await handleAutoDetectLocation();
      } catch (err) {
        console.log('Auto-location detection failed on load:', err.message);
        setInitialLoading(false);
      }
    };
    
    initApp();
  }, []);

  const getCurrentPosition = useCallback(() => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          resolve({ latitude, longitude });
        },
        (error) => {
          let errorMessage;
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location access denied';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location unavailable';
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timeout';
              break;
            default:
              errorMessage = 'Failed to get location';
          }
          reject(new Error(errorMessage));
        },
        {
          timeout: CONFIG.GEOLOCATION_TIMEOUT,
          enableHighAccuracy: false,
          maximumAge: 5 * 60 * 1000
        }
      );
    });
  }, []);

  const handleSevereAlert = useCallback((aqi) => {
    const isSevere = aqi > CONFIG.MAX_AQI_THRESHOLD;
    if (isSevere) {
      setSevere(true);
      toast.error("Air quality is dangerously poor in this area!");
    } else {
      setSevere(false);
    }
    return isSevere;
  }, []);

  const handleAutoDetectLocation = async () => {
    setAutoDetected(true);
    setLocationError("");
    setLoading(true);
    setError("");
    
    try {
      const position = await getCurrentPosition();
      await fetchDataByCoords(position.latitude, position.longitude);
    } catch (err) {
      setLocationError(err.message);
      setLoading(false);
      setInitialLoading(false);
    }
  };

  // =============================================================================
  // BACKEND API INTEGRATION POINTS
  // =============================================================================

  // BACKEND INTEGRATION: Fetch air quality data by coordinates
  // This function calls: GET /api/airquality?lat={latitude}&lon={longitude}
  const fetchDataByCoords = async (lat, lon) => {
    try {
      // API CALL 1: Get main air quality data
      const { data } = await axios.get(`${CONFIG.API_BASE}/airquality`, {
        params: { lat, lon },
        timeout: CONFIG.REQUEST_TIMEOUT
      });
      
      setAqiData(data);
      setError("");

      handleSevereAlert(data.aqi);

      // API CALL 2: Get nearby areas data (optional - can be commented out if not implemented)
      try {
        const nearbyResponse = await axios.get(`${CONFIG.API_BASE}/nearby`, {
          params: { lat, lon, radius: 50 },
          timeout: CONFIG.REQUEST_TIMEOUT
        });
        setNearbyAreas(nearbyResponse.data);
      } catch (nearbyErr) {
        console.warn('Failed to fetch nearby areas:', nearbyErr.message);
        setNearbyAreas([]);
      }

      // POTENTIAL ENHANCEMENT: Uncomment to add forecast data
      /*
      try {
        const forecastResponse = await axios.get(`${CONFIG.API_BASE}/forecast`, {
          params: { lat, lon, days: 3 }
        });
        // setForecastData(forecastResponse.data);
      } catch (forecastErr) {
        console.warn('Forecast data not available:', forecastErr.message);
      }
      */

    } catch (err) {
      const errorMessage = err.response?.data?.message || 
                          err.code === 'ECONNABORTED' ? 
                          'Request timeout - please try again' : 
                          'Failed to connect to server - check your connection';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  };

  const handleLocationInputChange = (value) => {
    setLocationInput(value);
    
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (value.trim()) {
      searchTimeoutRef.current = setTimeout(() => {
        if (validateCityName(value)) {
          handleFetchByCity(false);
        }
      }, 800);
    }
  };

  // BACKEND INTEGRATION: Fetch air quality data by city name
  // This function calls: GET /api/airquality?city={cityName}
  const handleFetchByCity = async (isRefresh = false) => {
    if (!validateCityName(locationInput)) {
      setError("Please enter a valid city name");
      return;
    }

    setAutoDetected(false);
    setNearbyAreas([]);
    isRefresh ? setRefreshing(true) : setLoading(true);
    setError("");

    try {
      const sanitizedCity = sanitizeInput(locationInput);
      
      // API CALL: Get air quality data by city name
      const { data } = await axios.get(`${CONFIG.API_BASE}/airquality`, {
        params: { city: sanitizedCity },
        timeout: CONFIG.REQUEST_TIMEOUT
      });
      
      setAqiData(data);
      handleSevereAlert(data.aqi);
      setNearbyAreas([]);

    } catch (err) {
      const errorMessage = err.response?.data?.message || 
                          err.code === 'ECONNABORTED' ? 
                          'Request timeout - please try again' : 
                          'City not found or server error - check the city name';
      setError(errorMessage);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    if (autoDetected && aqiData?.coordinates) {
      await fetchDataByCoords(aqiData.coordinates.lat, aqiData.coordinates.lon);
    } else if (locationInput) {
      await handleFetchByCity(true);
    } else {
      toast.info("Enter a city name or allow location access to refresh");
    }
  };

  const clearAllErrors = useCallback(() => {
    setError("");
    setLocationError("");
  }, []);

  const getRecommendation = (aqi) => {
    if (aqi <= 50) {
      return "Air quality is excellent. Perfect for outdoor activities!";
    } else if (aqi <= 100) {
      return "Air quality is acceptable. Generally safe for outdoor activities.";
    } else if (aqi <= 150) {
      return "Unhealthy for sensitive groups. Consider reducing prolonged outdoor exertion.";
    } else if (aqi <= 200) {
      return "Unhealthy air quality. Everyone may experience health effects.";
    } else if (aqi <= 300) {
      return "Very unhealthy air quality. Avoid outdoor activities.";
    } else {
      return "Hazardous air quality. Stay indoors with air purifiers.";
    }
  };

  const getHealthImplications = (aqi) => {
    if (aqi <= 50) {
      return "Little to no risk";
    } else if (aqi <= 100) {
      return "Moderate health concern for very sensitive individuals";
    } else if (aqi <= 150) {
      return "Increased risk for children, elderly, and people with respiratory conditions";
    } else if (aqi <= 200) {
      return "Everyone may begin to experience health effects";
    } else if (aqi <= 300) {
      return "Health warnings of emergency conditions";
    } else {
      return "Health alert: everyone may experience more serious health effects";
    }
  };

  // Show initial loading animation
  if (initialLoading) {
    return <InitialLoadingAnimation />;
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
        <ToastContainer 
          position="top-center"
          autoClose={5000}
          hideProgressBar={false}
          closeOnClick
          pauseOnHover
          toastClassName="text-sm"
        />

        {/* HEADER - Always visible */}
        <header className="w-full max-w-6xl mx-auto mt-4 px-4 flex flex-col md:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-sm">
              <FiActivity className="text-white text-base" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Predictors</h1>
              <p className="text-xs text-gray-500">
                Air Quality Insights {autoDetected && "(auto-detected)"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <FiBell
                className={`text-xl cursor-pointer ${
                  severe
                    ? "text-red-500 animate-pulse"
                    : "text-gray-400 hover:text-gray-600"
                }`}
                onClick={() =>
                  toast.info(
                    severe
                      ? "AQI Alert: Air quality is hazardous. Stay indoors!"
                      : "No active alerts at the moment."
                  )
                }
                aria-label="Notifications"
              />
            </div>

            <div className="flex items-center border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
              <FiMapPin className="text-gray-500 text-base mr-2" />
              <input
                type="text"
                placeholder="Enter city..."
                className="outline-none text-sm w-28 md:w-40 bg-transparent"
                value={locationInput}
                onChange={(e) => handleLocationInputChange(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleFetchByCity(false)}
                aria-label="Enter city name for air quality search"
                maxLength={100}
              />
            </div>

            <button
              onClick={() => handleFetchByCity(false)}
              disabled={loading || refreshing || !locationInput.trim()}
              className="bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              aria-label="Load air quality data"
            >
              {loading ? (
                <>
                  <FiLoader className="animate-spin text-xs" /> 
                  Loading
                </>
              ) : (
                <>
                  <FiSearch className="text-xs" />
                  Search
                </>
              )}
            </button>

            <button
              onClick={handleRefresh}
              disabled={loading || refreshing || (!autoDetected && !locationInput)}
              className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              aria-label="Refresh air quality data"
            >
              {refreshing ? (
                <>
                  <FiRefreshCcw className="animate-spin text-xs" /> 
                </>
              ) : (
                <>
                  <FiRefreshCcw className="text-xs" />
                  Refresh
                </>
              )}
            </button>
          </div>
        </header>

        {/* MAIN CONTENT - With loading overlay */}
        <main className="flex-1 w-full max-w-6xl mx-auto px-4 py-6">
          <div className="relative min-h-[400px]">
            {/* LOADING OVERLAY - Covers entire hero area */}
            {(loading || refreshing) && (
              <HeroLoadingOverlay 
                message={refreshing ? "Refreshing air quality data..." : "Loading air quality data..."}
              />
            )}

            {/* ERROR DISPLAY */}
            {displayError && !loading && !refreshing && (
              <ErrorDisplay 
                error={displayError}
                onRetry={handleAutoDetectLocation}
                onDismiss={clearAllErrors}
              />
            )}

            {/* DEFAULT STATE */}
            {!loading && !refreshing && !aqiData && !displayError && (
              <div className="w-full text-center flex flex-col items-center gap-3">
                <FiCloud className="text-6xl text-blue-300 mb-2" />
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    Enter a city and click <strong>Search</strong> to view air quality data
                  </p>
                  <p className="text-xs text-gray-500">
                    Or use your current location for automatic detection
                  </p>
                </div>
                <button
                  onClick={handleAutoDetectLocation}
                  className="mt-4 text-blue-500 hover:text-blue-700 text-sm underline"
                >
                  Use my current location
                </button>
              </div>
            )}

            {/* DATA DISPLAY */}
            {aqiData && !loading && !refreshing && !displayError && (
              <div className="w-full flex flex-col gap-6">
                {/* AQI Summary */}
                <section className="bg-white rounded-xl shadow-sm p-5 flex flex-col md:flex-row items-center justify-between gap-4">
                  <div>
                    <h2 className="text-base font-semibold">{aqiData.city}</h2>
                    <p className="text-gray-500 text-xs">
                      Updated: {aqiData.timestamp || new Date().toLocaleString()}
                    </p>
                    {aqiData.coordinates && (
                      <p className="text-gray-400 text-xs mt-0.5">
                        Coordinates: {aqiData.coordinates.lat.toFixed(4)}, {aqiData.coordinates.lon.toFixed(4)}
                      </p>
                    )}
                  </div>
                  <div className="text-center">
                    <p className="text-gray-500 text-xs">Current AQI</p>
                    <h2 className={`text-4xl font-bold ${getAQIColor(aqiData.aqi)}`}>
                      {aqiData.aqi}
                    </h2>
                    <p className="text-xs text-gray-600">
                      {getAQIStatus(aqiData.aqi)}
                    </p>
                  </div>
                </section>

                {/* Recommendation & Health Implications */}
                <section className={`rounded-xl shadow-sm p-5 text-white ${getAQIBgColor(aqiData.aqi)}`}>
                  <div className="text-center mb-2">
                    <p className="text-sm font-semibold">{getRecommendation(aqiData.aqi)}</p>
                  </div>
                  <div className="text-center text-xs opacity-90">
                    <p>Health Implications: {getHealthImplications(aqiData.aqi)}</p>
                  </div>
                </section>

                {/* AQI Trend Graph */}
                {aqiData.recent && aqiData.recent.length > 0 && (
                  <section className="bg-white rounded-xl shadow-sm p-5">
                    <h3 className="font-medium mb-3 text-gray-700 text-sm">
                      AQI Trend (Past {aqiData.recent.length} Hours)
                    </h3>
                    <div className="w-full h-32 flex items-end justify-between gap-1">
                      {aqiData.recent.map((val, idx) => (
                        <div
                          key={idx}
                          className={`flex-1 rounded-t-lg transition-all duration-300 ${
                            val > 100 ? "bg-red-400" : "bg-green-400"
                          }`}
                          style={{ height: `${Math.min((val / 300) * 100, 100)}%` }}
                          aria-label={`AQI value ${val} for hour ${idx + 1}`}
                        >
                          <div className="text-xs text-center mt-1 text-gray-600">
                            {val}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Earlier</span>
                      <span>Now</span>
                    </div>
                  </section>
                )}

                {/* Pollutant Data */}
                {aqiData.pollutants && (
                  <section className="bg-white rounded-xl shadow-sm p-5">
                    <h3 className="font-medium mb-3 text-gray-700 text-sm">
                      Pollutant Levels
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(aqiData.pollutants).map(([pollutant, value]) => (
                        <div key={pollutant} className="text-center p-2 bg-gray-50 rounded-lg">
                          <p className="font-medium text-gray-700 text-xs capitalize">{pollutant}</p>
                          <p className="text-base font-semibold text-blue-600">{value}</p>
                          <p className="text-xs text-gray-500">μg/m³</p>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {/* Nearby Areas */}
                {nearbyAreas.length > 0 && (
                  <section className="bg-white rounded-xl shadow-sm p-5">
                    <h3 className="font-medium mb-3 text-gray-700 text-sm">
                      Nearby Areas (within 50km)
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {nearbyAreas.map((area, index) => (
                        <div
                          key={`${area.name}-${index}`}
                          className={`p-3 rounded-lg shadow-sm text-center border ${
                            area.safe ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"
                          }`}
                        >
                          <h4 className="font-medium text-gray-700 text-xs mb-1">
                            {area.name}
                          </h4>
                          <p className={`text-xs font-semibold ${
                            area.safe ? "text-green-700" : "text-red-700"
                          }`}>
                            {area.safe ? "Safe" : "Unsafe"}
                          </p>
                          {area.aqi && (
                            <p className="text-xs text-gray-600 mt-0.5">
                              AQI: {area.aqi}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                )}
              </div>
            )}
          </div>
        </main>

        {/* FOOTER */}
        <footer className="w-full mt-auto py-4 text-center text-xs text-gray-400">
          <div className="max-w-6xl mx-auto px-4">
            <p>© 2025 {CONFIG.APP_NAME} — NASA Space Apps Challenge</p>
            <p className="mt-0.5">Real-time air quality predictions and monitoring</p>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;