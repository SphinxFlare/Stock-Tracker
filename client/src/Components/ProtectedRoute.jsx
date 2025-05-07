// src/components/ProtectedRoute.jsx

import { useContext } from "react";
import { Navigate } from "react-router-dom";
import AuthContext from "../Settings/AuthContext";

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);

  console.log("🔍 Checking ProtectedRoute:", { user, loading });

  if (loading) return <div>Loading...</div>;

  return user ? children : <Navigate to="/login" />;
};

export default ProtectedRoute;