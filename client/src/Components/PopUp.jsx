// src/Components/PopUp.jsx

import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  List,
  ListItem,
  ListItemText,
  IconButton,
  CircularProgress,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

const SearchPopup = ({ open, onClose, onSearch, searchResults, isLoading, onAddToWatchlist }) => {
  const [query, setQuery] = useState("");

  // Handle user typing in the search field
  const handleInputChange = (event) => {
    setQuery(event.target.value);
    onSearch(event.target.value); // Call the search function from parent
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Search Stocks</DialogTitle>
      <DialogContent>
        {/* Search Input Field */}
        <TextField
          autoFocus
          fullWidth
          margin="dense"
          label="Search for a stock..."
          variant="outlined"
          value={query}
          onChange={handleInputChange}
        />

        {/* Loading State */}
        {isLoading && <CircularProgress sx={{ mt: 2 }} />}

        {/* Search Results */}
        <List>
          {searchResults.length > 0 ? (
            searchResults.map((stock) => (
              <ListItem key={stock.symbol} divider>
                <ListItemText primary={stock.name} secondary={stock.symbol} />
                <IconButton onClick={() => onAddToWatchlist(stock.symbol)}> 
                  <AddIcon color="primary" />
                </IconButton>
              </ListItem>
            ))
          ) : (
            !isLoading && <ListItem>No results found</ListItem>
          )}
        </List>
      </DialogContent>
    </Dialog>
  );
};

export default SearchPopup;

