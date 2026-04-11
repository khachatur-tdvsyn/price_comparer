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


class RecordedDataViewSet(viewsets.ModelViewSet):
    queryset = RecordedData.objects.all()
    serializer_class = RecordedDataSerializer


class ItemMediaViewSet(viewsets.ModelViewSet):
    queryset = ItemMedia.objects.all()
    serializer_class = ItemMediaSerializer
