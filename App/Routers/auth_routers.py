# routers/auth_routers.py

from fastapi import APIRouter, Depends, HTTPException, Request
from App.Schemas.auth import UserCreate, UserResponse
from App.Models.user import User
from App.Models.stock import UserStock
from App.Config.security import hash_password, verify_password
from App.Config.database import get_db
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm
from App.Config.debs import get_current_user
from App.Schemas.auth import Token
from sqlalchemy.future import select
from App.Config.Oauth import get_oauth, SECRET_KEY, ALGORITHM


router = APIRouter(prefix="/auth", tags=["auth"])





ACCESS_TOKEN_EXPIRE_MINUTES = 30

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Use async query
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)  


    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}



@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Use async query with select()
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.get("/me")
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_active": current_user.is_active
    }




@router.get("/login/google")
async def login_google(request: Request, oauth=Depends(get_oauth)):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request, oauth=Depends(get_oauth)):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    # Extract user details
    email = user_info["email"]
    name = user_info.get("name", "")
    
    # Check if user exists in the database (implement this logic)
    # If not, create a new user

    return {"email": email, "name": name, "token": token}


@router.get("/portfolio")
async def portfolio_value(db: AsyncSession=Depends(get_db)) :
    result = await db.execute(
        select(
            UserStock.symbol,
            (UserStock.purchase_price * UserStock.quantity).label("total_value")
            )
    )
    value = result.all()
    portfolio = [{"symbol": stock[0], "total": stock[1]} for stock in value]
    stock_val = sum(stock["total"] for stock in portfolio)

    return {"total_portfolio_value": stock_val, "portfolio": portfolio}







