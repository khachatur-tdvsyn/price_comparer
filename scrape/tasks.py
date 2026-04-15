from decimal import Decimal

from django.conf import settings
from django.db import transaction

from celery import shared_task

from service.scraper.ebay import EbayScraper
from main.models import Item, ItemMedia, RecordedData, SourceName, Seller, Fee, Currency, CurrencyExchangeRateHistory
from .sessions import SessionManager
from service.scraper.currency import fetch_currencies_frankfurter

EBAY_SCRAPER_TYPE = 'ebay'

@shared_task
@transaction.atomic
def get_ebay_homepage_results():
    results = SessionManager.run_session(EBAY_SCRAPER_TYPE, 'get_homepage_products')
    
    return_ids = []

    for r in results:
        item = Item.objects.filter(external_id=r.external_id).first()
        if not item:
            item = Item(
                external_id=r.external_id,
                name=r.name,
                link=r.link,
                source=SourceName.EBAY
            )
            item.save()
        
        if r.image_url:
            media, created = ItemMedia.objects.get_or_create(
                item=item,
                url=r.image_url
            )

        recorded_data = RecordedData(
            item=item,
            currency=r.currency,
            price=r.price,
            discount=r.discount,
        )
        recorded_data.save()

        return_ids.append({'id': item.id, 'external_id': item.external_id})
    
    return return_ids

@shared_task
@transaction.atomic
def get_ebay_search_results(search_text, max_results):
   
    results = SessionManager.run_session(EBAY_SCRAPER_TYPE, 'search', search_text, max_results)

    return_ids = []
    for r in results:
        item = Item.objects.filter(external_id=r.external_id).first()
        if not item:
            item = Item(
                external_id=r.external_id,
                name=r.name,
                link=r.link,
                source=SourceName.EBAY
            )
            item.save()
        
        if r.image_url:
            media, created = ItemMedia.objects.get_or_create(
                item=item,
                url=r.image_url
            )

        recorded_data = RecordedData(
            item=item,
            currency=r.currency,
            price=r.price,
            discount=r.discount,
        )
        recorded_data.save()

        return_ids.append({'id': item.id, 'external_id': item.external_id})
    
    return return_ids

@shared_task
@transaction.atomic
def get_ebay_product_result(external_id):
    
    result = SessionManager.run_session(EBAY_SCRAPER_TYPE, 'get_product', external_id)
    print(result)
    
    item, created = Item.objects.get_or_create(external_id=external_id, source=SourceName.EBAY)
    item.name = result.name
    item.description = result.description
    item.options = result.options
    item.link= result.link
    
    # Set up item's seller
    seller, created = Seller.objects.get_or_create(
        name=result.seller_name, 
        profile_url=result.seller_link, 
        source=SourceName.EBAY
    )
    
    if created:
        item.seller = seller
    
    for u in result.image_urls:
        if u:
            media, created = ItemMedia.objects.get_or_create(
                item=item,
                url=u
            )
            print(f'Created media for {item}: {media.url=}')

    # Add recorded data for this item
    recorded_data = RecordedData(
        item=item,
        price=result.price,
        discount=result.discount,
        currency=result.currency
    )
    recorded_data.save()

    for f in result.fees:
        fee, created = Fee.objects.get_or_create(
            item=item,
            fee_type=int(f.fee_type),
            amount=f.amount or 0,
            currency=f.currency
        )
        fee.description = f.description
        fee.save()
        print('Added new fee')

    item.save()

    print('Product information updated successfully')
    return {
        'item_id': item.external_id,
        'external_id': getattr(item, 'id'),
    }

def fetch_and_update_currencies():
    """Fetch currencies and store history"""
    
    # Fetch from your data source
    success, currency_data = fetch_currencies_frankfurter()  # Your scraping logic

    if not success:
        print('Something went wrong', currency_data)
        return
    
    for data in currency_data:
        currency, created = Currency.objects.get_or_create(
            code=data['quote'],
            defaults={
                'exchange_rate': Decimal(data['rate'])
            }
        )
        
        # Store history if rate changed
        if not created and currency.exchange_rate != Decimal(data['rate']):
            CurrencyExchangeRateHistory.objects.create(
                currency=currency,
                exchange_rate=currency.exchange_rate  # Store old value
            )
        
        # Update current rate
        currency.exchange_rate = Decimal(data['rate'])
        currency.save()