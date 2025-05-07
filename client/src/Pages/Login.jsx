// src/Pages/Login.jsx

import React, { useState, useContext } from "react";
import {
  Container, TextField, Button, Typography, Box, Paper,
  InputAdornment, IconButton
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "../Settings/AuthContext";
import SnackbarAlert from "../Components/SnackBar";


const Login = () => {
  const { login } = useContext(AuthContext);  // ✅ Use login function from context
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });


  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      setSnackbar({ open: true, message: "Login Successful!", severity: "success" });
      setTimeout(() => navigate("/"), 1500); // Redirect after a slight delay
    } catch (error) {
      setSnackbar({ open: true, message: "Invalid credentials!", severity: "error" });
    }
  };

  return (
    <Container maxWidth="xs">
      <Paper elevation={6} sx={{ padding: 4, mt: 8, borderRadius: 3, textAlign: "center" }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          Welcome Back
        </Typography>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Log in to continue
        </Typography>

        <Box component="form" mt={2} onSubmit={handleLogin}>
          <TextField fullWidth margin="normal" label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <TextField
            fullWidth margin="normal" label="Password"
            type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            Login
          </Button>
          <Typography variant="body2" sx={{ mt: 2 }}>
            Don't have an account?{" "}
            <Link to="/register" style={{ textDecoration: "none", color: "#1976d2" }}>Sign up</Link>
          </Typography>
        </Box>
      </Paper>
         {/* ✅ Snackbar for Notifications */}
         <SnackbarAlert open={snackbar.open} handleClose={() => setSnackbar({ ...snackbar, open: false })} message={snackbar.message} severity={snackbar.severity} />
    
    </Container>
  );
};

export default Login;