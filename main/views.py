from decimal import Decimal
from datetime import datetime

from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import (
    F, Case, When, DecimalField, Subquery, OuterRef, Value, Q, Sum, Prefetch
)
from django.db.models.functions import Cast
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Seller, Tag, Item, Fee, RecordedData, ItemMedia, Currency
from .serializers import (
    SellerSerializer,
    TagSerializer,
    ItemSerializer,
    ItemHistorySerializer,
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

    def get_serializer_class(self):
        if self.action in ('history',):
            return ItemHistorySerializer
        else:
            return ItemSerializer

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
    
    def _get_prices_of_item(self, item_queryset, from_time, to_time):
        return item_queryset.annotate(
            history=Subquery(
                RecordedData.objects.filter(item=OuterRef('pk'), recorded_at__gte=from_time, recorded_at__lte=to_time).values('id')
            ),
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
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='external_id',
                required=True,
            ),
            OpenApiParameter(
                name='source',
                required=True,
            ),
            OpenApiParameter(
                name='currency',
                required=False,
            ),
            OpenApiParameter(
                name='from_time',
                required=False,
            ),
            OpenApiParameter(
                name='to_time',
                required=False,
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request, *args, **kwargs):
        query_params = self.request.query_params 
        external_id = query_params.get('external_id')
        source = query_params.get('source')

        from_time, to_time = query_params.get('from_time'), query_params.get('to_time')
        currency = query_params.get('currency')
        

        from_time = datetime.fromisoformat(from_time) if from_time else datetime.fromtimestamp(0)
        to_time = datetime.fromisoformat(to_time) if to_time else datetime.now()

        if from_time > to_time:
            print('Swaping bigger from_time and smaller to_time parameters')
            from_time, to_time = to_time, from_time

        try:
            instance = Item.objects.filter(external_id=external_id, source=source)

            history_queryset = RecordedData.objects.filter(
                item=instance.first(),
                recorded_at__gte=from_time,
                recorded_at__lte=to_time
            )
            
            if currency:
                history_queryset = self.annotate_converted_currency(history_queryset, currency, 'price')

            prefetch = Prefetch(
                'records',
                queryset=history_queryset,
                to_attr='history'
            )

            queryset = instance.prefetch_related(prefetch)


            if queryset.first() is None:
                raise Item.DoesNotExist

            serializer = self.get_serializer(queryset.first())
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
