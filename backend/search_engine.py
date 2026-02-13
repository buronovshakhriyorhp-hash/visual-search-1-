import time
import logging
import asyncio
import base64
import httpx
from functools import lru_cache

from config import get_settings
from exceptions import ExternalAPIError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()

class VisualSearchEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VisualSearchEngine, cls).__new__(cls)
        return cls._instance

    async def _upload_to_imgbb(self, image_bytes: bytes, client: httpx.AsyncClient) -> str:
        try:
            payload = {
                "key": settings.IMGBB_API_KEY,
                "image": base64.b64encode(image_bytes).decode('utf-8'),
            }
            
            response = await client.post("https://api.imgbb.com/1/upload", data=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()['data']['url']
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ImgBB upload failed: {e.response.text}")
            raise ExternalAPIError(f"ImgBB returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"ImgBB upload failed: {e}")
            raise ExternalAPIError(f"ImgBB upload failed: {e}")

    async def _search_serpapi(self, image_url: str, client: httpx.AsyncClient) -> dict:
        try:
            logger.info(f"Searching SerpApi with URL: {image_url}")
            params = {
                "engine": "google_lens",
                "api_key": settings.SERPAPI_KEY,
                "url": image_url,
                "hl": "en", 
                "country": "us"
            }
            
            response = await client.get("https://serpapi.com/search", params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"SerpApi search failed: {e.response.text}")
            raise ExternalAPIError(f"SerpApi returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"SerpApi connection failed: {e}")
            raise ExternalAPIError(str(e))

    async def perform_search(self, image_bytes: bytes):
        start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            try:
                img_url = await self._upload_to_imgbb(image_bytes, client)
                
                search_results = await self._search_serpapi(img_url, client)
                
                visual_matches = []
                if "visual_matches" in search_results:
                    for match in search_results["visual_matches"]:
                        visual_matches.append({
                            "title": match.get("title", "No Title"),
                            "link": match.get("link", "#"),
                            "price": match.get("price", {}).get("value", "N/A") if isinstance(match.get("price"), dict) else match.get("price", "N/A"),
                            "thumbnail": match.get("thumbnail", ""),
                            "source": match.get("source", "Google Lens")
                        })
                
                latency = time.time() - start_time
                logger.info(f"Search completed in {latency:.2f}s")
                
                return {
                    "visual_matches": visual_matches,
                    "latency": f"{latency:.2f}s",
                    "status_messages": [] if visual_matches else ["No visual matches found."]
                }
                
            except ExternalAPIError as e:
                logger.error(f"Search process failed: {e}")
                return {
                    "visual_matches": [],
                    "latency": f"{time.time() - start_time:.2f}s",
                    "status_messages": [str(e)],
                    "error": str(e)
                }
            except Exception as e:
                logger.exception("Unexpected error")
                return {
                    "visual_matches": [],
                    "latency": f"{time.time() - start_time:.2f}s",
                    "status_messages": ["Internal Server Error"],
                    "error": str(e)
                }

@lru_cache()
def get_search_engine():
    return VisualSearchEngine()
