from django.conf import settings
from django.db import transaction

from celery import shared_task

from service.scraper.ebay import EbayScraper
from main.models import Item, RecordedData, SourceName, Seller, Fee
from .sessions import SessionManager

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

    # Add recorded data for this item
    recorded_data = RecordedData(
        item=item,
        price=result.price,
        discount=result.discount,
        currency=result.currency
    )
    recorded_data.save()

    for f in result.fees:
        if f.amount:
            fee, created = Fee.objects.get_or_create(
                item=item,
                fee_type=int(f.fee_type),
                amount=f.amount,
                currency=f.currency
            )
            print('Added new fee')
        else:
            print('There is no amount in', f)

    item.save()

    print('Product information updated successfully')
    return {
        'item_id': item.external_id,
        'external_id': getattr(item, 'id'),
    }


    