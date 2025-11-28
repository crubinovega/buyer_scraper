from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from app.config import API_KEY
from app.scrapers.hillsborough.portfolio import lookup_hillsborough_portfolio
from app.scrapers.hillsborough.scraper import get_recent_cash_buyers


app = FastAPI(
    title="Foreclosure Scraper API",
    description="Multi-market scraper API (starting with Hillsborough County)",
    version="1.0"
)

def validate_api_key(key: str):
    if not key or key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key.")

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "service": "Hillsborough Buyer Scraper"}

@app.get("/scrape/hillsborough")
def scrape_hillsborough(key: str, days: int = 7, pages: int = 1):
    # API Key validation
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key.")

    try:
        results = get_recent_cash_buyers(max_pages=pages, days_back=days)
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/portfolio/hillsborough")
def run_hillsborough_portfolio(buyer_name: str, key: str = Query(None)):
    validate_api_key(key)
    try:
        data = lookup_hillsborough_portfolio(buyer_name)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"status": "ok", "message": "Foreclosure Scraper API running"}
