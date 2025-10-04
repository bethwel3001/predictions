import { useState, useEffect } from "react";
import axios from "axios";
import {
  FiMapPin,
  FiBell,
  FiAlertCircle,
  FiLoader,
  FiCloud,
  FiRefreshCcw,
} from "react-icons/fi";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  const [location, setLocation] = useState("");
  const [aqiData, setAqiData] = useState(null);
  const [nearbyAreas, setNearbyAreas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [severe, setSevere] = useState(false);
  const [autoDetected, setAutoDetected] = useState(false);

  const API_BASE = "http://localhost:8000/api";

  // Detect location on load
  useEffect(() => {
    detectLocation();
  }, []);

  const detectLocation = async () => {
    setLoading(true);
    setError("");
    try {
      if (!navigator.geolocation) throw new Error("Geolocation not supported");
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const { latitude, longitude } = pos.coords;
          setAutoDetected(true);
          fetchDataByCoords(latitude, longitude);
        },
        () => {
          setError("Unable to detect location. Please enter your city manually.");
          setLoading(false);
        },
        { timeout: 8000 }
      );
    } catch (err) {
      console.error(err);
      setError("Failed to get your location. Please try again.");
      setLoading(false);
    }
  };

  const fetchDataByCoords = async (lat, lon) => {
    try {
      const { data } = await axios.get(`${API_BASE}/airquality`, {
        params: { lat, lon },
      });
      setAqiData(data);

      if (data.aqi > 200) {
        setSevere(true);
        toast.error("⚠️ Air quality is dangerously poor in your area!");
      } else {
        setSevere(false);
      }

      // Fetch nearby areas
      const nearby = await axios.get(`${API_BASE}/nearby`, {
        params: { lat, lon },
      });
      setNearbyAreas(nearby.data);
    } catch (err) {
      setError("Error fetching air quality data.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDataByCity = async (isRefresh = false) => {
    if (!location.trim()) {
      setError("Please enter a valid city before loading data.");
      return;
    }

    setError("");
    isRefresh ? setRefreshing(true) : setLoading(true);

    try {
      const { data } = await axios.get(`${API_BASE}/airquality`, {
        params: { city: location },
      });
      setAqiData(data);
      setNearbyAreas([]);

      if (data.aqi > 200) {
        setSevere(true);
        toast.error("⚠️ Extremely poor air quality in this region!");
      } else {
        setSevere(false);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to fetch data for the selected city.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getAQIStatus = (value) => {
    if (value <= 50) return "Good";
    if (value <= 100) return "Moderate";
    if (value <= 150) return "Unhealthy for Sensitive Groups";
    if (value <= 200) return "Unhealthy";
    if (value <= 300) return "Very Unhealthy";
    return "Hazardous";
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <ToastContainer position="top-center" />

      {/* HEADER */}
      <header className="w-full max-w-6xl mx-auto mt-6 px-4 flex flex-col md:flex-row items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Air Quality Insights</h1>
          <p className="text-sm text-gray-500">
            Powered by NASA TEMPO Data {autoDetected && "(auto-detected)"}
          </p>
        </div>

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
            />
          </div>

          <div className="flex items-center border border-gray-200 rounded-lg px-3 py-2 bg-white">
            <FiMapPin className="text-gray-500 text-lg mr-2" />
            <input
              type="text"
              placeholder="Enter city..."
              className="outline-none text-sm w-32 md:w-48"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>

          <button
            onClick={() => fetchDataByCity(false)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition"
            disabled={loading || refreshing}
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
            onClick={() => fetchDataByCity(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition"
            disabled={loading || refreshing}
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
        {error && (
          <div className="text-center flex flex-col items-center gap-4">
            <FiAlertCircle className="text-6xl text-red-500 animate-bounce" />
            <p className="text-lg font-medium text-red-600">{error}</p>
            <button
              onClick={detectLocation}
              className="mt-2 bg-blue-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-600"
            >
              Retry Detect Location
            </button>
          </div>
        )}

        {/* LOADING */}
        {loading && (
          <div className="text-center flex flex-col items-center gap-3">
            <FiLoader className="text-5xl text-blue-500 animate-spin" />
            <p className="text-lg font-medium">Fetching Air Quality Data...</p>
            <p className="text-sm text-gray-500">
              Please wait while we contact NASA TEMPO servers.
            </p>
          </div>
        )}

        {/* DEFAULT STATE */}
        {!loading && !aqiData && !error && (
          <div className="text-center flex flex-col items-center gap-3 text-gray-500">
            <FiCloud className="text-6xl text-blue-300 animate-pulse" />
            <p className="text-sm">
              Enter a city and click <strong>Load</strong> to view air quality.
            </p>
          </div>
        )}

        {/* DATA */}
        {aqiData && !loading && !error && (
          <div className="w-full flex flex-col gap-8">
            {/* AQI Summary */}
            <section className="bg-white rounded-2xl shadow-sm p-6 flex flex-col md:flex-row items-center justify-between gap-6">
              <div>
                <h2 className="text-lg font-semibold">{aqiData.city}</h2>
                <p className="text-gray-500 text-sm">
                  Last updated: {aqiData.timestamp}
                </p>
              </div>
              <div className="text-center">
                <p className="text-gray-500 text-sm">Current AQI</p>
                <h2
                  className={`text-5xl font-bold ${
                    aqiData.aqi <= 50
                      ? "text-green-600"
                      : aqiData.aqi <= 100
                      ? "text-yellow-600"
                      : aqiData.aqi <= 150
                      ? "text-orange-600"
                      : "text-red-600"
                  }`}
                >
                  {aqiData.aqi}
                </h2>
                <p className="text-sm text-gray-600">
                  {getAQIStatus(aqiData.aqi)}
                </p>
              </div>
            </section>

            {/* Recommendation */}
            <section
              className={`rounded-2xl shadow-sm p-6 text-center text-white ${
                aqiData.aqi <= 100 ? "bg-green-500" : "bg-red-500"
              }`}
            >
              {aqiData.aqi <= 100
                ? "✅ Safe for outdoor activities. Take a walk!"
                : "🚫 Air quality is poor. Avoid outdoor exposure."}
            </section>

            {/* 5-hour Graph */}
            <section className="bg-white rounded-2xl shadow-sm p-6">
              <h3 className="font-medium mb-4 text-gray-700">
                AQI Trend (past 5 hours)
              </h3>
              <div className="w-full h-40 flex items-end justify-between gap-2">
                {aqiData.recent.map((val, idx) => (
                  <div
                    key={idx}
                    className={`flex-1 rounded-t-lg ${
                      val > 100 ? "bg-red-400" : "bg-green-400"
                    }`}
                    style={{ height: `${(val / 200) * 100}%` }}
                  ></div>
                ))}
              </div>
            </section>

            {/* Nearby Areas */}
            {nearbyAreas.length > 0 && (
              <section>
                <h3 className="font-medium mb-4 text-gray-700">
                  Nearby Areas
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {nearbyAreas.map((area) => (
                    <div
                      key={area.name}
                      className={`p-4 rounded-xl shadow-sm text-center ${
                        area.safe ? "bg-green-100" : "bg-red-100"
                      }`}
                    >
                      <h4 className="font-medium text-gray-700">
                        {area.name}
                      </h4>
                      <p
                        className={`text-sm ${
                          area.safe ? "text-green-700" : "text-red-700"
                        }`}
                      >
                        {area.safe ? "Safe" : "Unsafe"}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </main>

      {/* FOOTER */}
      <footer className="w-full mt-auto py-4 bg-white border-t border-gray-200 text-center text-xs text-gray-400">
        © 2025 Air Quality Insights — NASA Space Apps Challenge
      </footer>
    </div>
  );
}

export default App;
