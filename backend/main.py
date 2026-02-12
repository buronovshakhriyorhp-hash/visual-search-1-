import sys
import os

# Add current directory to sys.path for Vercel imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import logging
import uvicorn

from search_engine import get_search_engine
from config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
# Ensure uploads directory exists (Disabled for Vercel)
# os.makedirs("uploads", exist_ok=True)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": f"{settings.APP_NAME} is running!"}

@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):
    try:
        # Validate file size (Max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        await file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
            
        # Validate content type
        if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
             raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, and WEBP are allowed.")

        # Save uploaded file safely
        # os.makedirs("uploads", exist_ok=True)
        # file_location = f"uploads/{file.filename}"
        # with open(file_location, "wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Received search request for {file.filename}")
        
        # Read file into memory for Vercel/Serverless compatibility
        file_bytes = await file.read()
        
        engine = get_search_engine()
        results = await engine.perform_search(file_bytes)
        
        # Check for error in results (handled gracefully in engine, but we can check status)
        if "error" in results:
            logger.error(f"Engine reported error: {results['error']}")
            # We still return results to show error message in UI if needed, 
            # or raise 500 if it's critical. 
            # Current frontend expects 'visual_matches' which is present even on error (empty list).
        
        return results
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=settings.DEBUG)
