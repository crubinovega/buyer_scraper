import requests
import time
from datetime import datetime, timedelta

BASE_URL = "https://gis.hcpafl.org/CommonServices/property"


def fetch_sales(page=1, pagesize=500, days_back=7):
    """Fetch sales from SalesSearchMod endpoint within a date range."""
    url = f"{BASE_URL}/search/SalesSearchMod"

    # SalesSearchMod does not support date filters directly.
    # We will filter dates AFTER fetching.
    params = {
        "prop": "0403,0400,0500,0501,0200,0408,0508,0111,0102,0100,0106",
        "stype": "q",
        "pagesize": pagesize,
        "page": page
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    sales = resp.json()

    # Filter by date range manually
    cutoff = datetime.now() - timedelta(days=days_back)
    filtered = []

    for r in sales:
        try:
            sale_date = datetime.strptime(r.get("saleDate"), "%Y-%m-%d")
        except:
            continue

        if sale_date >= cutoff:
            filtered.append(r)

    return filtered


def fetch_property_details(pin):
    """Fetch buyer and mailing address from ParcelData endpoint."""
    url = f"{BASE_URL}/search/ParcelData?pin={pin}"

    resp = requests.get(url)
    resp.raise_for_status()

    return resp.json()


def get_recent_cash_buyers(max_pages=1, days_back=7):
    """Main scraper function to assemble Tampa buyer list."""
    all_buyers = []

    for page in range(1, max_pages + 1):
        print(f"📄 Fetching sales page {page}...")
        sales = fetch_sales(page=page, days_back=days_back)

        if not sales:
            print("No more sales within date range.")
            break

        for sale in sales:
            pin = sale.get("pin")
            if not pin:
                continue

            sale_price = sale.get("salePrice")
            sale_date = sale.get("saleDate")
            address = sale.get("address")
            folio = sale.get("displayFolio")

            # Fetch buyer details
            details = fetch_property_details(pin)

            buyer_name = details.get("owner")
            mailing = details.get("mailingAddress", {})

            mailing_full = f"{mailing.get('addr1', '')} {mailing.get('addr2', '')}, {mailing.get('city', '')} {mailing.get('state', '')} {mailing.get('zip', '')}"

            result = {
                "buyer_name": buyer_name,
                "mailing_address": mailing_full.strip().replace("  ", " "),
                "site_address": details.get("siteAddress"),
                "sale_price": sale_price,
                "sale_date": sale_date,
                "folio": folio,
                "pin": pin
            }

            all_buyers.append(result)

            time.sleep(0.2)  # polite scraping delay

    return all_buyers
