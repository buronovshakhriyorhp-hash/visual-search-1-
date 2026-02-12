import asyncio
import os
from search_engine import get_search_engine
from config import get_settings

# Mock settings if needed, or rely on .env loading
settings = get_settings()

async def test_search():
    print(f"Testing with keys: ImgBB={'OK' if settings.IMGBB_API_KEY else 'MISSING'}, SerpApi={'OK' if settings.SERPAPI_KEY else 'MISSING'}")
    
    engine = get_search_engine()
    
    # Use a real image if exists, or create a dummy one
    test_image = "test_image.jpg"
    if not os.path.exists(test_image):
        print("Creating dummy test image...")
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(test_image)
    
    print(f"Uploading {test_image}...")
    try:
        url = await engine._upload_to_imgbb(test_image)
        print(f"ImgBB URL: {url}")
        
        print("Searching SerpApi...")
        results = await engine._search_serpapi(url)
        print("SerpApi Keys returned:", results.keys())
        
        if "visual_matches" in results:
            print(f"Found {len(results['visual_matches'])} visual matches.")
            print("First match:", results['visual_matches'][0] if results['visual_matches'] else "None")
        else:
            print("WARNING: 'visual_matches' key NOT found in response.")
            print("Full Response subset:", str(results)[:500])
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
