import re


from .base import BaseShopScraper, ScrapedGeneralResult, ScrapedProduct, Fee, FeeType
# from base import BaseShopScraper, ScrapedGeneralResult, ScrapedProduct, Fee, FeeType
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional

from urllib.parse import quote

def get_discount(new_price, old_price):
    return (1 - new_price/old_price)*100


class EbayScraper(BaseShopScraper):
    base_url = 'https://www.ebay.com'

    items_list_selector = r'#s0-2-0-1-1-0-2-9-4-11-2-0-3-0-1-3-\@homepage-0-0-5\[0\]-\@row_xc_homepage_general_dweb_so-1-0-\@102690-featured-deals-2-7-4-1-11-1-0-4-2-0-5-1-0-list'
    ID_RE = re.compile(r'https:\/\/www\.ebay\.com\/itm\/(\d+)\??.*')
    PRICE_RE = re.compile(r'.?([\d\.]+)')
    DISCOUNT_RE = re.compile(r'(\d+)%')

    def _get_price(self, element: WebElement) -> Optional[Decimal]:
        comparing_text = element.text.replace(',', '')
        price_val = self.PRICE_RE.findall(comparing_text)
        return Decimal(price_val[0]) if len(price_val) > 0 else None
    
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

            id = self.ID_RE.match(str(link.get_attribute('href'))).group(1)
            print(id, start_price_val, discounted_price_val)

            results.append(ScrapedGeneralResult(
                external_id=id.group(1),
                image_url=image.get_attribute('src'),
                link=link.get_attribute('href'),
                name=name.text,
                price=start_price_val,
                discount=get_discount(discounted_price_val,start_price_val)
            ))
        
        return results
    
    def _get_discount_value(self, element: WebElement):
        if element:
            matches = self.DISCOUNT_RE.findall(element.text)
            return Decimal(matches[0]) if len(matches) > 0 else None
        return None
    
    def get_product(self, external_id):
        product_url = self.base_url + '/itm/{0}'.format(external_id)
        self.driver.get(product_url)

        name_item = self.driver.find_element(By.XPATH, '/html/body/div[2]/main/div[1]/div[1]/div[4]/div/div/div[2]/div/div/div[1]/h1/span')
        price_item = self.driver.find_element(By.XPATH, '/html/body/div[2]/main/div[1]/div[1]/div[4]/div/div/div[2]/div/div/div[3]/div/div/div/span[1]')
        
        # description_item = self.driver.find_element(By.XPATH, '/html/body/div[2]/main/div[1]/div[1]/div[5]/div[1]/div/div[2]/div/div/div[2]')
        description_item = self.driver.find_element(By.CSS_SELECTOR, '.vim.d-item-description')
        
        
        options_item = self.driver.find_element(By.CSS_SELECTOR, '.ux-layout-section-module-evo')

        option_items = options_item.find_elements(By.TAG_NAME, 'dl')
        options = dict()
        for i in option_items:
            key, value = i.find_element(By.TAG_NAME, 'dt'), i.find_element(By.TAG_NAME, 'dd')
            options[key.text] = value.text
        
        seller_item = self.driver.find_element(By.CSS_SELECTOR, '.x-store-information__store-name > a')
        # Fees section
        shipping_fee_item = self.driver.find_element(By.CSS_SELECTOR, '.ux-labels-values--shipping')

        discount_item = self._find_element_nowait(By.CSS_SELECTOR, '.x-price-transparency--discount')

        return ScrapedProduct(
            external_id=external_id,
            name=name_item.text,
            link=self.driver.current_url,
            price=self._get_price(price_item),
            description=description_item.get_attribute('innerHTML'),
            seller_name=seller_item.text,
            seller_link=seller_item.get_attribute('href'),
            options=options,
            fees=[
                Fee(FeeType.SHIPPING, self._get_price(shipping_fee_item))
            ],
            discount=self._get_discount_value(discount_item)
        )
        
        # Temp: get .vim x-breadcrumb 
    
    def search(self, query, max_results = 20):
        search_url = self.base_url + '/sch/i.html?_nkw={0}'
        self.driver.get(search_url.format(quote(query)))

        search_results_list = self.driver.find_element(By.CSS_SELECTOR, '.srp-results')
        items = search_results_list.find_elements(By.TAG_NAME, 'li')

        results = []
        for c, i in enumerate(items):
            if c >= max_results:
                break

            name_item = i.find_element(By.CSS_SELECTOR, '.s-card__title:nth-child(1)')
            price_item = i.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)')
            old_price_item = self._find_element_nowait(By.CSS_SELECTOR, 'div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(3)', i)
            link_item = i.find_element(By.CSS_SELECTOR, '.s-card__link')

            id = self.ID_RE.match(str(link_item.get_attribute('href')))

            print(price_item.text, old_price_item and old_price_item.text)
            price = self._get_price(price_item)
            old_price = self._get_price(old_price_item) if old_price_item else price

            results.append(ScrapedGeneralResult(
                external_id=id,
                image_url=None,
                name=name_item.text,
                price=price,
                discount=get_discount(price, old_price),
                link=link_item.get_attribute('href')
            ))

        return results
            

if __name__ == '__main__':
    with EbayScraper(False) as scrapper:
        results = scrapper.search('samsung', 5)
        with open('results.txt', 'w') as f:
            print(results)
            print(results, file=f, flush=True)
    