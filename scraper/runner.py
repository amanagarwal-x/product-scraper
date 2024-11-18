from notification import ConsoleNotificationChannel
from product_scraper import ProductScraper, Product
from product_storage import FileStorage
from settings import STATIC_TOKEN, BASE_TARGET_URL
from fastapi import FastAPI, Query, Header, HTTPException
from typing import Optional, List
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

notification_channels = {
    "console": ConsoleNotificationChannel()
}
storage = FileStorage()

def authenticate(token: str):
    if token != STATIC_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/scrape_products", response_model=List[Product])
async def scrape_products(
    pages: int = Query(1, gt=0),
    proxy: Optional[str] = Query(None),
    token: Optional[str] = Header(None)
):
    '''
    GET API to scrape products
    '''
    authenticate(token)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    start_time = time.time()
    scraper = ProductScraper(BASE_TARGET_URL, headers, proxy)
    all_products = []

    last_page_number = scraper.get_last_page_number()
    pages = min(pages, last_page_number)
    for page in range(1, pages + 1):
        products = scraper.scrape_page(page)
        all_products.extend(products)
        logger.debug(f"Scraped page {page}/{last_page_number} with {len(products)} products")

    updated_products_count = storage.save_products(all_products)
    scrape_time = round(time.time() - start_time, 2)
    
    for notification_channel in notification_channels.values():
        notification_channel.notify(len(all_products), pages, last_page_number, scrape_time)

    return all_products
