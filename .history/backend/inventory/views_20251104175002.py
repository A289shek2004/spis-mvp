from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Batch, Sale, Supplier
from .serializers import ProductSerializer, BatchSerializer, SaleSerializer, SupplierSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.select_related('product','supplier').all()
    serializer_class = BatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product','supplier']
    search_fields = ['batch_no']

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        days = int(request.query_params.get('days', 30))
        threshold = date.today() + timedelta(days=days)
        qs = self.queryset.filter(expiry_date__lte=threshold).order_by('expiry_date')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('batch').all()
    serializer_class = SaleSerializer
