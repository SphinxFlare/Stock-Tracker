import React from "react";
import { Snackbar, Alert } from "@mui/material";

const SnackbarAlert = ({ open, handleClose, message, severity }) => {
  return (
    <Snackbar open={open} autoHideDuration={3000} onClose={handleClose} anchorOrigin={{ vertical: "top", horizontal: "right" }}>
      <Alert onClose={handleClose} severity={severity} sx={{ width: "100%" }}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default SnackbarAlert;
