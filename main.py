from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from datetime import datetime, timedelta
import models, schemas, database, os

app = FastAPI(title="IoT Device API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

models.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": f"Too many requests: {exc.detail}",
            "message": "Rate limit exceeded. Please try again later.",
        },
    )


@app.post("/register")
@limiter.limit("10/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    prev_user = db.query(models.User).filter(models.User.email == user.email).first()
    if prev_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = pwd_context.hash(user.password)
    db_user = models.User(name=user.name, email=user.email, password_hash=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserResponse.model_validate(db_user)


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token_data = {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=1)}
    return {
        "access_token": jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM),
        "token_type": "bearer",
    }


@app.post("/devices")
def create_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    db_device = models.Device(
        name=device.name, location=device.location, user_id=user.id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return schemas.DeviceResponse.model_validate(db_device)


@app.post("/telemetry")
def ingest_telemetry(
    telemetry: schemas.TelemetryData,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    device = (
        db.query(models.Device)
        .filter(
            models.Device.id == telemetry.device_id, models.Device.user_id == user.id
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    db_telemetry = models.Telemetry(device_id=telemetry.device_id, data=telemetry.data)
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return schemas.TelemetryResponse.model_validate(db_telemetry)


@app.get("/devices")
def list_devices(db: Session = Depends(get_db), user=Depends(get_current_user)):
    devices = db.query(models.Device).filter(models.Device.user_id == user.id).all()
    return [schemas.DeviceResponse.model_validate(device) for device in devices]


@app.get("/telemetry/{device_id}")
def get_device_telemetry(
    device_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    device = (
        db.query(models.Device)
        .filter(models.Device.id == device_id, models.Device.user_id == user.id)
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    telemetry = (
        db.query(models.Telemetry).filter(models.Telemetry.device_id == device_id).all()
    )
    return [schemas.TelemetryResponse.model_validate(data) for data in telemetry]


@app.put("/devices/{device_id}/state")
def update_device_state(
    device_id: int,
    state_update: schemas.DeviceStateUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    device = (
        db.query(models.Device)
        .filter(models.Device.id == device_id, models.Device.user_id == user.id)
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    device.status = state_update.status
    db.commit()
    db.refresh(device)
    return schemas.DeviceResponse.model_validate(device)


@app.get("/users/me", response_model=schemas.UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return schemas.UserResponse.model_validate(user)
