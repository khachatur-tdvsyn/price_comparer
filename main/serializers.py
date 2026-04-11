from rest_framework import serializers
from .models import Seller, Tag, Item, Fee, RecordedData, ItemMedia


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'


class RecordedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordedData
        fields = '__all__'


class ItemMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemMedia
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['external_id', 'source', 'name', 'description', 'created', 'options', 'link', 'source', 'seller', 'tags']
        