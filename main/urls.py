from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sellers', views.SellerViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'fees', views.FeeViewSet)
router.register(r'recorded-data', views.RecordedDataViewSet)
router.register(r'item-media', views.ItemMediaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]