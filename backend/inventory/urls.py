# E:\medi_spis\spis-mvp\backend\inventory\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, BatchViewSet, SupplierViewSet, SaleViewSet, fefo_picklist
from .views import expiry_summary, fefo_picklist
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory import views, views_reports
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'batches', BatchViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'sales', SaleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('fefo/picklist/', fefo_picklist, name='fefo-picklist'),
    path('reports/expiry_summary/', expiry_summary, name='expiry-summary'),
    path('reports/dashboard/', views_reports.dashboard_summary),
    path('reports/risk-trend/', views_reports.risk_trend),
    path("transactions/sales/", views.create_sale, name="create-sale"),
    path("po/suggest/", views.suggest_po, name="suggest-po"),
    # path("debug/crash/", views.crash_test),
    
    
]
