from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EbayScraperViewSet
 
# Create a router and register the viewset
router = DefaultRouter()
router.register(r'ebay', EbayScraperViewSet, basename='ebay')
 
urlpatterns = [
    path('', include(router.urls)),
]
 