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
  FiMap,
  FiWind,
  FiDroplet,
  FiActivity,
} from "react-icons/fi";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Configuration - UPDATE THESE FOR PRODUCTION
const CONFIG = {
  API_BASE: "http://localhost:8000/api", // BACKEND: Update this to your backend API URL
  APP_NAME: "Predictors",
  MAX_AQI_THRESHOLD: 200,
  GEOLOCATION_TIMEOUT: 8000,
  REQUEST_TIMEOUT: 10000
};

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

// Animated Logo Component
const AnimatedLogo = () => {
  return (
    <div className="flex items-center gap-3">
      <div className="relative">
        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg animate-pulse">
          <FiActivity className="text-white text-lg animate-spin" style={{ animationDuration: '3s' }} />
        </div>
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
      </div>
      <div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Predictors
        </h1>
        <p className="text-sm text-gray-500">
          Air Quality Intelligence
        </p>
      </div>
    </div>
  );
};

// Enhanced Loading Animation Component
const LoadingAnimation = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="text-center">
        {/* Animated Logo */}
        <div className="mb-8">
          <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg mx-auto mb-4 animate-pulse">
            <FiActivity className="text-white text-2xl animate-spin" style={{ animationDuration: '2s' }} />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Predictors
          </h1>
          <p className="text-gray-600">Initializing Air Quality Monitor</p>
        </div>

        {/* Animated Dots */}
        <div className="flex justify-center space-x-2 mb-8">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>

        {/* Loading Progress */}
        <div className="w-64 bg-gray-200 rounded-full h-2 mx-auto overflow-hidden">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full animate-pulse"
            style={{ 
              width: '100%',
              animation: 'loadingBar 2s ease-in-out infinite'
            }}
          ></div>
        </div>

        <style jsx>{`
          @keyframes loadingBar {
            0% { transform: translateX(-100%); }
            50% { transform: translateX(0%); }
            100% { transform: translateX(100%); }
          }
        `}</style>
      </div>
    </div>
  );
};

// Skeleton Loading Component
const AQISkeleton = () => {
  return (
    <div className="w-full flex flex-col gap-8 animate-pulse">
      {/* AQI Summary Skeleton */}
      <section className="bg-white rounded-2xl shadow-sm p-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex-1">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
        <div className="text-center">
          <div className="h-4 bg-gray-200 rounded w-20 mb-2 mx-auto"></div>
          <div className="h-12 bg-gray-200 rounded w-24 mx-auto mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-16 mx-auto"></div>
        </div>
      </section>

      {/* Recommendation Skeleton */}
      <section className="rounded-2xl shadow-sm p-6">
        <div className="h-6 bg-gray-200 rounded w-3/4 mx-auto"></div>
      </section>

      {/* Graph Skeleton */}
      <section className="bg-white rounded-2xl shadow-sm p-6">
        <div className="h-5 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="w-full h-40 flex items-end justify-between gap-2">
          {[...Array(5)].map((_, idx) => (
            <div
              key={idx}
              className="flex-1 bg-gray-200 rounded-t-lg"
              style={{ height: `${Math.random() * 80 + 20}%` }}
            ></div>
          ))}
        </div>
      </section>

      {/* Nearby Areas Skeleton */}
      <section>
        <div className="h-5 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-gray-200 text-center">
              <div className="h-5 bg-gray-300 rounded w-3/4 mx-auto mb-2"></div>
              <div className="h-4 bg-gray-300 rounded w-1/2 mx-auto"></div>
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
            <FiAlertTriangle className="text-6xl text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition"
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
        // Silent fail for auto-detect on load
        console.log('Auto-location detection failed on load:', err.message);
      } finally {
        // Hide initial loading animation after 2 seconds minimum
        setTimeout(() => setInitialLoading(false), 2000);
      }
    };
    
    initApp();
  }, []);

  const getCurrentPosition = useCallback(() => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'));
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
              errorMessage = 'Location access denied. Please enable location permissions.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information unavailable.';
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timed out.';
              break;
            default:
              errorMessage = 'An unknown error occurred while getting location.';
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
    
    try {
      const position = await getCurrentPosition();
      await fetchDataByCoords(position.latitude, position.longitude);
    } catch (err) {
      setLocationError(err.message);
      setLoading(false);
    }
  };

  // BACKEND INTEGRATION: Fetch air quality data by coordinates
  // ROUTE: GET /api/airquality?lat={latitude}&lon={longitude}
  const fetchDataByCoords = async (lat, lon) => {
    try {
      // BACKEND: This endpoint should return air quality data for coordinates
      // Expected response format:
      // {
      //   city: "City Name",
      //   aqi: 85,
      //   timestamp: "2024-01-15T10:30:00Z",
      //   recent: [80, 82, 85, 83, 85], // Last 5 hours AQI data
      //   coordinates: { lat, lon }
      // }
      const { data } = await axios.get(`${CONFIG.API_BASE}/airquality`, {
        params: { lat, lon },
        timeout: CONFIG.REQUEST_TIMEOUT
      });
      
      setAqiData(data);
      setError("");

      // Handle severe alert
      handleSevereAlert(data.aqi);

      // BACKEND INTEGRATION: Fetch nearby areas data
      // ROUTE: GET /api/nearby?lat={latitude}&lon={longitude}&radius=50
      // This endpoint should return nearby areas with their AQI status
      // Expected response format: array of { name: "Area Name", aqi: number, safe: boolean }
      try {
        const nearbyResponse = await axios.get(`${CONFIG.API_BASE}/nearby`, {
          params: { lat, lon, radius: 50 }, // 50km radius
          timeout: CONFIG.REQUEST_TIMEOUT
        });
        setNearbyAreas(nearbyResponse.data);
      } catch (nearbyErr) {
        console.warn('Failed to fetch nearby areas:', nearbyErr.message);
        setNearbyAreas([]);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || 
                          err.code === 'ECONNABORTED' ? 
                          'Request timeout. Please try again.' : 
                          'Error fetching air quality data. ';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationInputChange = (value) => {
    setLocationInput(value);
    
    // Clear existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    // Set new timeout for debounced search
    if (value.trim()) {
      searchTimeoutRef.current = setTimeout(() => {
        if (validateCityName(value)) {
          handleFetchByCity(false);
        }
      }, 1000);
    }
  };

  // BACKEND INTEGRATION: Fetch air quality data by city name
  // ROUTE: GET /api/airquality?city={cityName}
  const handleFetchByCity = async (isRefresh = false) => {
    if (!validateCityName(locationInput)) {
      setError("Please enter a valid city name (letters, spaces, hyphens, and commas only)");
      return;
    }

    setAutoDetected(false);
    setNearbyAreas([]);
    isRefresh ? setRefreshing(true) : setLoading(true);
    setError("");

    try {
      const sanitizedCity = sanitizeInput(locationInput);
      
      // BACKEND: This endpoint should return air quality data for city name
      // Expected response format same as coordinates endpoint
      const { data } = await axios.get(`${CONFIG.API_BASE}/airquality`, {
        params: { city: sanitizedCity },
        timeout: CONFIG.REQUEST_TIMEOUT
      });
      
      setAqiData(data);

      // Handle severe alert
      handleSevereAlert(data.aqi);

      // BACKEND: Optionally fetch nearby areas for city as well
      // This can be implemented if your backend supports it
      setNearbyAreas([]); // Clear nearby areas for city search

    } catch (err) {
      const errorMessage = err.response?.data?.message || 
                          'Failed to fetch data for the selected city. Please check the city name.';
      setError(errorMessage);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    if (autoDetected && aqiData?.coordinates) {
      // Refresh with current coordinates
      await fetchDataByCoords(aqiData.coordinates.lat, aqiData.coordinates.lon);
    } else if (locationInput) {
      // Refresh with current city
      await handleFetchByCity(true);
    } else {
      toast.info("Please enter a city name or allow location access to refresh data");
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
    return <LoadingAnimation />;
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 to-purple-50 text-gray-800">
        <ToastContainer 
          position="top-center"
          autoClose={5000}
          hideProgressBar={false}
          closeOnClick
          pauseOnHover
        />

        {/* HEADER */}
        <header className="w-full max-w-6xl mx-auto mt-6 px-4 flex flex-col md:flex-row items-center justify-between gap-3">
          <AnimatedLogo />

          <div className="flex items-center gap-3">
            {/* Notification Icon */}
            <div className="relative">
              <FiBell
                className={`text-2xl cursor-pointer ${
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

            {/* Search Bar */}
            <div className="flex items-center border border-gray-200 rounded-lg px-3 py-2 bg-white focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent shadow-sm">
              <FiMapPin className="text-gray-500 text-lg mr-2" />
              <input
                type="text"
                placeholder="Enter city..."
                className="outline-none text-sm w-32 md:w-48 bg-transparent"
                value={locationInput}
                onChange={(e) => handleLocationInputChange(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleFetchByCity(false)}
                aria-label="Enter city name for air quality search"
                maxLength={100}
              />
            </div>

            {/* Buttons */}
            <button
              onClick={() => handleFetchByCity(false)}
              disabled={loading || refreshing || !locationInput.trim()}
              className="bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-2 rounded-lg text-sm hover:from-green-600 hover:to-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
              aria-label="Load air quality data"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <FiLoader className="animate-spin" /> Loading...
                </span>
              ) : (
                "Load"
              )}
            </button>

            <button
              onClick={handleRefresh}
              disabled={loading || refreshing || (!autoDetected && !locationInput)}
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:from-blue-600 hover:to-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
              aria-label="Refresh air quality data"
            >
              {refreshing ? (
                <span className="flex items-center gap-2">
                  <FiRefreshCcw className="animate-spin" /> Refreshing...
                </span>
              ) : (
                "Refresh"
              )}
            </button>
          </div>
        </header>

        {/* MAIN CONTENT */}
        <main className="flex-1 w-full max-w-6xl mx-auto px-4 py-8 flex flex-col items-center justify-center">
          {/* ERROR */}
          {displayError && (
            <div className="text-center flex flex-col items-center gap-4 max-w-md">
              <FiAlertTriangle className="text-6xl text-red-500 animate-bounce" />
              <p className="text-lg font-medium text-red-600">{displayError}</p>
              <p className="text-sm text-gray-500">
                Please check your internet connection or API server, then try again.
              </p>
              <div className="flex gap-3 mt-2">
                <button
                  onClick={handleAutoDetectLocation}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-600 transition"
                >
                  Retry Detect Location
                </button>
                <button
                  onClick={clearAllErrors}
                  className="bg-gray-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-600 transition"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )}

          {/* LOADING SKELETON */}
          {(loading || refreshing) && <AQISkeleton />}

          {/* DEFAULT STATE */}
          {!loading && !refreshing && !aqiData && !displayError && (
            <div className="text-center flex flex-col items-center gap-3 text-gray-500">
              <div className="relative">
                <FiCloud className="text-6xl text-blue-300 animate-pulse" />
                <FiWind className="text-3xl text-purple-300 absolute -top-2 -right-2 animate-pulse" style={{ animationDelay: '1s' }} />
              </div>
              <p className="text-sm">
                Enter a city and click <strong>Load</strong> to view air quality.
              </p>
              <button
                onClick={handleAutoDetectLocation}
                className="mt-4 text-blue-500 hover:text-blue-700 text-sm underline flex items-center gap-2"
              >
                <FiMap className="text-sm" />
                Or use my current location
              </button>
            </div>
          )}

          {/* DATA DISPLAY */}
          {aqiData && !loading && !refreshing && !displayError && (
            <div className="w-full flex flex-col gap-8">
              {/* AQI Summary */}
              <section className="bg-white rounded-2xl shadow-sm p-6 flex flex-col md:flex-row items-center justify-between gap-6">
                <div>
                  <h2 className="text-lg font-semibold">{aqiData.city}</h2>
                  <p className="text-gray-500 text-sm">
                    Last updated: {aqiData.timestamp || new Date().toLocaleString()}
                  </p>
                  {aqiData.coordinates && (
                    <p className="text-gray-400 text-xs mt-1">
                      Coordinates: {aqiData.coordinates.lat.toFixed(4)}, {aqiData.coordinates.lon.toFixed(4)}
                    </p>
                  )}
                </div>
                <div className="text-center">
                  <p className="text-gray-500 text-sm">Current AQI</p>
                  <h2 className={`text-5xl font-bold ${getAQIColor(aqiData.aqi)}`}>
                    {aqiData.aqi}
                  </h2>
                  <p className="text-sm text-gray-600">
                    {getAQIStatus(aqiData.aqi)}
                  </p>
                </div>
              </section>

              {/* Recommendation & Health Implications */}
              <section className={`rounded-2xl shadow-sm p-6 text-white ${getAQIBgColor(aqiData.aqi)}`}>
                <div className="text-center mb-3">
                  <p className="text-lg font-semibold">{getRecommendation(aqiData.aqi)}</p>
                </div>
                <div className="text-center text-sm opacity-90">
                  <p>Health Implications: {getHealthImplications(aqiData.aqi)}</p>
                </div>
              </section>

              {/* AQI Trend Graph */}
              {/* BACKEND: This section requires recent AQI data array from backend */}
              {aqiData.recent && aqiData.recent.length > 0 && (
                <section className="bg-white rounded-2xl shadow-sm p-6">
                  <h3 className="font-medium mb-4 text-gray-700">
                    AQI Trend (Past {aqiData.recent.length} Hours)
                  </h3>
                  <div className="w-full h-40 flex items-end justify-between gap-2">
                    {aqiData.recent.map((val, idx) => (
                      <div
                        key={idx}
                        className={`flex-1 rounded-t-lg transition-all duration-500 ${
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
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>Earlier</span>
                    <span>Now</span>
                  </div>
                </section>
              )}

              {/* Pollutant Data */}
              {/* BACKEND: Add this section if your backend provides pollutant breakdown */}
              {/* ROUTE: GET /api/airquality should include pollutants object */}
              {aqiData.pollutants && (
                <section className="bg-white rounded-2xl shadow-sm p-6">
                  <h3 className="font-medium mb-4 text-gray-700">
                    Pollutant Levels
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(aqiData.pollutants).map(([pollutant, value]) => (
                      <div key={pollutant} className="text-center p-3 bg-gray-50 rounded-lg">
                        <p className="font-medium text-gray-700 capitalize">{pollutant}</p>
                        <p className="text-lg font-semibold text-blue-600">{value}</p>
                        <p className="text-xs text-gray-500">μg/m³</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Nearby Areas */}
              {/* BACKEND: This section requires nearby areas data from /nearby endpoint */}
              {/* ROUTE: GET /api/nearby?lat={lat}&lon={lon}&radius=50 */}
              {nearbyAreas.length > 0 && (
                <section className="bg-white rounded-2xl shadow-sm p-6">
                  <h3 className="font-medium mb-4 text-gray-700">
                    Nearby Areas (within 50km)
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {nearbyAreas.map((area, index) => (
                      <div
                        key={`${area.name}-${index}`}
                        className={`p-4 rounded-xl shadow-sm text-center border-2 ${
                          area.safe ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"
                        }`}
                      >
                        <h4 className="font-medium text-gray-700 mb-2">
                          {area.name}
                        </h4>
                        <p className={`text-sm font-semibold ${
                          area.safe ? "text-green-700" : "text-red-700"
                        }`}>
                          {area.safe ? "Safe" : "Unsafe"}
                        </p>
                        {area.aqi && (
                          <p className="text-xs text-gray-600 mt-1">
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
        </main>

        {/* FOOTER - No border line */}
        <footer className="w-full mt-auto py-6 bg-transparent text-center text-xs text-gray-400">
          <div className="max-w-6xl mx-auto px-4">
            <p>© 2025 {CONFIG.APP_NAME} — NASA Space Apps Challenge</p>
            <p className="mt-1">Real-time air quality predictions and monitoring</p>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;