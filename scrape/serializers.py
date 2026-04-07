from rest_framework import serializers

class ScraperSearchSerializer(serializers.Serializer):
    search_text = serializers.CharField(required=True)
    max_results = serializers.IntegerField(default=20, required=False)