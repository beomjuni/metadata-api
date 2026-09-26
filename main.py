from fastapi import FastAPI, HTTPException, Query
import httpx
from bs4 import BeautifulSoup

app = FastAPI(title="URL Metadata Extractor API")

@app.get("/v1/extract")
async def extract_metadata(url: str = Query(..., description="Target URL to extract")):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch URL")
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        def get_meta(prop_name, attr="property"):
            tag = soup.find("meta", {attr: prop_name})
            return tag["content"] if tag and tag.has_attr("content") else None

        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 20]
        
        return {
            "status": "success",
            "url": url,
            "data": {
                "title": get_meta("og:title") or (soup.title.string if soup.title else None),
                "description": get_meta("og:description") or get_meta("description", attr="name"),
                "image": get_meta("og:image"),
                "text_preview": " ".join(paragraphs[:5])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
