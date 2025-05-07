// src/Settings/AuthContext.js

import { createContext, useState, useEffect } from "react";
import api from "../Services/API";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    console.log("🔍 Checking token:", token);

    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      api.get("/auth/me")
        .then(response => {
          console.log("✅ User fetched successfully:", response.data);
          setUser(response.data);
          localStorage.setItem("user", JSON.stringify(response.data)); // 🔹 Save user data
        })
        .catch((error) => {
          console.error("❌ Failed to fetch user:", error);
          setUser(null);
          localStorage.removeItem("user"); // 🔹 Remove invalid user data
        })
        .finally(() => {
          console.log("🔄 Finished loading.");
          setLoading(false);
        });
    } else {
      console.log("🚫 No token found.");
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      console.log("🔐 Logging in...");
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      console.log("✅ Login time:", response.data.last_login)
      console.log("✅ Login successful! Token:", response.data.access_token);
      localStorage.setItem("token", response.data.access_token);
      api.defaults.headers.common["Authorization"] = `Bearer ${response.data.access_token}`;

      const userData = await api.get("/auth/me");
      console.log("✅ Fetched user after login:", userData.data);
      setUser(userData.data);
      localStorage.setItem("user", JSON.stringify(userData.data)); // 🔹 Store user info
    } catch (error) {
      console.error("❌ Login failed:", error);
      throw new Error("Invalid credentials");
    }
  };

  const logout = () => {
    console.log("🚪 Logging out...");
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;