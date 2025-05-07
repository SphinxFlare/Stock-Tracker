# App/Services/stock_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from App.Models.stock import (
    Stock, UserStock, PortfolioSnapshot, StockAnalysisSnapshot
    )
from App.Schemas.stock import (
    StockCreate, StockUpdate, UserStockCreate, 
    UserStockUpdate,
)
import pandas as pd
import os
from sqlalchemy import text
import yfinance as yf
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException
import pytz



india_tz = pytz.timezone("Asia/Kolkata")


CSV_FILE_PATH = "App/Data/company_data.csv"  # Update with your actual path


# ✅ Create a new stock
async def create_stock(db: AsyncSession, stock_data: StockCreate):
    new_stock = Stock(**stock_data.model_dump())  # Convert Pydantic model to dictionary
    db.add(new_stock)
    await db.commit()
    await db.refresh(new_stock)  # Reload from DB
    return new_stock

# ✅ Get all stocks
async def get_all_stocks(db: AsyncSession):
    result = await db.execute(select(Stock))
    return result.scalars().all()

# ✅ Get stock by symbol
async def get_stock_by_symbol(db: AsyncSession, symbol: str):
    result = await db.execute(select(Stock).where(Stock.symbol == symbol))
    return result.scalars().first()


# ✅ Update a stock
async def update_stock(db: AsyncSession, symbol: str, stock_data: StockUpdate):
    result = await db.execute(select(Stock).where(Stock.symbol == symbol))
    stock = result.scalars().first()
    
    if not stock:
        return None  # Stock not found
    
    for key, value in stock_data.model_dump(exclude_unset=True).items():
        setattr(stock, key, value)  # Update only provided fields
    
    await db.commit()
    await db.refresh(stock)
    return stock

# ✅ Delete a stock
async def delete_stock(db: AsyncSession, symbol: str):
    result = await db.execute(select(Stock).where(Stock.symbol == symbol))
    stock = result.scalars().first()
    
    if not stock:
        return None  # Stock not found
    
    await db.delete(stock)
    await db.commit()
    return stock

# ✅ Function to Load CSV into DB
async def load_csv_to_db(db: AsyncSession):
    """Reads stock data from CSV and inserts it into the database."""
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"⚠️ CSV file not found at {CSV_FILE_PATH}!")
        return

    df = pd.read_csv(CSV_FILE_PATH)

    # ✅ Check if required columns exist
    required_cols = ["Name", "Last", "High", "Low", "Chg.", "Change%", "Vol.", "Time", "Ticker"]
    if not all(col in df.columns for col in required_cols):
        print("⚠️ CSV format is incorrect. Make sure all required columns exist.")
        return

    # ✅ Clear old data before inserting new data
    await db.execute(text("TRUNCATE TABLE stocks RESTART IDENTITY CASCADE"))
    await db.commit()

    # ✅ Insert new stock data
    for _, row in df.iterrows():
        await db.execute(text("""
            INSERT INTO stocks (symbol, name, price, change)
            VALUES (:symbol, :name, :price, :change)
            ON CONFLICT (symbol) DO NOTHING
        """), {
            "symbol": row["Ticker"],
            "name": row["Name"],
            "price": float(row["Last"].replace(',', '')),  # ✅ Remove commas before converting to float
            "change": float(row["Change%"].replace('%', '')) 
        })

    await db.commit()
    print("✅ Stock data successfully loaded into the database.")


# ✅ Function to update only selected stocks
async def update_selected_stocks(db: AsyncSession, symbols: list):
    if not symbols:
        print("⚠️ No stock symbols provided!")
        return {"error": "No stock symbols provided"}

    print(f"🔄 Fetching live stock prices for: {symbols}")
    
    try:
        # Fetch stock prices for selected stocks
        old_price = 0
        stock_data = yf.download(tickers=" ".join(symbols), period="1d", interval="1m")
        for symbol in symbols:
            if symbol in stock_data["Close"]:
                latest_price = stock_data["Close"][symbol].dropna().iloc[-1]  # Get latest adjusted closing price

                stock_result = await db.execute(select(Stock).where(Stock.symbol == symbol))
                stock = stock_result.scalars().first()

                if stock:
                    old_price = stock.price
                    stock.price = latest_price
                    await db.commit()
                    await db.refresh(stock)
                    print(f"✅ Updated {symbol}: ${latest_price}")

        return {"message": f"{stock.name} price updated from {old_price} to {latest_price} successfully"}

    except Exception as e:
        print(f"❌ Error updating stocks: {e}")
        return {"error": str(e)}
    
# ✅ Fetch all available stocks for dropdown (Ticker & Name)
async def get_available_stocks(db: AsyncSession):
    """Get available stocks for dropdown selection."""
    result = await db.execute(select(Stock.symbol, Stock.name))
    stocks = result.fetchall()
    return [{"symbol": s[0], "name": s[1]} for s in stocks]


# ✅ Add a stock for a specific user
async def add_user_stock(db: AsyncSession, stock_data: UserStockCreate, user_id: int):
    try:
        new_stock = UserStock(**stock_data.model_dump(), user_id=user_id)
        db.add(new_stock)
        await db.commit()
        await db.refresh(new_stock)  # ✅ Ensure stock is fully stored before updating

        print(f"✅ New stock {new_stock.symbol} added, now updating stock data...")

        # 2️⃣ Trigger stock data update
        await update_all_user_stocks(db, user_id)

        return {"message": f"Stock {new_stock.symbol} added and updated successfully!"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")


# ✅ Get all stocks belonging to a specific user
async def get_user_stocks(db: AsyncSession, user_id: int):
    result = await db.execute(select(UserStock).where(UserStock.user_id == user_id))
    return result.scalars().all()


# ✅ Update stock for a specific user
async def update_user_stock(db: AsyncSession, stock_id: int, stock_data: UserStockUpdate, user_id: int):
    result = await db.execute(select(UserStock).where(UserStock.id == stock_id, UserStock.user_id == user_id))
    stock = result.scalars().first()

    if not stock:
        return {"error": "Stock not found or unauthorized"}

    for key, value in stock_data.model_dump(exclude_unset=True).items():
        setattr(stock, key, value)

    await db.commit()
    await db.refresh(stock)
    return stock


# ✅ Delete stock for a specific user
async def delete_user_stock(db: AsyncSession, stock_id: int, user_id: int):
    result = await db.execute(select(UserStock).where(UserStock.id == stock_id, UserStock.user_id == user_id))
    stock = result.scalars().first()

    if not stock:
        return {"error": "Stock not found or unauthorized"}

    await db.delete(stock)
    await db.commit()
    return {"message": "Stock deleted successfully"}



# ✅ Get stocks by name (autocomplete search)
async def search_stocks(db: AsyncSession, name: str):
    result = await db.execute(
        select(Stock)
        .where(Stock.name.ilike(f"%{name}%"))  # Case-insensitive search for names that start with `query`
        .limit(5)  # Limit results to 10 for performance
    )
    return result.scalars().all()



# ✅ Fetch Live Price of a Stock
async def fetch_live_price(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        live_price = stock.history(period="1d")["Close"].iloc[-1]  # Get last closing price
        return live_price
    except Exception as e:
        raise Exception(f"Error fetching live price for {symbol}: {str(e)}")


# ✅ Fetch Latest Stock Data for Portfolio Analysis
async def analyze_portfolio(latest_snapshots: list[StockAnalysisSnapshot]):
    portfolio_summary = {
        "total_investment": 0,
        "current_value": 0,
        "total_profit_loss": 0,
        "stock_analysis": []
    }

    for stock in latest_snapshots:
        live_price = stock.live_price  # ✅ Use stored live price  
        total_investment = stock.purchase_price * stock.quantity
        current_value = live_price * stock.quantity
        profit_loss = current_value - total_investment
        percentage_change = ((live_price - stock.purchase_price) / stock.purchase_price) * 100

        # Update portfolio summary
        portfolio_summary["total_investment"] += total_investment
        portfolio_summary["current_value"] += current_value
        portfolio_summary["total_profit_loss"] += profit_loss

        # Store individual stock analysis
        portfolio_summary["stock_analysis"].append({
            "symbol": stock.symbol,
            "name": stock.name,
            "purchase_price": stock.purchase_price,
            "live_price": live_price,
            "quantity": stock.quantity,
            "profit_loss": profit_loss,
            "percentage_change": round(percentage_change, 2),
            "total_investment": total_investment,
            "current_value": current_value
        })

    # Calculate overall change percentage
    portfolio_summary["overall_change_percentage"] = (
        (portfolio_summary["total_profit_loss"] / portfolio_summary["total_investment"]) * 100
        if portfolio_summary["total_investment"] > 0 else 0
    )

    return portfolio_summary



# ✅ Save Portfolio Snapshot to Database (Async)
async def save_portfolio_snapshot(user_id: int, portfolio_data: dict, db: AsyncSession):
    snapshot = PortfolioSnapshot(
        user_id=user_id,
        total_investment=portfolio_data["total_investment"],
        current_value=portfolio_data["current_value"],
        total_profit_loss=portfolio_data["total_profit_loss"],
        overall_change=portfolio_data["overall_change_percentage"],
    )

    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)

    return snapshot


# ✅ Save Stock Analysis Snapshot to Database (Async)
async def save_stock_analysis_snapshot(user_id: int, stock_data: dict, db: AsyncSession):
    snapshot = StockAnalysisSnapshot(
        user_id=user_id,
        symbol=stock_data["symbol"],
        name=stock_data["name"],
        purchase_price=stock_data["purchase_price"],
        live_price=stock_data["live_price"],
        quantity=stock_data["quantity"],
        profit_loss=stock_data["profit_loss"],
        percentage_change=stock_data["percentage_change"],
        total_investment=stock_data["total_investment"],
        current_value=stock_data["current_value"],
        timestamp=datetime.utcnow()
    )

    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)

    return snapshot



# async def update_user_stocks(user_id: int, db: AsyncSession):
#     """
#     ✅ Updates stock analysis snapshots for the user.
#     """
#     try:
#         today = datetime.now(india_tz).date()

#         # ✅ Check last update to avoid multiple fetches
#         result = await db.execute(
#             select(StockAnalysisSnapshot.timestamp)
#             .where(StockAnalysisSnapshot.user_id == user_id)
#             .order_by(StockAnalysisSnapshot.timestamp.desc())
#             .limit(1)
#         )
#         last_updated = result.scalar()

#         if last_updated and last_updated.astimezone(india_tz).date() == today:
#             print("🔹 Data is already updated today. Skipping fetch.")
#             return  # Prevent unnecessary API calls

#         # ✅ Fetch all stocks the user holds
#         stocks = await db.execute(select(UserStock).where(UserStock.user_id == user_id))
#         user_stocks = stocks.scalars().all()

#         for stock in user_stocks:
#             try:
#                 ticker = stock.symbol
#                 yf_stock = yf.Ticker(ticker)
#                 info = yf_stock.history(period="2d")  # ✅ Get 2 days of data

#                 if len(info) < 2:
#                     print(f"❌ Not enough data for {ticker}, skipping.")
#                     continue

#                 latest_price = info["Close"].iloc[-1]
#                 prev_close = info["Close"].iloc[-2]
#                 change = latest_price - prev_close
#                 change_percent = round((change / prev_close) * 100, 2)

#                 purchase_price = stock.purchase_price
#                 quantity = stock.quantity
#                 total_investment = purchase_price * quantity
#                 current_value = latest_price * quantity
#                 profit_loss = round(current_value - total_investment, 2)

#                 # ✅ Check if an entry for today already exists
#                 existing_snapshot = await db.execute(
#                     select(StockAnalysisSnapshot).where(
#                         StockAnalysisSnapshot.user_id == user_id,
#                         StockAnalysisSnapshot.symbol == ticker,
#                         StockAnalysisSnapshot.timestamp >= today
#                     )
#                 )
#                 existing_snapshot = existing_snapshot.scalars().first()

#                 if existing_snapshot:
#                     # ✅ Update existing snapshot
#                     await db.execute(
#                         update(StockAnalysisSnapshot)
#                         .where(StockAnalysisSnapshot.id == existing_snapshot.id)
#                         .values(
#                             live_price=latest_price,
#                             profit_loss=profit_loss,
#                             percentage_change=change_percent,
#                             current_value=current_value,
#                             timestamp=datetime.now(india_tz)

#                         )
#                     )
#                 else:
#                     # ✅ Insert new snapshot
#                     new_snapshot = StockAnalysisSnapshot(
#                         user_id=user_id,
#                         symbol=ticker,
#                         name=stock.name,
#                         purchase_price=purchase_price,
#                         live_price=latest_price,
#                         quantity=quantity,
#                         profit_loss=profit_loss,
#                         percentage_change=change_percent,
#                         total_investment=total_investment,
#                         current_value=current_value,
#                         timestamp=datetime.now(india_tz)

#                     )
#                     db.add(new_snapshot)

#             except Exception as e:
#                 print(f"❌ Error fetching data for {stock.symbol}: {e}")

#         # ✅ Commit all changes once
#         await db.commit()
#         print("✅ Stock analysis snapshot updated successfully.")

#     except Exception as e:
#         await db.rollback()
#         print(f"❌ Error updating stock snapshots: {e}")



async def update_all_user_stocks(db: AsyncSession, user_id: int):
    """
    ✅ Fetches the latest stock prices for all user stocks and updates StockAnalysisSnapshot.
    """
    try:
        # 1️⃣ Get all user stocks
        result = await db.execute(select(UserStock).where(UserStock.user_id == user_id))
        user_stocks = result.scalars().all()

        if not user_stocks:
            print("⚠️ No stocks found for the user.")
            return

        print(f"✅ Found {len(user_stocks)} stocks for user {user_id}.")

        # 2️⃣ Fetch live data for each stock
        for stock in user_stocks:
            try:
                ticker = stock.symbol
                yf_stock = yf.Ticker(ticker)
                info = yf_stock.history(period="2d")  # ✅ Get last 2 days' data

                if len(info) < 2:
                    print(f"❌ Not enough data for {ticker}, skipping.")
                    continue

                latest_price = info["Close"].iloc[-1]
                prev_close = info["Close"].iloc[-2]
                change = latest_price - prev_close
                change_percent = round((change / prev_close) * 100, 2)

                purchase_price = stock.purchase_price
                quantity = stock.quantity
                total_investment = purchase_price * quantity
                current_value = latest_price * quantity
                profit_loss = round(current_value - total_investment, 2)

                # 3️⃣ Check if today's snapshot exists
                existing_snapshot = await db.execute(
                    select(StockAnalysisSnapshot).where(
                        StockAnalysisSnapshot.user_id == user_id,
                        StockAnalysisSnapshot.symbol == ticker,
                        StockAnalysisSnapshot.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)  # ✅ Fixed datetime issue
                    )
                )
                existing_snapshot = existing_snapshot.scalars().first()

                if existing_snapshot:
                    # ✅ Update existing snapshot
                    await db.execute(
                        update(StockAnalysisSnapshot)
                        .where(StockAnalysisSnapshot.id == existing_snapshot.id)
                        .values(
                            live_price=latest_price,
                            profit_loss=profit_loss,
                            percentage_change=change_percent,
                            current_value=current_value,
                            timestamp=datetime.utcnow(),
                        )
                    )
                else:
                    # ✅ Insert new snapshot
                    new_snapshot = StockAnalysisSnapshot(
                        user_id=user_id,
                        symbol=ticker,
                        name=stock.name,
                        purchase_price=purchase_price,
                        live_price=latest_price,
                        quantity=quantity,
                        profit_loss=profit_loss,
                        percentage_change=change_percent,
                        total_investment=total_investment,
                        current_value=current_value,
                        timestamp=datetime.utcnow()
                    )
                    db.add(new_snapshot)

            except Exception as e:
                print(f"❌ Error fetching data for {stock.symbol}: {e}")

        # ✅ Commit all changes once
        await db.commit()
        print("✅ Stock analysis snapshot updated successfully.")

    except Exception as e:
        await db.rollback()
        print(f"❌ Error updating stock snapshots: {e}")


async def fetch_stock_history(
    symbol: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    db: AsyncSession
) -> List[StockAnalysisSnapshot]:
    """Fetch stock history for a given symbol within a date range"""

    # ✅ Default: Last 7 days if no start_date provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    
    # ✅ Default: Today's date if no end_date provided
    if not end_date:
        end_date = datetime.utcnow()

    # 🛠️ Query database for filtered stock history
    query = (
        select(StockAnalysisSnapshot)
        .where(StockAnalysisSnapshot.symbol == symbol)
        .where(StockAnalysisSnapshot.timestamp >= start_date)
        .where(StockAnalysisSnapshot.timestamp <= end_date)
        .order_by(StockAnalysisSnapshot.timestamp)
    )

    result = await db.execute(query)
    stock_records = result.scalars().all()

    if not stock_records:
        raise HTTPException(status_code=404, detail="No history found for this stock in the given date range")

    return stock_records








async def update_user_stocks(user_id: int, db: AsyncSession):
    """
    ✅ Updates stock analysis snapshots for the user (now UTC based).
    """
    try:
        # 🕒 Use UTC for all datetime logic
        today_utc = datetime.utcnow().date()

        result = await db.execute(
            select(StockAnalysisSnapshot.timestamp)
            .where(StockAnalysisSnapshot.user_id == user_id)
            .order_by(StockAnalysisSnapshot.timestamp.desc())
            .limit(1)
        )
        last_updated = result.scalar()

        if last_updated and last_updated.date() == today_utc:
            print("🔹 Data is already updated today (UTC). Skipping fetch.")
            return

        stocks = await db.execute(select(UserStock).where(UserStock.user_id == user_id))
        user_stocks = stocks.scalars().all()

        print(f"👥 Found {len(user_stocks)} stock(s) for user {user_id}.")

        for stock in user_stocks:
            try:
                ticker = stock.symbol
                print(f"📈 Fetching data for stock: {ticker}")
                yf_stock = yf.Ticker(ticker)
                info = yf_stock.history(period="2d")

                print(f"Fetched data for {ticker}: {info}")

                if len(info) < 2:
                    print(f"❌ Not enough data for {ticker}, skipping.")
                    continue

                latest_price = info["Close"].iloc[-1]
                prev_close = info["Close"].iloc[-2]
                change = latest_price - prev_close
                change_percent = round((change / prev_close) * 100, 2)

                purchase_price = stock.purchase_price
                quantity = stock.quantity
                total_investment = purchase_price * quantity
                current_value = latest_price * quantity
                profit_loss = round(current_value - total_investment, 2)

                # ✅ Use UTC timestamp
                utc_now = datetime.utcnow()

                existing_snapshot = await db.execute(
                    select(StockAnalysisSnapshot).where(
                        StockAnalysisSnapshot.user_id == user_id,
                        StockAnalysisSnapshot.symbol == ticker,
                        StockAnalysisSnapshot.timestamp >= datetime.combine(today_utc, datetime.min.time())
                    )
                )
                existing_snapshot = existing_snapshot.scalars().first()

                if existing_snapshot:
                    await db.execute(
                        update(StockAnalysisSnapshot)
                        .where(StockAnalysisSnapshot.id == existing_snapshot.id)
                        .values(
                            live_price=latest_price,
                            profit_loss=profit_loss,
                            percentage_change=change_percent,
                            current_value=current_value,
                            timestamp=utc_now  # ✅ Now UTC timestamp
                        )
                    )
                    print(f"🔄 Updated snapshot for {ticker}.")
                else:
                    new_snapshot = StockAnalysisSnapshot(
                        user_id=user_id,
                        symbol=ticker,
                        name=stock.name,
                        purchase_price=purchase_price,
                        live_price=latest_price,
                        quantity=quantity,
                        profit_loss=profit_loss,
                        percentage_change=change_percent,
                        total_investment=total_investment,
                        current_value=current_value,
                        timestamp=utc_now  # ✅ Now UTC timestamp
                    )
                    db.add(new_snapshot)
                    print(f"✅ Inserted new snapshot for {ticker}.")

            except Exception as e:
                print(f"❌ Error fetching data for {stock.symbol}: {e}")

        await db.commit()
        print("✅ Stock analysis snapshot updated successfully.")

    except Exception as e:
        await db.rollback()
        print(f"❌ Error updating stock snapshots for user {user_id}: {e}")