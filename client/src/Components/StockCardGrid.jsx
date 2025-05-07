// src/Components/StockCardGrid.jsx


import React, { useState } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Collapse,
  Box,
} from "@mui/material";
import StockHistoryInlineChart from "./StockHistoryChart"; // same chart you already have

const StockCardGrid = ({ stocks }) => {
  const [expandedIndex, setExpandedIndex] = useState(null);

  return (
    <Grid container spacing={3}>
      {stocks.map((stock, index) => (
        <Grid item xs={12} sm={6} md={4} key={index}>
          <Card
            sx={{
              backgroundColor: "#a4bcda",
              color: "black",
              borderRadius: 3,
              boxShadow: 3,
            }}
          >
            <CardContent>
              <Typography variant="h6">
                <b>{stock.name}</b> ({stock.symbol})
              </Typography>

              <Typography>🧮 Quantity: {stock.quantity}</Typography>
              <Typography>💰 Buy: ${stock.purchase_price.toFixed(2)}</Typography>
              <Typography>📈 Current: ${stock.live_price.toFixed(2)}</Typography>

              <Typography
                sx={{
                  color: stock.profit_loss >= 0 ? "#1d9e03" : "#f04e30",
                  mt: 1,
                }}
              >
                {stock.profit_loss >= 0 ? "📈 Profit" : "📉 Loss"}: $
                {stock.profit_loss.toFixed(2)}
              </Typography>

              <Button
                sx={{ mt: 2 }}
                variant="outlined"
                color="primary"
                fullWidth
                onClick={() =>
                  setExpandedIndex(expandedIndex === index ? null : index)
                }
              >
                {expandedIndex === index ? "Hide History" : "View History"}
              </Button>

              {/* 🔽 Collapsible Chart Area */}
              <Collapse in={expandedIndex === index} timeout="auto" unmountOnExit>
                <Box sx={{ mt: 3 }}>
                   <StockHistoryInlineChart
                    stock={stock}
                    onClose={() => setExpandedIndex(null)}
                   />
                </Box>
          </Collapse>

            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default StockCardGrid;