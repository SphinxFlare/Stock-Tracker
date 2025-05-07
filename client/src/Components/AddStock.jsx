// src/components/AddStock.jsx

import React, { useState } from "react";
import { TextField, Button, Box } from "@mui/material";
import { addStockToWatchlist } from "../Services/API";

const AddStock = ({ onStockAdded }) => {
    const [symbol, setSymbol] = useState("");

    const handleAddStock = async () => {
        if (symbol.trim() === "") return;
        await addStockToWatchlist(symbol.toUpperCase());
        onStockAdded(symbol.toUpperCase());
        setSymbol(""); // Clear input
    };

    return (
        <Box display="flex" gap={2} marginBottom={2}>
            <TextField
                label="Enter Stock Symbol"
                variant="outlined"
                size="small"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
            />
            <Button variant="contained" color="primary" onClick={handleAddStock}>
                Add Stock
            </Button>
        </Box>
    );
};

export default AddStock;
