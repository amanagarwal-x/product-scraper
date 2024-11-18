from abc import ABC, abstractmethod
import logging


class NotificationChannel(ABC):
    '''
    Base class for notification channels
    '''
    
    @abstractmethod
    def notify(self, product_count: int, input_pages: int, last_page: int, scrape_time: float):
        pass
    

class ConsoleNotificationChannel(NotificationChannel):

    def notify(self, product_count: int, input_pages: int, last_page: int, scrape_time: float):
        logging.info(f"Scraping completed. {product_count} products were scraped from {input_pages}/{last_page} pages and updated in {scrape_time} seconds.")