// src/Components/Navbar.jsx

import React, { useState } from "react";
import { Box, IconButton, Tooltip, Typography, Collapse } from "@mui/material";
import { styled } from "@mui/system";
import { Link } from "react-router-dom"; // For routing

// Icons 🎨
import AccountBalanceIcon from "@mui/icons-material/AccountBalance"; // Home
// import QueryStatsTwoToneIcon from "@mui/icons-material/QueryStatsTwoTone"; // Search
import TipsAndUpdatesTwoToneIcon from "@mui/icons-material/TipsAndUpdatesTwoTone"; // Watchlist
// import NewspaperTwoToneIcon from "@mui/icons-material/NewspaperTwoTone"; // Market News
// import NotificationsTwoToneIcon from "@mui/icons-material/NotificationsTwoTone"; // Notifications
// import MilitaryTechIcon from "@mui/icons-material/MilitaryTech"; // Portfolio
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet"; // Our Stock

// Sidebar container
const SidebarContainer = styled(Box)(({ expanded }) => ({
  width: expanded ? 200 : 70,
  height: "100vh",
  background: "linear-gradient(to right top, #051937, #002844, #00364e, #004554, #005357)",
  padding: "10px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  transition: "width 0.3s ease-in-out",
  position: "fixed",
  left: 0,
  top: 0,
  zIndex: 1000,
  borderRight: "2px solid rgba(255,255,255,0.1)",
  overflow: "hidden",
}));

// Sidebar item
const NavItem = styled(Link)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  width: "100%",
  padding: "12px",
  textDecoration: "none",
  color: "#fff",
  fontSize: "16px",
  fontWeight: "bold",
  borderRadius: "10px",
  transition: "background 0.3s ease-in-out",
  "&:hover": {
    background: "rgba(255, 255, 255, 0.2)",
  },
}));

// Icon styles
const IconWrapper = styled(IconButton)({
  fontSize: "24px",
  color: "#fff",
  transition: "transform 0.3s",
  "&:hover": {
    transform: "scale(1.1)",
  },
});

export default function Sidebar() {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <SidebarContainer
      expanded={expanded}
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
    >
      {/* Home */}
      <NavItem to="/">
        <Tooltip title="Home">
          <IconWrapper>
            <AccountBalanceIcon />
          </IconWrapper>
        </Tooltip>
        <Collapse in={expanded} orientation="horizontal">
          <Typography sx={{ ml: 2 }}>Home</Typography>
        </Collapse>
      </NavItem>

      {/* Watchlist */}
      <NavItem to="/watchlist">
        <Tooltip title="Watchlist">
          <IconWrapper>
            <TipsAndUpdatesTwoToneIcon />
          </IconWrapper>
        </Tooltip>
        <Collapse in={expanded} orientation="horizontal">
          <Typography sx={{ ml: 2 }}>Watchlist</Typography>
        </Collapse>
      </NavItem>

      {/* User Stocks */}
      <NavItem to="/userstocks">
        <Tooltip title="User Stocks">
          <IconWrapper>
            <AccountBalanceWalletIcon />
          </IconWrapper>
        </Tooltip>
        <Collapse in={expanded} orientation="horizontal">
          <Typography sx={{ ml: 2 }}>User Stocks</Typography>
        </Collapse>
      </NavItem>
    </SidebarContainer>
  );
}
