# backend/inventory/views.py
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Batch, Sale, Supplier
from .serializers import ProductSerializer, BatchSerializer, SaleSerializer, SupplierSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
from inventory.services.fefo import generate_fefo_picklist

import pytest
from datetime import date, timedelta
from inventory.models import Product, Batch, Sale
from rest_framework.test import APIClient

from rest_framework.decorators import api_view
# from rest_framework.response import Response
from django.db.models import Sum
from datetime import date, timedelta
from .models import Batch
from django.db import transaction
from inventory.services.po import suggest_reorder_for_product
from django.http import JsonResponse

# 🧾 Products
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'generic_name']
    filterset_fields = ['category']


# 🏭 Suppliers
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


# 📦 Batches (with expiring filter)
class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.select_related('product', 'supplier').all()
    serializer_class = BatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'supplier']
    search_fields = ['batch_no']

    # Custom action — list expiring batches
    @action(detail=False, methods=['get'])
    def expiring(self, request):
        try:
            days = int(request.query_params.get('days', 30))
        except (TypeError, ValueError):
            days = 30
        threshold = date.today() + timedelta(days=days)
        qs = self.queryset.filter(expiry_date__lte=threshold).order_by('expiry_date')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# 💰 Sales
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('batch').all()
    serializer_class = SaleSerializer


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def fefo_picklist(request):
    product_id = int(request.query_params.get('product_id'))
    qty = int(request.query_params.get('qty', 1))
    result = generate_fefo_picklist(product_id, qty)
    return Response(result)



@pytest.mark.django_db
def test_expiry_summary_api():
    product = Product.objects.create(name="Vitamin C")

    today = date.today()
    # 2 batches expiring soon, 1 later
    Batch.objects.create(product=product, batch_no="B1", expiry_date=today + timedelta(days=10), quantity=10, purchase_price=5)
    Batch.objects.create(product=product, batch_no="B2", expiry_date=today + timedelta(days=20), quantity=15, purchase_price=7)
    Batch.objects.create(product=product, batch_no="B3", expiry_date=today + timedelta(days=90), quantity=50, purchase_price=12)

    client = APIClient()
    response = client.get("/api/reports/expiry_summary/?days=30")

    assert response.status_code == 200
    data = response.json()
    assert data["total_batches"] == 2
    assert data["total_quantity"] == 25


@api_view(['GET'])
def expiry_summary(request):
    days = int(request.query_params.get('days', 30))
    threshold = date.today() + timedelta(days=days)
    qs = Batch.objects.filter(expiry_date__lte=threshold)
    total_batches = qs.count()
    total_qty = qs.aggregate(total=Sum('quantity'))['total'] or 0
    return Response({'days': days, 'total_batches': total_batches, 'total_quantity': total_qty})

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # uncomment this line if you enable auth later
def create_sale(request):
    """
    Expected body:
    {
      "product_id": <int>,
      "qty": <int>,
      "price": <float, optional>,
      "batch_id": <int, optional>
    }
    """
    data = request.data
    try:
        qty = int(data.get('qty', 0))
        product_id = int(data.get('product_id'))
    except (TypeError, ValueError):
        return Response({'error': 'product_id and qty required and must be integers'}, status=status.HTTP_400_BAD_REQUEST)

    price = float(data.get('price', 0.0))
    batch_id = data.get('batch_id')

    if qty <= 0:
        return Response({'error': 'qty must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

    # Use transaction to lock affected rows
    with transaction.atomic():
        # if client specified a batch, use that first
        if batch_id:
            try:
                batch = Batch.objects.select_for_update().get(id=batch_id)
            except Batch.DoesNotExist:
                return Response({'error': 'batch not found'}, status=status.HTTP_404_NOT_FOUND)
            if batch.quantity < qty:
                return Response({'error': 'Insufficient quantity in selected batch'}, status=status.HTTP_400_BAD_REQUEST)
            batch.quantity -= qty
            batch.save()
            sale = Sale.objects.create(batch=batch, qty_sold=qty, price=price)
            return Response({'status': 'ok', 'sale_id': sale.id}, status=status.HTTP_201_CREATED)

        # otherwise allocate across FEFO picklist
        picks = generate_fefo_picklist(product_id=product_id, required_qty=qty)['picks']
        total_available = sum(p['pick_qty'] for p in picks)
        if total_available < qty:
            return Response({'error': 'Insufficient total stock'}, status=status.HTTP_400_BAD_REQUEST)

        created_sales = []
        for p in picks:
            b = Batch.objects.select_for_update().get(id=p['batch_id'])
            take = p['pick_qty']
            # double-check available (might be changed by concurrent tx)
            if b.quantity < take:
                return Response({'error': 'Concurrent modification — try again'}, status=status.HTTP_409_CONFLICT)
            b.quantity -= take
            b.save()
            s = Sale.objects.create(batch=b, qty_sold=take, price=price)
            created_sales.append(s.id)

    return Response({'status': 'ok', 'sales': created_sales}, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def suggest_po(request):
    """
    body: { "product_id": int, "safety_stock_days": int (optional) }
    """
    try:
        product_id = int(request.data["product_id"])
    except (KeyError, ValueError):
        return Response({"error": "product_id required"}, status=status.HTTP_400_BAD_REQUEST)

    safety_days = int(request.data.get("safety_stock_days", 7))
    result = suggest_reorder_for_product(product_id=product_id, safety_days=safety_days)
    return Response(result)



# def crash_test(request):
#     1 / 0  # force ZeroDivisionError
#     return JsonResponse({"status": "ok"})