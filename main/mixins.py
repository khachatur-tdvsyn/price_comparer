from decimal import Decimal

from django.db.models import (
    F, Case, When, DecimalField, Subquery, OuterRef, Value, Q, Sum
)
from django.db.models.functions import Cast
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Currency
from .serializers import ItemSerializer

class CurrencyConverterMixin:
    price_field: str = 'amount'
    subquery: Subquery | None = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        target_currency = self.request.query_params.get('currency')

        if target_currency:
            try:
                # Verify currency exists
                target = Currency.objects.get(code=target_currency.upper())
                
                queryset = queryset.annotate(
                    converted_price_amount=Cast(
                        (self.subquery or F(self.price_field))* Decimal(str(target.exchange_rate)),
                        DecimalField(max_digits=10, decimal_places=2)
                    ),
                    target_currency_code=Value(target_currency)
                )
            except Currency.DoesNotExist:
                # If currency doesn't exist, just return normal queryset
                pass
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency'] = self.request.query_params.get('currency')
        return context

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='currency',
                description='Convert prices to this currency code',
                required=False,
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        """List items with optional currency conversion at database level"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='currency',
                description='Convert prices to this currency code',
                required=False,
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        """List items with optional currency conversion at database level"""
        return super().retrieve(request, *args, **kwargs)