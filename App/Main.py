# App/Main.py

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession
from App.Config.database import get_db, init_db
from App.Services.stock_service import load_csv_to_db
from contextlib import asynccontextmanager
from App.Routers import stock_routers, auth_routers, feat_routers
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
import logging
from App.Scheduler import start_scheduler
from App.Config.database import SessionLocal



# ✅ Create FastAPI app with startup lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on app startup - Initializes DB and loads stock data."""
    async for db in get_db():
        await init_db()
        # await load_csv_to_db(db)
        break

    # ✅ START SCHEDULER HERE!
    app.state.db_session = SessionLocal
    start_scheduler(app)

    yield

app = FastAPI(lifespan=lifespan)

# ✅ Allow requests from your frontend (adjust the URL accordingly)
origins = [
    "http://localhost:3000",  # If running React locally
    "http://127.0.0.1:3000",  # Some setups use 127.0.0.1 instead of localhost
]

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # ✅ Allows all headers (including Authorization)
)

# ✅ Home route
@app.get("/")
def home():
    return {"message": "Welcome to the Stock Tracker API!"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logging.debug(f"🔍 Incoming Request: {request.method} {request.url}\nBody: {body.decode()}")
    response = await call_next(request)
    return response


# ✅ Register stock routes
app.include_router(stock_routers.stock_router)
app.include_router(stock_routers.user_router)
app.include_router(feat_routers.feat_router)
# ✅ Register watchlist stock routes


# ✅ User routes
app.include_router(auth_routers.router)

# ✅ Add middleware here (to FastAPI app, NOT APIRouter)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))




