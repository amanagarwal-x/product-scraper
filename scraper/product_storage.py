from product_scraper import Product
from abc import ABC, abstractmethod
from typing import List, Dict
import json
import redis


class Cache(ABC):
    '''
    Base class for product cache
    '''
    @abstractmethod
    def get(self, key: str) -> str:
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        pass


class RuntimeCache(Cache):
    def __init__(self):
        self.cache: Dict[str, str] = {}

    def get(self, key: str) -> str:
        return self.cache.get(key)

    def set(self, key: str, value: str):
        self.cache[key] = value


class RedisCache(Cache):
    def __init__(self):
        self.cache = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    def get(self, key: str) -> str:
        cached_price = self.cache.get(key)
        if cached_price is not None:
            cached_price = float(cached_price)
        return cached_price

    def set(self, key: str, value: str):
        self.cache.set(key, value)


class ProductStorage(ABC):
    '''
    Base class for persistent product storage
    '''
    
    def __init__(self):
        # self.cache = RuntimeCache()
        self.cache = RedisCache()

    @abstractmethod
    def save_products(self, products: List[Product]):
        pass


class FileStorage(ProductStorage):
    JSON_FILE_NAME = "products.json"

    def save_products(self, products: List[Product]):
        # Load existing data from the JSON file if it exists
        try:
            with open(self.JSON_FILE_NAME, "r") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        updated_products_count = 0

        for product in products:
            cached_price = self.cache.get(product.name)
            if cached_price != product.price:
                self.cache.set(product.name, product.price)
                updated_products_count += 1

                for data in existing_data:
                    if data["product_title"] == product.name:
                        data["product_price"] = product.price
                        break
                else:
                    existing_data.append({
                        "product_title": product.name,
                        "product_price": product.price,
                        "path_to_image": product.image_url
                    })

        with open(self.JSON_FILE_NAME, "w") as file:
            json.dump(existing_data, file, indent=2)

        return updated_products_count
