import { useState } from "react";
import {
  FiMapPin,
  FiAlertTriangle,
  FiAlertCircle,
  FiLoader,
  FiCloud,
  FiRefreshCcw,
} from "react-icons/fi";

function App() {
  const [location, setLocation] = useState("");
  const [aqiData, setAqiData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [notification, setNotification] = useState("");

  // FAST API BACKEND URL
  const API_URL = `http://localhost:8000/api/airquality?city=${location}`;

  // Fetch data (for both load and refresh)
  const fetchData = async (isRefresh = false) => {
    try {
      if (!location.trim()) {
        setError("Please enter a valid city before loading data.");
        setAqiData(null);
        return;
      }

      setError("");
      setNotification("");
      setAqiData(null);
      isRefresh ? setRefreshing(true) : setLoading(true);

      // Simulate network latency for demo clarity
      await new Promise((res) => setTimeout(res, 1500));

      const response = await fetch(API_URL);
      if (!response.ok) throw new Error("Failed to fetch air quality data");

      const data = await response.json();
      setAqiData(data);

      if (data.aqi > 100) {
        setNotification("⚠️ Air quality is unhealthy. Avoid outdoor exposure.");
      }
    } catch (err) {
      console.error(err);
      setError(
        "Oh no! Something went wrong while fetching air quality data. Please try again."
      );
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
      {/* Header */}
      <header className="w-full max-w-6xl mx-auto mt-8 px-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Air Quality Insights</h1>
          <p className="text-sm text-gray-500">Powered by NASA TEMPO Data</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
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
            onClick={() => fetchData(false)}
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
            onClick={() => fetchData(true)}
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

      {/* Notification */}
      {notification && (
        <div className="w-full max-w-6xl mx-auto mt-6 px-4">
          <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-3 rounded-lg flex items-center gap-2">
            <FiAlertTriangle />
            <p className="text-sm">{notification}</p>
          </div>
        </div>
      )}

      {/* MAIN CONTENT */}
      <main className="flex-1 w-full max-w-6xl mx-auto px-4 py-8 flex items-center justify-center">
        {/* Error State */}
        {error && (
          <div className="text-center flex flex-col items-center gap-4">
            <FiAlertCircle className="text-6xl text-red-500 animate-bounce" />
            <p className="text-lg font-medium text-red-600">{error}</p>
            <p className="text-sm text-gray-500">
              Try checking your internet connection or backend API.
            </p>
          </div>
        )}

        {/* Loading / Refreshing State */}
        {(loading || refreshing) && (
          <div className="text-center flex flex-col items-center gap-4">
            <FiLoader className="text-5xl text-blue-500 animate-spin" />
            <p className="text-lg font-medium">
              {loading ? "Loading air quality data..." : "Refreshing data..."}
            </p>
            <p className="text-sm text-gray-500">
              Please wait while we contact NASA TEMPO servers.
            </p>
          </div>
        )}

        {/* Empty State */}
        {!aqiData && !loading && !refreshing && !error && (
          <div className="text-center flex flex-col items-center gap-3 text-gray-500">
            <FiCloud className="text-6xl text-blue-300 animate-pulse" />
            <p className="text-sm">
              Enter a city and click <strong>Load</strong> to view air quality.
            </p>
          </div>
        )}

        {/* Data Display */}
        {aqiData && !loading && !refreshing && !error && (
          <div className="w-full flex flex-col gap-8">
            {/* Summary */}
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

            {/* Pollutants */}
            <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {aqiData.pollutants.map((item) => (
                <div
                  key={item.name}
                  className="bg-white rounded-xl shadow-sm p-4 text-center"
                >
                  <p className="text-sm text-gray-500">{item.name}</p>
                  <p className="text-lg font-semibold">{item.value} µg/m³</p>
                </div>
              ))}
            </section>

            {/* Forecast */}
            <section className="bg-white rounded-2xl shadow-sm p-6">
              <h3 className="font-medium mb-4 text-gray-700">
                Forecast (next 24h)
              </h3>
              <div className="w-full h-40 flex items-end justify-between gap-2">
                {aqiData.forecast.map((val, idx) => (
                  <div
                    key={idx}
                    className={`flex-1 rounded-t-lg transition-all duration-300 ${
                      val > 100 ? "bg-red-400" : "bg-green-400"
                    }`}
                    style={{ height: `${(val / 200) * 100}%` }}
                  ></div>
                ))}
              </div>
            </section>

            {/* Health Advice */}
            <section className="bg-white rounded-2xl shadow-sm p-6">
              <h3 className="font-medium mb-2 text-gray-700">Health Advisory</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {aqiData.health_advice}
              </p>
            </section>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full mt-auto py-4 bg-white border-t border-gray-200 text-center text-xs text-gray-400">
        © 2025 Air Quality Insights — NASA Space Apps Challenge
      </footer>
    </div>
  );
}

export default App;
