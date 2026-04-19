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
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('-created')
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Note: total_price returns null if there is no information about fee.
        return queryset.annotate(
            price=Subquery(
                RecordedData.objects.filter(item=OuterRef('pk')).values('price')[:1])
            ,
            total_price=Subquery(
                RecordedData.objects.filter(item=OuterRef('pk')).values('price')[:1]) + \
                    Sum(Fee.objects.filter(item=OuterRef('pk')).values('amount'))
            ,
            currency=Subquery(
                RecordedData.objects.filter(item=OuterRef('pk')).values('currency')[:1]
            ),
        )

    def retrieve(self, request, external_id=None, source=None):
        try:
            # Query using both fields
            instance = Item.objects.get(external_id=external_id, source=source)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        except Item.DoesNotExist:
            raise NotFound(
                detail=f"Object with id={external_id} and source={source} not found."
            )


class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        target_currency = self.request.query_params.get('currency')

        if target_currency:
            try:
                # Verify currency exists
                target = Currency.objects.get(code=target_currency.upper())
                
                queryset = queryset.annotate(
                    converted_amount=Cast(
                        F('amount') * Decimal(str(target.exchange_rate)),
                        DecimalField(max_digits=10, decimal_places=2)
                    ),
                    target_currency=Value(target_currency)
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
        responses=ItemSerializer(many=True),
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
        responses=ItemSerializer(many=True),
    )
    def retrieve(self, request, *args, **kwargs):
        """List items with optional currency conversion at database level"""
        return super().retrieve(request, *args, **kwargs)


class RecordedDataViewSet(viewsets.ModelViewSet):
    queryset = RecordedData.objects.all()
    serializer_class = RecordedDataSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        target_currency = self.request.query_params.get('currency')

        if target_currency:
            try:
                # Verify currency exists
                target = Currency.objects.get(code=target_currency.upper())
                
                queryset = queryset.annotate(
                    converted_price_amount=Cast(
                        F('price') * Decimal(str(target.exchange_rate)),
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
        responses=ItemSerializer(many=True),
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
        responses=ItemSerializer(many=True),
    )
    def retrieve(self, request, *args, **kwargs):
        """List items with optional currency conversion at database level"""
        return super().retrieve(request, *args, **kwargs)


class ItemMediaViewSet(viewsets.ModelViewSet):
    queryset = ItemMedia.objects.all()
    serializer_class = ItemMediaSerializer
