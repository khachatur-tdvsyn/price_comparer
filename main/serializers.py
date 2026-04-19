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
    converted_amount = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    target_currency = serializers.CharField(read_only=True)
    class Meta:
        model = Fee
        fields = '__all__'


class RecordedDataSerializer(serializers.ModelSerializer):
    converted_price_amount = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    target_currency_code = serializers.CharField(read_only=True)
    class Meta:
        model = RecordedData
        fields = '__all__'


class ItemMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemMedia
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    currency = serializers.CharField(read_only=True)
    class Meta:
        model = Item
        fields = ['id', 'external_id', 'source', 'name', 'price', 'currency', 'total_price', 'description', 'created', 'options', 'link', 'source', 'seller', 'tags']
        