// src/pages/Watchlist.jsx

// import React, { useEffect, useState } from "react";
// import { Container, Typography, CircularProgress } from "@mui/material";
// import { fetchWatchlist } from "../Services/API";
// import StockCard from "../Components/StockCard";
// import AddStock from "../Components/AddStock";

// const Watchlist = () => {
//     const [watchlist, setWatchlist] = useState([]);
//     const [loading, setLoading] = useState(true);

//     useEffect(() => {
//         loadWatchlist();
//     }, []);

//     const loadWatchlist = async () => {
//         setLoading(true);
//         const data = await fetchWatchlist();
//         if (data) setWatchlist(data.stock_details);
//         setLoading(false);
//     };

//     const handleStockAdded = async () => {
//         await loadWatchlist();
//     };

//     const handleStockRemoved = async (symbol) => {
//         setWatchlist((prev) => prev.filter((stock) => stock.symbol !== symbol));
//     };

//     return (
//         <Container maxWidth="sm">
//             <Typography variant="h4" align="center" marginTop={3} marginBottom={2}>
//                 My Watchlist
//             </Typography>
//             <AddStock onStockAdded={handleStockAdded} />
            
//             {loading ? (
//                 <CircularProgress />
//             ) : watchlist.length > 0 ? (
//                 watchlist.map((stock) => (
//                     <StockCard key={stock.symbol} stock={stock} onRemove={handleStockRemoved} />
//                 ))
//             ) : (
//                 <Typography align="center">Your watchlist is empty.</Typography>
//             )}
//         </Container>
//     );
// };

// export default Watchlist;

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  CircularProgress,
  Snackbar,
  Box,
  Grid,
  Paper,
  Grow,
  Fade
} from "@mui/material";
import MuiAlert from "@mui/material/Alert";
import DeleteIcon from "@mui/icons-material/Delete";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import { getWatchlist, removeStockFromWatchlist } from "../Services/API";

// 🎨 Custom styles
const cardStyles = {
  p: 1,
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  borderRadius: 3,
  boxShadow: 6,
  transition: "0.3s",
  background: "rgba(255, 255, 255, 0.1)", // Glassmorphism effect
  backdropFilter: "blur(10px)", // Glass effect
  "&:hover": { boxShadow: 12, transform: "scale(1.02)" },
};

const Watchlist = () => {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      const data = await getWatchlist();
      const watchlistArray = data?.watchlist?.watchlist || data?.watchlist || [];
      console.log("📜 Updated Watchlist Data:", watchlistArray);
      setWatchlist(watchlistArray);
    } catch (error) {
      console.error("❌ Error fetching watchlist:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveStock = async (stockSymbol) => {
    try {
      console.log("🗑️ Removing stock:", stockSymbol);
      const response = await removeStockFromWatchlist(stockSymbol);
      console.log("✅ API Response:", response);
      setSnackbar({ open: true, message: `🗑️ Stock removed!`, severity: "info" });
      
      // ⚡ Smooth removal effect
      setWatchlist((prev) => prev.filter((stock) => stock.symbol !== stockSymbol));
    } catch (error) {
      console.error("❌ Error:", error);
      setSnackbar({ open: true, message: `❌ ${error}`, severity: "error" });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold", textAlign: "center", color: "#1976D2" }}>
        📊 My Watchlist
      </Typography>

      {/* Show loading spinner */}
      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <CircularProgress size={60} />
        </Box>
      ) : watchlist.length > 0 ? (
        <Grid container spacing={3}>
          {watchlist.map((stock, index) => (
            <Grow in={true} timeout={500 * (index + 1)} key={stock.symbol}>
              <Grid item xs={12} sm={6} md={4}>
                <Card sx={cardStyles}>
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                      {stock.symbol} - {stock.company_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      💰 Price: <b>${stock.current_price ? stock.current_price.toFixed(2) : "N/A"}</b>
                    </Typography>

                    {/* 📈 Dynamic price change animation */}
                    <Typography
                      variant="body2"
                      sx={{
                        color: stock.percent_change
                          ? stock.percent_change >= 0
                            ? "green"
                            : "red"
                          : "gray",
                        fontWeight: "bold",
                        transition: "0.3s ease-in-out",
                      }}
                    >
                      {stock.percent_change
                        ? (stock.percent_change >= 0 ? "📈" : "📉") +
                          ` ${stock.percent_change.toFixed(1)}%`
                        : "N/A"}
                    </Typography>
                  </CardContent>

                  {/* 🗑️ Delete button with animation */}
                  <IconButton
                    onClick={() => handleRemoveStock(stock.symbol)}
                    color="error"
                    sx={{ transition: "0.3s", "&:hover": { transform: "scale(1.2)" } }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Card>
              </Grid>
            </Grow>
          ))}
        </Grid>
      ) : (
        <Fade in={true} timeout={1000}>
          <Paper
            elevation={6}
            sx={{
              textAlign: "center",
              mt: 5,
              p: 4,
              borderRadius: 3,
              backgroundColor: "#f5f5f5",
            }}
          >
            <AddCircleOutlineIcon sx={{ fontSize: 60, color: "#1976D2" }} />
            <Typography variant="h6" sx={{ mt: 2, color: "#666" }}>
              🚀 No stocks in your watchlist. Start adding some!
            </Typography>
          </Paper>
        </Fade>
      )}

      {/* ✅ Snackbar Notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <MuiAlert severity={snackbar.severity} sx={{ fontSize: "16px", fontWeight: "bold" }}>
          {snackbar.message}
        </MuiAlert>
      </Snackbar>
    </Box>
  );
};

export default Watchlist;
