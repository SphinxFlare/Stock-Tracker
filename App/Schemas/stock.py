# App/Schemas/stock.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# Schema for creating a stock
class StockCreate(BaseModel):
    symbol: str
    name: str
    price: float

# Schema for returning stock data
class StockResponse(StockCreate):
    id: int

    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be converted to Pydantic models

# ✅ Schema for updating a stock (allows partial updates)
class StockUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    market_cap: Optional[float] = None


# ✅ Define Pydantic model for request body
class StockSymbolsRequest(BaseModel):
    symbols: List[str]


# ✅ Schema for creating a user stock
class UserStockCreate(BaseModel):
    symbol: str  # User selects from dropdown
    name: str    # Auto-filled based on `symbol`
    purchase_price: float  # User manually enters the price they bought at
    quantity: int
    purchase_date: datetime | None = None
    notes: str | None = None


class UserStockUpdate(BaseModel):
    purchase_price: float | None = None
    quantity: int | None = None
    notes: str | None = None


class UserStockResponse(UserStockCreate):
    id: int
    user_id: int



class TrendingStockSchema(BaseModel):
    id: int
    symbol: str
    name: str
    price: float
    change: float
    volume: int
    last_updated: date

    class Config:
        from_attributes = True   # ✅ Allows converting SQLAlchemy models to Pydantic


# ✅ Request body model
class WatchlistRequest(BaseModel):
    stock_symbol: str


# ✅ Stock Data Schema
class StockHistoryResponse(BaseModel):
    timestamp: datetime
    live_price: float
    current_value: float
    percentage_change: float

