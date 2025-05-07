# App/Routers/feat_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from App.Schemas.stock import WatchlistRequest
from App.Models.user import User
from App.Models.stock import Watchlist, StockData
from App.Config.debs import get_current_user
from App.Config.database import get_db
from App.Services.feat_service import(
    add_stock_to_watchlist, get_user_watchlist, check_stock_data,
    update_watchlist_stocks, get_updated_watchlist
    )


feat_router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"]
)


@feat_router.get("/", summary="Get user's watchlist with stock details")
async def get_watchlist(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)):
    """
    Fetch the watchlist for a given user, including stock details.
    """
    watchlist = await get_updated_watchlist(current_user.id, db)

    if not watchlist:
        raise HTTPException(status_code=404, detail="No watchlist found for user")

    return {"watchlist": watchlist}



@feat_router.post("/add", summary="Add a stock to the user's watchlist")
async def add_stock(
    request: WatchlistRequest,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)):
    """
    Add a stock to the user's watchlist.
    """
    try:
        result = await add_stock_to_watchlist(current_user.id, request.stock_symbol, db)
        return {"message": result}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    

@feat_router.delete("/remove/{stock_symbol}", summary="Remove a stock from the user's watchlist")
async def remove_watchlist(
    stock_symbol: str,  
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a stock from the user's watchlist without deleting the entire entry."""

    # Fetch the user's watchlist
    result = await db.execute(select(Watchlist).where(Watchlist.user_id == current_user.id))
    watchlist = result.scalars().first()

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist does not exist")

    if stock_symbol not in watchlist.stocks:
        raise HTTPException(status_code=404, detail="Stock not found in watchlist")

    # Use array_remove to update the array correctly
    stmt = (
        Watchlist.__table__.update()
        .where(Watchlist.user_id == current_user.id)
        .values(
            stocks=func.array_remove(Watchlist.stocks, stock_symbol),
            updated_at=func.now()
        )
    )
    await db.execute(stmt)

    # Fetch the updated watchlist
    result = await db.execute(select(Watchlist).where(Watchlist.user_id == current_user.id))
    watchlist = result.scalars().first()

    # If the stocks array is empty, delete the watchlist
    if not watchlist.stocks:
        await db.delete(watchlist)

    await db.commit()

    return {"message": f"Stock {stock_symbol} removed from watchlist"}




@feat_router.get("/check/{symbol}", summary="Check stock data and history")
async def check_stock(
    symbol: str,  
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve stock data from both StockData and StockHistory."""
    return await check_stock_data(symbol, db)


@feat_router.put("/update-watchlist/{user_id}")
async def update_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ):
    result = await update_watchlist_stocks(current_user.id, db)
    return result

@feat_router.get("/stock_data")
async def get_stockdata(db: AsyncSession = Depends(get_db)) :
    result = await db.execute(select(StockData))
    return result.scalars().all()