# tasks/update_snapshots.py

from App.celery_worker import celery
from App.Config.database import get_db
from App.Models.user import User
from App.Models.stock import StockAnalysisSnapshot, UserStock
from sqlalchemy.future import select
from sqlalchemy import update
import yfinance as yf
from datetime import datetime, timedelta
import asyncio




async def _update_user_snapshot(user_id: int, db):
    result = await db.execute(select(UserStock).where(UserStock.user_id == user_id))
    user_stocks = result.scalars().all()

    if not user_stocks:
        print(f"⚠️ No stocks found for user {user_id}. Skipping.")
        return

    # 🛑 Fetch existing snapshots for today
    today = datetime.utcnow().date()
    existing_snapshots = await db.execute(
        select(StockAnalysisSnapshot.symbol)
        .where(StockAnalysisSnapshot.user_id == user_id)
        .where(StockAnalysisSnapshot.timestamp >= datetime.combine(today, datetime.min.time()))
    )
    updated_symbols_today = set(existing_snapshots.scalars().all())  # Set of stock symbols updated today

    for stock in user_stocks:
        ticker = stock.symbol

        # ⏭️ Skip stock if it was already updated today
        if ticker in updated_symbols_today:
            print(f"⏭️ Already updated {ticker} today. Skipping.")
            continue
        
        try:
            print(f"📈 Fetching data for {ticker}")
            info = yf.Ticker(ticker).history(period="2d")

            if info.empty or len(info) < 2:
                print(f"❌ Not enough data for {ticker}. Skipping.")
                continue

            latest_price = info["Close"].iloc[-1]
            prev_price = info["Close"].iloc[-2]
            pct_change = round(((latest_price - prev_price) / prev_price) * 100, 2)

            quantity = stock.quantity
            investment = stock.purchase_price * quantity
            current_value = latest_price * quantity
            profit_loss = current_value - investment

            now = datetime.utcnow()

            # Check if snapshot exists for this stock today
            existing = await db.execute(
                select(StockAnalysisSnapshot)
                .where(StockAnalysisSnapshot.user_id == user_id)
                .where(StockAnalysisSnapshot.symbol == ticker)
                .where(StockAnalysisSnapshot.timestamp >= datetime.combine(today, datetime.min.time()))
            )
            snapshot = existing.scalars().first()

            if snapshot:
                await db.execute(
                    update(StockAnalysisSnapshot)
                    .where(StockAnalysisSnapshot.id == snapshot.id)
                    .values(
                        live_price=latest_price,
                        profit_loss=profit_loss,
                        percentage_change=pct_change,
                        current_value=current_value,
                        timestamp=now
                    )
                )
                print(f"🔄 Updated snapshot for {ticker}")
            else:
                new_snapshot = StockAnalysisSnapshot(
                    user_id=user_id,
                    symbol=ticker,
                    name=stock.name,
                    purchase_price=stock.purchase_price,
                    live_price=latest_price,
                    quantity=quantity,
                    profit_loss=profit_loss,
                    percentage_change=pct_change,
                    total_investment=investment,
                    current_value=current_value,
                    timestamp=now
                )
                db.add(new_snapshot)
                print(f"✅ Inserted new snapshot for {ticker}")

        except Exception as e:
            print(f"❌ Error with {ticker}: {str(e)}")




@celery.task
def update_all_users_snapshots():
    print("📡 Starting scheduled update...")
    asyncio.run(_run_update_task())

async def _run_update_task():
    async for session in get_db():
        user_ids = (await session.execute(select(User.id))).scalars().all()

        for user_id in user_ids:
            print(f"👤 Updating stocks for user: {user_id}")
            await _update_user_snapshot(user_id, session)
        
        await session.commit()
        print("✅ All users updated.")
