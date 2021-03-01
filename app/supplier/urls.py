from django.urls import path, include
from rest_framework.routers import DefaultRouter

from supplier import views

router = DefaultRouter()
router.register('suppliers', views.SupplierViewSet)
router.register('purchase-orders',
                views.PurchaseOrderViewSet,
                basename='purchase-order')

app_name = 'supplier'

urlpatterns = [
    path('', include(router.urls)),
]
