# App/Services/feat_service.py

from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from App.Models.stock import Stock, Watchlist
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import array
import yfinance as yf
from App.Models.stock import StockData, StockHistory
from datetime import datetime



async def add_stock_to_watchlist(user_id: int, stock_symbol: str, db: AsyncSession):
    """Add a single stock to the user's watchlist with validation."""

    # 1️⃣ Fetch the user's watchlist
    result = await db.execute(select(Watchlist).where(Watchlist.user_id == user_id))
    watchlist = result.scalars().first()

    # 2️⃣ Fetch stock details from Stock table
    stock_result = await db.execute(select(Stock).where(Stock.symbol == stock_symbol))
    stock = stock_result.scalars().first()

    if not stock:  # ❌ Invalid stock symbol
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    if watchlist:
        watchlist_stocks = watchlist.stocks or []  # Ensure it's a list

        # 3️⃣ Check if stock is already in the watchlist
        if stock_symbol in watchlist_stocks:
            raise HTTPException(status_code=400, detail="Stock already in watchlist")

        # 4️⃣ Enforce the limit of 10 stocks
        if len(watchlist_stocks) >= 10:
            raise HTTPException(status_code=400, detail="Watchlist cannot exceed 10 stocks")

        # ✅ Use PostgreSQL `array_append()` to update the ARRAY column
        stmt = (
            Watchlist.__table__.update()
            .where(Watchlist.user_id == user_id)
            .values(
                stocks=func.array_append(Watchlist.stocks, stock_symbol),
                updated_at=func.now()
            )
        )
        await db.execute(stmt)

    else:
        # 6️⃣ Create a new watchlist
        watchlist = Watchlist(user_id=user_id, stocks=[stock_symbol])
        db.add(watchlist)

    # 7️⃣ Commit changes to DB with error handling
    try:
        await db.commit()
        if watchlist:
            await db.refresh(watchlist)
    except Exception as e:
        await db.rollback()
        print(f"❌ Commit failed: {e}")  # Log the actual error
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    # 🔥 Ensure the stock update runs
    print(f"🚀 Triggering update for: {stock_symbol}") 

    # 8️⃣ Fetch fresh stock data from yfinance **only once**
    await update_stock_data(stock_symbol, db)

    return {"message": f"{stock_symbol} added to watchlist"}



async def get_user_watchlist(user_id: int, db: AsyncSession):
    """Retrieve and display the user's watchlist with stock details."""

    # 1️⃣ Fetch the user's watchlist
    result = await db.execute(select(Watchlist).where(Watchlist.user_id == user_id))
    watchlist = result.scalars().first()

    # 2️⃣ If the user has no watchlist, return an empty list
    if not watchlist or not watchlist.stocks:
        return {"message": "Your watchlist is empty", "watchlist": []}

    # 3️⃣ Fetch stock details from the Stock table
    stock_details_result = await db.execute(
        select(Stock).where(Stock.symbol.in_(watchlist.stocks))
    )
    stock_details = stock_details_result.scalars().all()

    # 4️⃣ Format and return the watchlist data
    watchlist_data = [
        {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "price": stock.price,
            "change": stock.change
        }
        for stock in stock_details
    ]

    return {"watchlist": watchlist_data}


async def update_stock_data(symbol: str, db: AsyncSession):
    """Fetch new stock data only if it’s not already stored."""
    print(f"🔍 Checking stock data for: {symbol}")  # Debugging

    # Check if stock already exists
    result = await db.execute(select(StockData).where(StockData.symbol == symbol))
    stock = result.scalars().first()

    if stock:  
        print(f"✅ Stock {symbol} already exists, returning stored data: {stock}")
        return {"message": f"Stock {symbol} data already stored", "data": stock}

    # Fetch new data
    print(f"🌐 Fetching new data for: {symbol}")
    try:
        stock_info = yf.Ticker(symbol).info
        new_price = stock_info.get("regularMarketPrice")
        prev_close = stock_info.get("regularMarketPreviousClose")
        percent_change = ((new_price - prev_close) / prev_close) * 100 if prev_close else None
        high_24h = stock_info.get("dayHigh")
        low_24h = stock_info.get("dayLow")
        volume = stock_info.get("volume")
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return {"error": f"Failed to fetch stock data: {e}"}

    # Insert into StockData table
    new_stock = StockData(
        symbol=symbol,
        company_name=stock_info.get("shortName"),
        current_price=new_price,
        previous_close_price=prev_close,
        percent_change=percent_change,
        high_24h=high_24h,
        low_24h=low_24h,
        volume=volume,
        last_updated=datetime.utcnow()
    )
    db.add(new_stock)
    print(f"✅ New stock {symbol} added to StockData: {new_stock}")

    # Insert into StockHistory table
    stock_history_entry = StockHistory(
        symbol=new_stock.symbol,
        company_name=new_stock.company_name,
        current_price=new_price,
        previous_close_price=prev_close,
        percent_change=percent_change,
        high_24h=high_24h,
        low_24h=low_24h,
        volume=volume,
        recorded_at=new_stock.last_updated
    )
    db.add(stock_history_entry)
    print(f"📌 Stock history entry added for {symbol}: {stock_history_entry}")

    # Commit changes
    try:
        await db.commit()
        await db.refresh(new_stock)
        print("✅ Commit successful!")
    except Exception as e:
        await db.rollback()
        print(f"❌ Commit failed: {e}")
        return {"error": f"Database commit failed: {e}"}

    return {"message": f"Stock {symbol} updated successfully", "data": new_stock}




async def Add_stock_to_watchlist(user_id, stock_symbol, db):
    # Fetch the user's watchlist
    watchlist = await db.execute(
        select(Watchlist).where(Watchlist.user_id == user_id)
    )
    watchlist = watchlist.scalar_one_or_none()

    if not watchlist:
        # Create a new watchlist if it doesn’t exist
        watchlist = Watchlist(user_id=user_id, stocks=[], updated_at=datetime.utcnow())
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

    # Check if stock is already in the watchlist
    if stock_symbol in watchlist.stocks:
        return {"message": f"{stock_symbol} is already in your watchlist"}


    # Use PostgreSQL array_append to safely add the stock symbol
    await db.execute(
        Watchlist.__table__.update()
        .where(Watchlist.user_id == user_id)
        .values(
            stocks=func.array_append(Watchlist.stocks, stock_symbol),
            updated_at=datetime.utcnow()
        )
    )

    await db.commit()

    # Refresh the watchlist to get the latest data
    await db.refresh(watchlist)

    return watchlist


async def update_watchlist_stocks(user_id: int, db: AsyncSession):
    """Fetch all stocks from a user's watchlist and update their data."""
    print("Update function triggers")
    
    # Retrieve user's watchlist
    result = await db.execute(select(Watchlist).where(Watchlist.user_id == user_id))
    watchlist = result.scalar_one_or_none()

    if not watchlist or not watchlist.stocks:
        return {"message": "No stocks in watchlist to update"}

    updated_stocks = set()  # Use a set to avoid duplicates
    errors = []

    # Loop through each stock and update
    for symbol in watchlist.stocks:
        normalized_symbol = symbol.upper()  # Normalize to uppercase
        result = await update_stock_data(normalized_symbol, db)
        
        if "error" in result:
            errors.append({normalized_symbol: result["error"]})
        else:
            updated_stocks.add(normalized_symbol)  # Store only uppercase symbols

    return {
        "updated_stocks": list(updated_stocks),  # Convert back to list for JSON response
        "errors": errors if errors else None
    }



async def check_stock_data(symbol: str, db: AsyncSession):
    """Retrieve stock data from both StockData and StockHistory."""
    
    # Check StockData table
    result_data = await db.execute(select(StockData).where(StockData.symbol == symbol))
    stock_data = result_data.scalars().first()
    
    # Check StockHistory table
    result_history = await db.execute(select(StockHistory).where(StockHistory.symbol == symbol))
    stock_history = result_history.scalars().all()  # Get all history records for that stock

    return {
        "StockData": stock_data,
        "StockHistory": stock_history
    }



async def get_updated_watchlist(user_id: int, db: AsyncSession):
    """Retrieve and update the user's watchlist with the latest stock data, handling missing stocks."""
    
    # 1️⃣ Fetch the user's watchlist
    result = await db.execute(select(Watchlist).where(Watchlist.user_id == user_id))
    watchlist = result.scalars().first()

    # 2️⃣ If no watchlist or it's empty, return a message
    if not watchlist or not watchlist.stocks:
        return {"message": "Your watchlist is empty", "watchlist": []}

    # 3️⃣ Fetch updated stock details from stock_data
    stock_data_result = await db.execute(
        select(StockData).where(StockData.symbol.in_(watchlist.stocks))
    )
    stock_data_list = stock_data_result.scalars().all()

    # 4️⃣ Convert stock_data_list to a dictionary for easy lookup
    stock_data_dict = {stock.symbol: stock for stock in stock_data_list}

    # 5️⃣ Build the response, handling missing stocks
    watchlist_data = []
    for symbol in watchlist.stocks:
        if symbol in stock_data_dict:
            stock = stock_data_dict[symbol]
            watchlist_data.append({
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "current_price": stock.current_price,
                "previous_close_price": stock.previous_close_price,
                "percent_change": stock.percent_change,
                "high_24h": stock.high_24h,
                "low_24h": stock.low_24h,
                "volume": stock.volume,
                "last_updated": stock.last_updated,
                "status": "Available"
            })
        else:
            # Stock is in the watchlist but missing from StockData
            watchlist_data.append({
                "symbol": symbol,
                "company_name": None,
                "current_price": None,
                "previous_close_price": None,
                "percent_change": None,
                "high_24h": None,
                "low_24h": None,
                "volume": None,
                "last_updated": None,
                "status": "Data unavailable"
            })

    return {"watchlist": watchlist_data}

