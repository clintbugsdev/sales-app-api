from django.urls import path, include
from rest_framework.routers import DefaultRouter

from supplier import views

router = DefaultRouter()
router.register('suppliers', views.SupplierViewSet)

app_name = 'supplier'

urlpatterns = [
    path('', include(router.urls))
]
