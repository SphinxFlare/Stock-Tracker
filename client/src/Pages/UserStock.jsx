// src/Pages/UserStock.jsx


import React, { useState, useEffect } from "react";
import api from "../Services/API";
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  IconButton,
  Autocomplete,
  Grid,
  Fab,
} from "@mui/material";
import { Add, Edit, Delete, AttachMoney, CalendarToday, ShowChart } from "@mui/icons-material";
import { motion } from "framer-motion";
import SnackbarAlert from "../Components/SnackBar";
import debounce from "lodash.debounce";

const UserStocks = () => {
  const [stocks, setStocks] = useState([]);
  const [open, setOpen] = useState(false);
  const [editStock, setEditStock] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [formData, setFormData] = useState({
    symbol: "",
    name: "",
    purchase_price: "",
    quantity: "",
    purchase_date: "",
    notes: "",
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });

  useEffect(() => {
    fetchStocks();
  }, []);

  const fetchStocks = async () => {
    try {
      const response = await api.get("/userstocks/get");
      setStocks(response.data);
    } catch (error) {
      setSnackbar({ open: true, message: "Error fetching stocks!", severity: "error" });
    }
  };

  const fetchCompanySuggestions = debounce(async (query) => {
    if (!query) return;
    try {
      const response = await api.get(`/stocks/stocks/search/?query=${query}`);
      setSearchResults(response.data);
    } catch (error) {
      console.error("Error fetching companies:", error);
    }
  }, 300);

  const handleOpen = (stock = null) => {
    setEditStock(stock);
    setFormData(stock || { symbol: "", name: "", purchase_price: "", quantity: "", purchase_date: "", notes: "" });
    setOpen(true);
  };

  const handleClose = () => setOpen(false);

  const handleChange = (e) => {
    let { name, value } = e.target;
    if (name === "purchase_price" || name === "quantity") value = value ? Number(value) : "";
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async () => {
    try {
      if (editStock) {
        await api.put(`/userstocks/edit/${editStock.id}`, formData);
        setSnackbar({ open: true, message: "Stock updated successfully!", severity: "success" });
      } else {
        await api.post("/userstocks/add", formData);
        setSnackbar({ open: true, message: "Stock added successfully!", severity: "success" });
      }
      fetchStocks();
      handleClose();
    } catch (error) {
      setSnackbar({ open: true, message: "Error saving Stock!", severity: "error" });
    }
  };

  const handleDelete = async (stockId) => {
    if (window.confirm("Are you sure you want to delete this stock?")) {
      try {
        await api.delete(`/userstocks/delete/${stockId}`);
        setSnackbar({ open: true, message: "Stock deleted successfully!", severity: "success" });
        fetchStocks();
      } catch (error) {
        setSnackbar({ open: true, message: "Error deleting Stock!", severity: "error" });
      }
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: "bold", textAlign: "center", color: "#1976D2" }}>
        📊 My Stocks
      </Typography>

      {/* Floating Add Button */}
      <Fab
        color="primary"
        aria-label="add"
        onClick={() => handleOpen()}
        sx={{ position: "fixed", bottom: 20, right: 20 }}
      >
        <Add />
      </Fab>

      {/* Stock Cards */}
      <Grid container spacing={3}>
        {stocks.length > 0 ? (
          stocks.map((stock) => (
            <Grid item xs={12} sm={6} md={4} key={stock.id}>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Card
                  sx={{
                    borderRadius: "15px",
                    background: "linear-gradient(135deg, #232526, #414345)",
                    color: "white",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
                    overflow: "hidden",
                    position: "relative",
                  }}
                >
                  {/* Card Content */}
                  <CardContent>
                    <Typography
                      variant="h6"
                      sx={{ display: "flex", alignItems: "center", fontWeight: "bold" }}
                    >
                      <ShowChart sx={{ color: "#00c853", mr: 1 }} /> {stock.name} ({stock.symbol})
                    </Typography>

                    <Typography variant="body1" sx={{ display: "flex", alignItems: "center", fontSize: "1rem" }}>
                      <AttachMoney sx={{ color: "#ffeb3b", mr: 1 }} />
                      <span style={{ fontWeight: "bold", fontSize: "1.2rem" }}>
                        ${stock.purchase_price}
                      </span>
                    </Typography>

                    <Typography variant="body2" sx={{ color: "#b0bec5", mt: 1 }}>
                      🏷 Quantity: <span style={{ fontWeight: "bold", color: "#ffffff" }}>{stock.quantity}</span>
                    </Typography>

                    <Typography variant="body2" sx={{ display: "flex", alignItems: "center", color: "#b0bec5", mt: 1 }}>
                      <CalendarToday sx={{ color: "#03a9f4", mr: 1 }} />{" "}
                      {new Date(stock.purchase_date).toLocaleDateString()}
                    </Typography>
                  </CardContent>

                  <CardActions
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      borderTop: "1px solid rgba(255, 255, 255, 0.2)",
                      padding: "8px 16px",
                      background: "rgba(255, 255, 255, 0.05)",
                    }}
                  >
                    <IconButton color="info" onClick={() => handleOpen(stock)}>
                      <Edit sx={{ color: "#4caf50" }} />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDelete(stock.id)}>
                      <Delete sx={{ color: "#f44336" }} />
                    </IconButton>
                  </CardActions>
                </Card>
              </motion.div>
            </Grid>
          ))
        ) : (
          <Typography>No stocks found.</Typography>
        )}
      </Grid>

      {/* Add/Edit Stock Dialog with Animation */}
      <Dialog
  open={open}
  onClose={handleClose}
  PaperProps={{
    sx: {
      borderRadius: "12px",
      background: "linear-gradient(135deg, #232526, #414345)",
      color: "white",
      padding: "20px",
      boxShadow: "0 8px 16px rgba(0,0,0,0.3)",
      width: "400px",
    },
  }}
>
  <motion.div
    initial={{ opacity: 0, scale: 0.85 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3, ease: "easeOut" }}
  >
    {/* Title Section */}
    <DialogTitle
      sx={{
        textAlign: "center",
        fontWeight: "bold",
        fontSize: "1.5rem",
        color: "#ffeb3b",
      }}
    >
      {editStock ? "✏️ Edit Stock" : "➕ Add Stock"}
    </DialogTitle>

    {/* Form Content */}
    <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
      <Autocomplete
        options={searchResults}
        getOptionLabel={(option) => option.name}
        onInputChange={(e, newValue) => fetchCompanySuggestions(newValue)}
        onChange={(e, newValue) =>
          newValue &&
          setFormData({ ...formData, name: newValue.name, symbol: newValue.symbol })
        }
        renderInput={(params) => (
          <TextField
            {...params}
            label="🔍 Search Company"
            fullWidth
            variant="outlined"
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: "10px",
                backgroundColor: "rgba(255, 255, 255, 0.1)",
                "& fieldset": { borderColor: "rgba(255, 255, 255, 0.3)" },
                "&:hover fieldset": { borderColor: "white" },
                "&.Mui-focused fieldset": { borderColor: "#ffeb3b" },
              },
              "& .MuiInputBase-input": { color: "white" },
              "& .MuiInputLabel-root": { color: "rgba(255, 255, 255, 0.6)" },
            }}
          />
        )}
      />

      <TextField
        label="🏷 Symbol"
        name="symbol"
        value={formData.symbol}
        fullWidth
        disabled
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            "& fieldset": { borderColor: "rgba(255, 255, 255, 0.3)" },
            "&:hover fieldset": { borderColor: "white" },
          },
          "& .MuiInputBase-input": { color: "white" },
          "& .MuiInputLabel-root": { color: "rgba(255, 255, 255, 0.6)" },
        }}
      />

      <TextField
        label="💰 Purchase Price"
        name="purchase_price"
        type="number"
        value={formData.purchase_price}
        onChange={handleChange}
        fullWidth
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            "& fieldset": { borderColor: "rgba(255, 255, 255, 0.3)" },
            "&:hover fieldset": { borderColor: "white" },
          },
          "& .MuiInputBase-input": { color: "white" },
          "& .MuiInputLabel-root": { color: "rgba(255, 255, 255, 0.6)" },
        }}
      />

      <TextField
        label="📦 Quantity"
        name="quantity"
        type="number"
        value={formData.quantity}
        onChange={handleChange}
        fullWidth
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            "& fieldset": { borderColor: "rgba(255, 255, 255, 0.3)" },
            "&:hover fieldset": { borderColor: "white" },
          },
          "& .MuiInputBase-input": { color: "white" },
          "& .MuiInputLabel-root": { color: "rgba(255, 255, 255, 0.6)" },
        }}
      />
    </DialogContent>

    {/* Buttons */}
    <DialogActions sx={{ justifyContent: "center", gap: 2, mt: 2 }}>
      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.9 }}>
        <Button onClick={handleClose} variant="contained" color="secondary" sx={{ borderRadius: "20px" }}>
          ❌ Cancel
        </Button>
      </motion.div>

      <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
        <Button
          onClick={handleSubmit}
          variant="contained"
          sx={{
            background: "#ffeb3b",
            color: "black",
            fontWeight: "bold",
            borderRadius: "20px",
            "&:hover": { background: "#fdd835" },
          }}
        >
          {editStock ? "💾 Update" : "✅ Add"}
        </Button>
      </motion.div>
    </DialogActions>
  </motion.div>
</Dialog>


      <SnackbarAlert open={snackbar.open} handleClose={() => setSnackbar({ ...snackbar, open: false })} message={snackbar.message} severity={snackbar.severity} />
    </Container>
  );
};

export default UserStocks;