// src/Pages/Dashboard.jsx

import React, { useContext, useState, useEffect } from "react";
import {
  Container,
  Typography,
  AppBar,
  Toolbar,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  Box,
  CircularProgress,
  Button,
  Collapse
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import AuthContext from "../Settings/AuthContext";
import api from "../Services/API";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import StockHistoryModal from "../Components/StockHistoryModel";
import StockCardGrid from "../Components/StockCardGrid";


// 🎨 Define styles
const profitStyle = { color: "green", fontWeight: "bold" };
const lossStyle = { color: "red", fontWeight: "bold" };

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  // 📊 State Management
  const [portfolio, setPortfolio] = useState(null);
  const [stocks, setStocks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // const [selectedStock, setSelectedStock] = useState(null);
  // const [historyModalOpen, setHistoryModalOpen] = useState(false);


const [expandedRowIndex, setExpandedRowIndex] = useState(null);



  // 🔥 Fetch Portfolio & Stock Data
  useEffect(() => {
    async function fetchData() {
      try {

        // 🔄 Step 1: Update user's stocks first
        // console.log("🚀 Updating stocks...");
        // await api.post("/userstocks/update-stocks");

        // Fetch performance data
        const performanceRes = await api.get("/userstocks/portfolio/performance");
        console.log("📡 Performance API Response:", performanceRes.data);

        // Fetch portfolio data
        const portfolioRes = await api.get("/auth/portfolio");
        console.log("📡 Portfolio API Response:", portfolioRes.data);

        // Set state
        setPortfolio({
          totalInvestment: performanceRes.data.total_investment,
          currentValue: performanceRes.data.current_value,
          totalProfitLoss: performanceRes.data.total_profit_loss,
          overallChangePercentage: performanceRes.data.overall_change_percentage,
        });
        console.log("✅ Updated Portfolio State:", portfolio);
        setStocks(performanceRes.data.stock_analysis);
      } catch (error) {
        console.error("❌ Error fetching data:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, []);

  

  const SummaryCard = ({ title, value, icon, color }) => (
    <Card sx={{ 
      bgcolor: color, 
      color: "white", 
      flex: 1, 
      textAlign: "center", 
      p: 1,
      transition: "transform 0.3s",
      "&:hover": { transform: "scale(1.05)" } 
    }}>
    
      <CardContent>
        {icon}
        <Typography variant="h6" sx={{ mt: 1, fontWeight: "bold" }}>
          {title}
        </Typography>
        <Typography variant="h5" sx={{ fontWeight: "bold" }}>
          ${value?.toFixed(2)}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg">
      {/* 🔹 Navbar */}
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Stock Dashboard
          </Typography>
          <Avatar sx={{ bgcolor: "#2196F3" }} onClick={() => navigate("/profile")}>
            {user.name[0]}
          </Avatar>
        </Toolbar>
      </AppBar>

     {/* 🔹 Portfolio Overview */}
<Box sx={{ textAlign: "center", mb: 4 }}>
  <Typography variant="h5">Welcome, {user?.name} 👋</Typography>

  {portfolio ? (
    <Typography variant="h6">
      {portfolio.overallChangePercentage > 50
        ? "🚀 Amazing growth! Your portfolio is booming! 🎉"
        : portfolio.overallChangePercentage > 20
        ? "📈 Nice! Your investments are growing well!"
        : portfolio.overallChangePercentage > 0
        ? "🟢 Steady growth, keep going!"
        : "🔴 Your portfolio is in loss, consider rebalancing."
      }
    </Typography>
  ) : (
    <Typography variant="h6" color="gray">
      🔄 Loading portfolio insights...
    </Typography>
  )}

  {isLoading ? (
    <CircularProgress sx={{ mt: 3 }} />
  ) : portfolio ? (
    <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", p: 2 }}>
      <SummaryCard
        title="💰 Total Investment"
        value={portfolio.totalInvestment}
        icon={<AttachMoneyIcon sx={{ fontSize: 40 }} />}
        color="#1976D2"
      />
      <SummaryCard
        title="📊 Current Value"
        value={portfolio.currentValue}
        icon={<AccountBalanceWalletIcon sx={{ fontSize: 40 }} />}
        color="#388E3C"
      />
      <SummaryCard
        title={portfolio.totalProfitLoss >= 0 ? "Total Profit 📈" : "Total Loss 📉"}
        value={portfolio.totalProfitLoss}
        icon={
          portfolio.totalProfitLoss >= 0 ? (
            <TrendingUpIcon sx={{ fontSize: 40 }} />
          ) : (
            <TrendingDownIcon sx={{ fontSize: 40 }} />
          )
        }
        color={portfolio.totalProfitLoss >= 0 ? "#43A047" : "#D32F2F"}
      />
    </Box>
  ) : (
    <Typography variant="h6" color="error">
      ❌ Failed to Load Portfolio Data
    </Typography>
  )}
</Box>



      {/* 🔹 Stock Holdings Breakdown */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6">📊 Your Stock Holdings</Typography>

              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Stock</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Buy Price</TableCell>
                      <TableCell>Current Price</TableCell>
                      <TableCell>Investment</TableCell>
                      <TableCell>Current Value</TableCell>
                      <TableCell>Profit/Loss</TableCell>
                      <TableCell>% Change</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {isLoading ? (
                      <TableRow>
                        <TableCell colSpan={8} align="center">
                          <CircularProgress />
                        </TableCell>
                      </TableRow>
                    ) : (
                      stocks.map((stock, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <b>{stock.name}</b> ({stock.symbol})
                          </TableCell>
                          <TableCell>{stock.quantity}</TableCell>
                          <TableCell>${stock.purchase_price.toFixed(2)}</TableCell>
                          <TableCell>${stock.live_price.toFixed(2)}</TableCell>
                          <TableCell>${stock.total_investment.toFixed(2)}</TableCell>
                          <TableCell>${stock.current_value.toFixed(2)}</TableCell>
                          <TableCell
                            sx={stock.profit_loss >= 0 ? profitStyle : lossStyle}
                          >
                            {stock.profit_loss >= 0 ? "📈" : "📉"} ${stock.profit_loss.toFixed(2)}
                          </TableCell>
                          <TableCell
                            sx={stock.percentage_change >= 0 ? profitStyle : lossStyle}
                          >
                            {stock.percentage_change.toFixed(2)}%
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

     {/* 🌟 Section Separator */}
<Box sx={{ textAlign: "center", mt: 6, mb: 3 }}>
  <Typography 
    variant="h4" 
    sx={{ 
      fontWeight: "bold", 
      color: "#1976D2", 
      mb: 1,
      letterSpacing: 1
    }}
  >
    📈 Visual Breakdown
  </Typography>
  <Typography variant="subtitle1" color="textSecondary">
    A card-based glance at your stocks — fast, clean, and focused.
  </Typography>
</Box>

     
      {/* 🔥 Swapped out table with card grid */}
      <StockCardGrid stocks={stocks} />



    </Container>
  );
};

export default Dashboard;
