from decimal import Decimal

from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import (
    F, Case, When, DecimalField, Subquery, OuterRef, Value, Q, Sum
)
from django.db.models.functions import Cast
from rest_framework import viewsets
from .models import Seller, Tag, Item, Fee, RecordedData, ItemMedia, Currency
from .serializers import (
    SellerSerializer,
    TagSerializer,
    ItemSerializer,
    FeeSerializer,
    RecordedDataSerializer,
    ItemMediaSerializer,
)
from .mixins import CurrencyConverterMixin
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ItemViewSet(CurrencyConverterMixin, viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('-created')
    serializer_class = ItemSerializer

    def _make_annotation(self, queryset, target_currency):
        if target_currency:
            target_currency = target_currency.upper()

            return queryset.annotate(
                price=Subquery(
                    RecordedData.objects.filter(item=OuterRef('pk')).values('price')[:1]
                ) * Subquery(
                    Currency.objects.filter(code=target_currency.upper()).values('exchange_rate')[:1]
                ),
                total_price=(
                    Subquery(
                    RecordedData.objects.filter(item=OuterRef('pk')).values('price')[:1]) + \
                        Sum(Fee.objects.filter(item=OuterRef('pk')).values('amount'))
                    ) * Subquery(
                        Currency.objects.filter(code=target_currency.upper()).values('exchange_rate')[:1]
                    ),
                currency=Value(target_currency)
            )
        else:
            return queryset.annotate(
                price=Subquery(
                    RecordedData.objects.filter(item=OuterRef('pk')).values('price')[:1]
                ),
                total_price=Subquery(
                    RecordedData.objects.filter(item=OuterRef('pk')).values('price')[:1]) + \
                        Sum(Fee.objects.filter(item=OuterRef('pk')).values('amount')),
                currency=Subquery(
                    RecordedData.objects.filter(item=OuterRef('pk')).values('currency')[:1]
                )
            )

    def get_queryset(self):
        queryset = self.queryset
        target_currency = self.request.query_params.get('currency')
        
        return self._make_annotation(queryset, target_currency)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='currency',
                description='Convert prices to this currency code',
                required=False,
            )
        ],
    )
    def retrieve(self, request, external_id=None, source=None):
        try:
            target_currency = self.request.query_params.get('currency')
            # Query using both fields
            instance = Item.objects.filter(external_id=external_id, source=source)
            annotated = self._make_annotation(instance, target_currency)

            if annotated.first() is None:
                raise Item.DoesNotExist

            serializer = self.get_serializer(annotated.first())
            return Response(serializer.data)
        
        except Item.DoesNotExist:
            raise NotFound(
                detail=f"Object with id={external_id} and source={source} not found."
            )


class FeeViewSet(CurrencyConverterMixin, viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    price_field = 'amount'


class RecordedDataViewSet(CurrencyConverterMixin, viewsets.ModelViewSet):
    queryset = RecordedData.objects.all()
    serializer_class = RecordedDataSerializer
    price_field = 'price'


class ItemMediaViewSet(viewsets.ModelViewSet):
    queryset = ItemMedia.objects.all()
    serializer_class = ItemMediaSerializer
