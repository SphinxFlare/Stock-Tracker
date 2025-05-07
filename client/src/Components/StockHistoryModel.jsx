// src/Components/StockHistoryModel.jsx

import React, { useEffect, useState, useRef } from "react";
import {
  Modal, Box, Typography, CircularProgress, Button, TextField
} from "@mui/material";
import { Line, Chart } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";
import api from "../Services/API";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, zoomPlugin);

const StockHistoryModal = ({ open, handleClose, stock }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const chartRef = useRef(null);

  useEffect(() => {
    if (stock) fetchStockHistory();
  }, [stock, startDate, endDate]);


  const fetchStockHistory = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/userstocks/stocks/${stock.symbol}/history`, {
        params: { start_date: startDate, end_date: endDate },
      });
      setHistory(response.data);
    } catch (error) {
      console.error("Error fetching stock history:", error);
    } finally {
      setLoading(false);
    }
  };

  // **Create Gradient for Chart Line**
  const createGradient = (ctx) => {
    let gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, "rgba(75,192,192,1)");  // Light teal
    gradient.addColorStop(1, "rgba(75,192,192,0.1)");  // Fades out
    return gradient;
  };

  // **Chart Data & Styling**
  const formatChartData = () => {
    if (!history.length) return {};
    const ctx = chartRef.current?.ctx;
    return {
      labels: history.map((data) => new Date(data.timestamp).toLocaleDateString()),
      datasets: [
        {
          label: "Stock Price",
          data: history.map((data) => data.live_price),
          borderColor: "#4BC0C0",
          backgroundColor: ctx ? createGradient(ctx) : "rgba(75,192,192,0.4)",
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: "#fff",
          borderWidth: 2,
          tension: 0.4, // Smooth curve
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }, // Hide legend
      tooltip: {
        enabled: true,
        backgroundColor: "#222",
        bodyColor: "#fff",
        bodyFont: { weight: "bold" },
        callbacks: {
          label: (tooltipItem) => `💲 ${tooltipItem.raw.toFixed(2)}`,
        },
      },
      zoom: {
        pan: { enabled: true, mode: "x" },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: "x",
        },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: "#ddd" } },
      y: { grid: { color: "#444" }, ticks: { color: "#ddd", callback: (val) => `$${val}` } },
    },
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <Box sx={{ width: "80%", margin: "auto", mt: 5, bgcolor: "#1e1e1e", p: 4, borderRadius: 2, color: "#fff" }}>
        <Typography variant="h5" sx={{ mb: 2 }}>📊 Stock History - {stock?.name}</Typography>

        {/* Date Picker */}
        <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
          <TextField label="Start Date" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} InputLabelProps={{ shrink: true }} sx={{ bgcolor: "#333", color: "#fff", borderRadius: 1 }} />
          <TextField label="End Date" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} InputLabelProps={{ shrink: true }} sx={{ bgcolor: "#333", color: "#fff", borderRadius: 1 }} />
          <Button variant="contained" sx={{ bgcolor: "#4BC0C0" }} onClick={fetchStockHistory}>Apply</Button>
        </Box>

        {/* Loading State */}
        {loading ? <CircularProgress /> : history.length > 0 ? (
          <>
            {/* 📈 Enhanced Line Chart */}
            <Box sx={{ height: 300, mb: 2 }}>
              <Line ref={chartRef} data={formatChartData()} options={chartOptions} />
            </Box>

            {/* 📌 Quick Stats */}
            <Box sx={{ p: 2, bgcolor: "#292929", borderRadius: 2 }}>
              <Typography variant="h6">📌 Quick Stats</Typography>
              <Typography>📈 Highest: 💲{Math.max(...history.map((h) => h.live_price)).toFixed(2)}</Typography>
              <Typography>📉 Lowest: 💲{Math.min(...history.map((h) => h.live_price)).toFixed(2)}</Typography>
              <Typography>📊 Average: 💲{(history.reduce((sum, h) => sum + h.live_price, 0) / history.length).toFixed(2)}</Typography>
            </Box>
          </>
        ) : (
          <Typography color="error">❌ No data found for this period.</Typography>
        )}

        {/* Close Button */}
        <Button variant="contained" sx={{ mt: 3, bgcolor: "#f04e30" }} onClick={handleClose}>
          Close
        </Button>
      </Box>
    </Modal>
  );
};

export default StockHistoryModal;