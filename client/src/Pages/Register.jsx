// src/Pages/Register.jsx

import React, { useState, useContext } from "react";
import {
  Container, TextField, Button, Typography, Box, Paper,
  InputAdornment, IconButton
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "../Settings/AuthContext";

const Register = () => {
  const { register } = useContext(AuthContext);  // ✅ Use register function from context
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    try {
      await register(name, email, password);  // ✅ Call AuthContext register function
      navigate("/login");  // ✅ Redirect to login after successful registration
    } catch (error) {
      alert("Registration failed");
    }
  };

  return (
    <Container maxWidth="xs">
      <Paper elevation={6} sx={{ padding: 4, mt: 8, borderRadius: 3, textAlign: "center" }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          Create Account
        </Typography>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Sign up to get started
        </Typography>

        <Box component="form" mt={2} onSubmit={handleRegister}>
          <TextField fullWidth margin="normal" label="Full Name" value={name} onChange={(e) => setName(e.target.value)} />
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
          <TextField
            fullWidth margin="normal" label="Confirm Password"
            type={showConfirmPassword ? "text" : "password"} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            Register
          </Button>
          <Typography variant="body2" sx={{ mt: 2 }}>
            Already have an account?{" "}
            <Link to="/login" style={{ textDecoration: "none", color: "#1976d2" }}>Log in</Link>
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;