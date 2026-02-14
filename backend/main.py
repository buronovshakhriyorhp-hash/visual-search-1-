import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import shutil
import os
import io
import logging
import uvicorn

from search_engine import get_search_engine
from config import get_settings

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

@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):
    try:
        MAX_FILE_SIZE = 10 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        await file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
        
        logger.info(f"Received search request for {file.filename}")
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
