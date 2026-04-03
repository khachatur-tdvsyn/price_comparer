from django.shortcuts import render
from rest_framework import viewsets
from .models import Seller, Tag, Item, Fee, RecordedData, ItemMedia
from .serializers import (
    SellerSerializer,
    TagSerializer,
    ItemSerializer,
    FeeSerializer,
    RecordedDataSerializer,
    ItemMediaSerializer,
)


class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer


class RecordedDataViewSet(viewsets.ModelViewSet):
    queryset = RecordedData.objects.all()
    serializer_class = RecordedDataSerializer


class ItemMediaViewSet(viewsets.ModelViewSet):
    queryset = ItemMedia.objects.all()
    serializer_class = ItemMediaSerializer
