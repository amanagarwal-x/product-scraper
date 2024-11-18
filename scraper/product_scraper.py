from fastapi import HTTPException
from typing import Optional, List
from pydantic import BaseModel
from typing import Optional, List, Union
import os
import requests
from bs4 import BeautifulSoup
import time


class Product(BaseModel):
    name: str
    image_url: str
    price: Union[float, None]


class ProductScraper:
    '''
    Main class to scrape products from a website
    '''
    RETRY_COUNT = int(os.getenv("RETRY_COUNT", 3))
    RETRY_TIMEOUT = int(os.getenv("RETRY_TIMEOUT", 2))
    
    def __init__(self, base_url: str, headers: dict, proxy: Optional[str] = None):
        self.base_url = base_url
        self.headers = headers
        self.proxy = proxy

    def _get_page_soup(self, page: int) -> BeautifulSoup:
        url = f"{self.base_url}{page}/"
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        for _ in range(self.RETRY_COUNT):  # Simple retry mechanism
            try:
                response = requests.get(url, headers=self.headers, proxies=proxies)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "lxml")
                    return soup
            except requests.RequestException:
                time.sleep(self.RETRY_TIMEOUT)
        raise HTTPException(status_code=500, detail="Failed to scrape page")


    def _parse_products(self, soup) -> List[Product]:
        products = []
        for product_card in soup.select(".product-inner"):
            name = product_card.select_one(".addtocart-buynow-btn").find("a")['data-title'].strip()
            image_url = product_card.select_one(".mf-product-thumbnail").a["href"]
            price = product_card.select_one(".woocommerce-Price-amount")
            if price:
                price = price.bdi.get_text(strip=True)
                price = self.__parse_price(price)
            products.append(Product(name=name, image_url=image_url, price=price))
        return products

    def scrape_page(self, page: int) -> List[Product]:
        soup = self._get_page_soup(page)
        products = self._parse_products(soup)
        return products
    
    def get_last_page_number(self) -> int:
        soup = self._get_page_soup(1)
        page_numbers_list = soup.select_one(".page-numbers")
        page_numbers = page_numbers_list.find_all("a")
        page_numbers = [int(link.text) for link in page_numbers if link.text.isdigit()]
        return page_numbers[-1]

    @staticmethod
    def __parse_price(price: str) -> float:
        price = price.replace("₹", "").replace(",", "")
        return float(price)

