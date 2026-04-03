from celery import shared_task
from service.scraper.ebay import EbayScraper

from .models import Item, RecordedData, SourceName

@shared_task
def get_ebay_homepage_results():
    with EbayScraper(False) as scrapper:
        results = scrapper.get_homepage_products(5)
    
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