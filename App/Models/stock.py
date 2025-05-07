# App/Models/stock.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, ARRAY
from sqlalchemy.orm import relationship
from App.Config.database import Base
from datetime import datetime
from sqlalchemy.sql import func

# ✅ Stock Model
class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    change = Column(Float, nullable=False)

    # Relationship with UserStock
    user_stocks = relationship("UserStock", back_populates="stock")

    # Relationship with StockAnalysisSnapshot (NEWLY ADDED)
    stock_snapshots = relationship("StockAnalysisSnapshot", back_populates="stock", cascade="all, delete-orphan")

# ✅ UserStock Model
class UserStock(Base):
    __tablename__ = "user_stocks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, ForeignKey("stocks.symbol"), nullable=False)  
    name = Column(String, nullable=False)
    purchase_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    # Relationship with Stock
    stock = relationship("Stock", back_populates="user_stocks")

# ✅ Portfolio Snapshot Model
class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"  # Renamed from `portfolio` for clarity

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_investment = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    total_profit_loss = Column(Float, nullable=False)
    overall_change = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

# ✅ Stock Analysis Snapshot Model (MODIFIED)
class StockAnalysisSnapshot(Base):
    __tablename__ = "stock_analysis_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    symbol = Column(String, ForeignKey("stocks.symbol"), index=True)  # Added ForeignKey to maintain integrity
    name = Column(String)
    purchase_price = Column(Float)
    live_price = Column(Float)
    quantity = Column(Integer)
    profit_loss = Column(Float)
    percentage_change = Column(Float)
    total_investment = Column(Float)
    current_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with Stock (NEW)
    stock = relationship("Stock", back_populates="stock_snapshots")



# ✅ Schema for Trending Stock
class TrendingStock(Base):
    __tablename__ = "trending_stocks"  # Table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)  # Auto-increment ID
    symbol = Column(String, unique=True, nullable=False)  # Stock ticker (e.g., "AAPL")
    name = Column(String, nullable=False)  # Company name
    price = Column(Float, nullable=False)  # Latest stock price
    change = Column(Float, nullable=False)  # Daily % change
    volume = Column(Integer, nullable=False)  # Trading volume
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)  # Last update timestamp





class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  
    stocks = Column(ARRAY(String), default=[])  # Store up to 10 stock symbols
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, ForeignKey("stock_data.symbol"), nullable=False, index=True)  # Link to StockData
    company_name = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)  # Timestamp of the data entry
    current_price = Column(Float, nullable=False)
    previous_close_price = Column(Float, nullable=True)
    percent_change = Column(Float, nullable=True)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)

    # Relationship with StockData (not mandatory but helpful)
    stock = relationship("StockData", back_populates="history")


class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    company_name = Column(String, nullable=True)
    current_price = Column(Float, nullable=False)
    previous_close_price = Column(Float, nullable=True)
    percent_change = Column(Float, nullable=True)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with StockHistory
    history = relationship("StockHistory", back_populates="stock", cascade="all, delete-orphan")

