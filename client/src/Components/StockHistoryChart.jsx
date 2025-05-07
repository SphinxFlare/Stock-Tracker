// src/Components/StockHistoryChart.jsx

import React, { useEffect, useState, useRef } from "react";
import {
  Box,
  Typography,
  CircularProgress,
  IconButton,
  TextField,
  Button,
  Dialog, 
  DialogContent,  
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";
import api from "../Services/API";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  zoomPlugin
);

const StockHistoryInlineChart = ({ stock, onClose }) => {
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
      const res = await api.get(`/userstocks/stocks/${stock.symbol}/history`, {
        params: { start_date: startDate, end_date: endDate },
      });
      setHistory(res.data);
    } catch (err) {
      console.error("Error fetching history:", err);
    } finally {
      setLoading(false);
    }
  };

  const createGradient = (ctx) => {
    let gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(0, 201, 167, 0.4)"); // mint green top
    gradient.addColorStop(1, "rgba(0, 201, 167, 0)");   // fade to transparent
    return gradient;
  };
  

  const chartData = () => {
    if (!history.length) return {};
    const ctx = chartRef.current?.ctx;
    return {
      labels: history.map((h) =>
        new Date(h.timestamp).toLocaleDateString("en-US", {
          day: "numeric",
          month: "short",
        })
      ),
      datasets: [
        {
          label: "Price",
          data: history.map((h) => h.live_price),
          borderColor: "#00C9A7", // bright mint line
          backgroundColor: ctx ? createGradient(ctx) : "rgba(0,201,167,0.2)",
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: { top: 20, bottom: 20, left: 10, right: 10 },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (tooltipItem) => `$${tooltipItem.raw.toFixed(2)}`,
        },
      },
      legend: { display: false },
      zoom: {
        pan: { enabled: true, mode: "x" },
        zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: "x" },
      },
    },
    scales: {
      x: {
        ticks: { color: "#666" },
        grid: { color: "#eee" },
      },
      y: {
        ticks: {
          color: "#666",
          callback: (val) => `$${val}`,
        },
        grid: { color: "#eee" },
      },
    },
  };
  

  return (
    <Dialog
      open={true}
      onClose={onClose}
      fullWidth
      maxWidth="md"
      PaperProps={{
          sx: {
          backdropFilter: "blur(6px)",
          borderRadius: 3,
         },
       }}
    >

  <DialogContent sx={{ p: 4, position: "relative", bgcolor: "#fff" }}>
    <IconButton
      onClick={onClose}
      sx={{ position: "absolute", top: 16, right: 16 }}
    >
      <CloseIcon />
    </IconButton>

    <Typography variant="h6" sx={{ mb: 3 }}>
      📊 {stock.name} ({stock.symbol}) History
    </Typography>

    {/* Date Filter */}
    <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
      <TextField
        label="Start Date"
        type="date"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="End Date"
        type="date"
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
        InputLabelProps={{ shrink: true }}
      />
      <Button variant="contained" onClick={fetchStockHistory}>
        Apply
      </Button>
    </Box>

    {/* Chart */}
    {loading ? (
      <CircularProgress />
    ) : history.length > 0 ? (
      <Box sx={{ width: "100%", height: 400,  backgroundColor: "#fefefe", 
        borderRadius: 2, 
        p: 2  }}>
        <Line ref={chartRef} data={chartData()} options={chartOptions} />
      </Box>
    ) : (
      <Typography color="error">No data found in this range.</Typography>
    )}
  </DialogContent>
</Dialog>

  );
};

export default StockHistoryInlineChart;