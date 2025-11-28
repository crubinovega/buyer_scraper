from app.scrapers.hillsborough.scraper import get_recent_cash_buyers

buyers = get_recent_cash_buyers(max_pages=1, days_back=365)
print(buyers[:5])
