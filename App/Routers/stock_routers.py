# App/Routers/stock_router.py

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from App.Config.database import get_db
from App.Config.debs import get_current_user
from App.Services.stock_service import (
    get_all_stocks, get_stock_by_symbol, update_stock, delete_stock,
    update_selected_stocks, get_user_stocks, update_user_stock, 
    delete_user_stock, add_user_stock, analyze_portfolio,
    search_stocks, save_portfolio_snapshot, save_stock_analysis_snapshot,
    update_all_user_stocks, update_user_stocks, fetch_stock_history
)
from App.Schemas.stock import ( 
    StockSymbolsRequest, UserStockResponse, UserStockCreate,
    UserStockUpdate, TrendingStockSchema, StockHistoryResponse                            
)
from App.Models.user import User
from App.Models.stock import  UserStock, StockAnalysisSnapshot
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime
from typing import List, Optional



stock_router = APIRouter(prefix="/stocks", tags=["Stocks"])
user_router = APIRouter(prefix="/userstocks", tags=["User Stocks"])


# ✅ Get all stocks
@stock_router.get("/")
async def fetch_all_stocks(db: AsyncSession = Depends(get_db)):
    return await get_all_stocks(db)

# ✅ Get stock by symbol
@stock_router.get("/{symbol}")
async def fetch_stock(symbol: str, db: AsyncSession = Depends(get_db)):
    stock = await get_stock_by_symbol(db, symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


# ✅ Update stock price
@stock_router.put("/{symbol}")
async def modify_stock(symbol: str, price: float, db: AsyncSession = Depends(get_db)):
    stock = await update_stock(db, symbol, price)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"message": "Stock updated successfully", "stock": stock}

# ✅ Delete stock
@stock_router.delete("/{symbol}")
async def remove_stock(symbol: str, db: AsyncSession = Depends(get_db)):
    stock = await delete_stock(db, symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"message": "Stock deleted successfully"}


# ✅ Route to update specific stocks
@stock_router.put("/stocks/update-selected-prices")
async def update_selected_stock_prices(
    request: StockSymbolsRequest = Body(...), 
    db: AsyncSession = Depends(get_db)
):
    print("Received request body:", request)
    print("Extracted symbols:", request.symbols)
    
    return await update_selected_stocks(db, request.symbols)



# ✅ API Endpoint for Stock Search
@stock_router.get("/stocks/search")
async def fetch_stocks_query(query: str, db: AsyncSession = Depends(get_db)):
    stocks = await search_stocks(db, query)
    return stocks if stocks else []  # Return an empty list if no matches


# ✅ Create a new stock entry for the logged-in user
@user_router.post("/add")
async def adding_user_stock(
    stock_data: UserStockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Get the authenticated user
):
    return await add_user_stock(db, stock_data, current_user.id)

# ✅ Get all stocks for the logged-in user
@user_router.get("/get")
async def fetch_user_stocks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Get the authenticated user
):
    return await get_user_stocks(db, current_user.id)

# ✅ Update a stock owned by the user
@user_router.put("/edit/{stock_id}")
async def modify_user_stock(
    stock_id: int,
    stock_data: UserStockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Get the authenticated user
):
    stock = await update_user_stock(db, stock_id, stock_data, current_user.id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found or not owned by user")
    return {"message": "Stock updated successfully", "stock": stock}

# ✅ Delete a stock owned by the user
@user_router.delete("/delete/{stock_id}")
async def remove_user_stock(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Get the authenticated user
):
    stock = await delete_user_stock(db, stock_id, current_user.id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found or not owned by user")
    return {"message": "Stock deleted successfully"}


@user_router.get("/portfolio/performance")
async def get_user_portfolio_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Fetch the latest stock snapshots for each symbol
    subquery = (
        select(StockAnalysisSnapshot.id)
        .where(StockAnalysisSnapshot.user_id == current_user.id)
        .order_by(StockAnalysisSnapshot.symbol, desc(StockAnalysisSnapshot.timestamp))
        .distinct(StockAnalysisSnapshot.symbol)
    ).subquery()

    result = await db.execute(
        select(StockAnalysisSnapshot)
        .where(StockAnalysisSnapshot.id.in_(subquery))
    )
    latest_snapshots = result.scalars().all()

    if not latest_snapshots:
        raise HTTPException(status_code=404, detail="No stock snapshots found for your portfolio")

    # ✅ Analyze the user's portfolio based on the latest stored snapshots
    portfolio_data = await analyze_portfolio(latest_snapshots)

    # ✅ Save portfolio snapshot
    await save_portfolio_snapshot(current_user.id, portfolio_data, db)

    return portfolio_data


@user_router.post("/update-stocks")
async def update_stocks_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ✅ Triggers stock analysis snapshot update for the logged-in user.
    """
    await update_user_stocks(current_user.id, db)  # ✅ Fixed function call
    return {"message": "Stock snapshot updated successfully! 🚀"}


# ✅ Async API to fetch stock price history with date filters
@user_router.get("/stocks/{symbol}/history", response_model=List[StockHistoryResponse])
async def get_stock_history(
    symbol: str,
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """API endpoint to fetch stock price history with optional date filters"""
    return await fetch_stock_history(symbol, start_date, end_date, db)



@user_router.get("/stock_analysis")
async def update_stocks_route(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(StockAnalysisSnapshot))
    return result.scalars().all()







