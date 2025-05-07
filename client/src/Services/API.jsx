// src/Services/API.jsx

import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"; 

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});


// ✅ Ensure token is always included
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


// ✅ Fixed: Use watchlist_id in the URL
export const removeStockFromWatchlist = async (stockSymbol) => {
  try {
      const response = await api.delete(`/watchlist/remove/${stockSymbol}`);
      return response.data;
  } catch (error) {
      console.error("❌ Error removing stock:", error);
      return null;
  }
};



// ✅ Fetch the watchlist
export const getWatchlist = async () => {
  try {
      const response = await api.get("/watchlist/");  // ✅ Corrected endpoint
      console.log("📡 API Response:", response.data);
      return response.data.watchlist || [];
  } catch (error) {
      console.error("❌ Error fetching watchlist:", error.response?.data || error.message);
      return [];  // ✅ Return empty array instead of null
  }
};

// ✅ Add a stock to the watchlist
export const addStockToWatchlist = async (symbol) => {
  try {
    console.log("📡 Sending API Request: Adding", symbol, "to watchlist...");

    const response = await api.post("/watchlist/add", { stock_symbol: symbol });  // ✅ Corrected request key

    console.log("✅ API Success:", response.data);
    
    return response.data;
  } catch (error) {
    console.error("❌ API Error:", error.response?.data || error.message);
    throw error.response?.data?.detail || "Error adding stock.";
  }
};




export default api;



