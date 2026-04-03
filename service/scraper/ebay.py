import re

from .base import BaseShopScraper, ScrapedGeneralResult
# from .base import BaseShopScraper, ScrapedGeneralResult
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional


class EbayScraper(BaseShopScraper):
    base_url = 'https://www.ebay.com'

    items_list_selector = r'#s0-2-0-1-1-0-2-9-4-11-2-0-3-0-1-3-\@homepage-0-0-5\[0\]-\@row_xc_homepage_general_dweb_so-1-0-\@102690-featured-deals-2-7-4-1-11-1-0-4-2-0-5-1-0-list'
    
    ID_RE = re.compile(r'https:\/\/www\.ebay\.com\/itm\/(\d+)')
    PRICE_RE = re.compile(r'.?([\d\.]+)')

    def _get_price(self, element: WebElement) -> Optional[Decimal]:
        comparing_text = element.text.replace(',', '')
        price_val = self.PRICE_RE.findall(comparing_text)
        return Decimal(price_val[0])
    
    def get_homepage_products(self, max_results=20):
        item_list = self.wait_for(
            (
                By.CSS_SELECTOR,
                self.items_list_selector,
            )
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", item_list)
        
        items = item_list.find_elements(By.CSS_SELECTOR, 'li')
        results = []
        for c, item in enumerate(items):
            if c >= max_results:
                break

            image = item.find_element(By.CSS_SELECTOR, 'article > div:nth-child(1) > a:nth-child(2) > img:nth-child(1)')
            link = item.find_element(By.CSS_SELECTOR, 'article > a')
            name = item.find_element(By.CSS_SELECTOR, 'article > a > div:nth-child(1) > span:nth-child(1)')
            
            price_item = item.find_element(By.CSS_SELECTOR, 'article > a > div:nth-child(1) > div:nth-child(2) > span:nth-child(1)')

            
            start_price = self._find_element_nowait(By.CSS_SELECTOR, 'del:nth-child(2)', price_item)
            discounted_price = self._find_element_nowait(By.CSS_SELECTOR, 'ins:nth-child(1)', price_item)

            if start_price or discounted_price:
                discounted_price_val = self._get_price(discounted_price)
                start_price_val = self._get_price(start_price)
            else:
                discounted_price_val = start_price_val = self._get_price(price_item)

            id = self.ID_RE.match(str(link.get_attribute('href')))
            print(id, start_price_val, discounted_price_val)

            results.append(ScrapedGeneralResult(
                external_id=id.group(1),
                image_url=image.get_attribute('src'),
                link=link.get_attribute('href'),
                name=name.text,
                price=start_price_val,
                discount=(1 - discounted_price_val/start_price_val)*100
            ))
        
        return results
    
    def get_product(self, external_id):
        ...
    
    def search(self, query, max_results = 20):
        ...

if __name__ == '__main__':
    with EbayScraper(False) as scrapper:
        results = scrapper.get_homepage_products()
        with open('results.txt', 'w') as f:
            print(results, file=f, flush=True)
    