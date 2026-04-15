import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import Currency
 
 
class Command(BaseCommand):
    help = 'Load currency metadata from JSON file'
 
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='currencies.json',
            help='Path to the currency JSON file',
        )
 
    def handle(self, *args, **options):
        file_path = options['file']
        
        # Try to find the file in different locations
        if not os.path.exists(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return
 
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            created_count = 0
            updated_count = 0
 
            for currency_data in data['currencies']:
                currency, created = Currency.objects.update_or_create(
                    code=currency_data['code'],
                    defaults={
                        'name': currency_data['name'],
                        'symbol': currency_data['symbol'],
                        'country_name': currency_data['country'],
                        'exchange_rate': 0  # Will be updated later
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
 
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully loaded currencies. '
                    f'Created: {created_count}, Updated: {updated_count}'
                )
            )
 
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON file: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading currencies: {str(e)}')
            )