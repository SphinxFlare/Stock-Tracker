// src/App.js

import { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./Settings/AuthContext";
import Dashboard from "./Pages/Dashboard";
import UserStocks from "./Pages/UserStock";
import Login from "./Pages/Login";
import Register from "./Pages/Register";
import ProtectedRoute from "./Components/ProtectedRoute";
import Watchlist from "./Pages/Wachlist";
import Navbar from "./Components/Navbar";
import { requestNotificationPermission, listenForMessages } from "./Settings/FirebaseConfig";

function App() {
  useEffect(() => {
    const setupNotifications = async () => {
      const token = await requestNotificationPermission();
      if (token) {
        console.log("✅ FCM Token received:", token);
      }
    };

    setupNotifications();
    listenForMessages();
  }, []);

  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* No Navbar on these pages */}
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />

          {/* Navbar wraps protected pages only */}
          <Route
            path="/"
            element={
              <>
                <Navbar />
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              </>
            }
          />
          <Route
            path="/userstocks"
            element={
              <>
                <Navbar />
                <ProtectedRoute>
                  <UserStocks />
                </ProtectedRoute>
              </>
            }
          />
          <Route
            path="/watchlist"
            element={
              <>
                <Navbar />
                <ProtectedRoute>
                  <Watchlist />
                </ProtectedRoute>
              </>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
