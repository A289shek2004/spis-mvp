from rest_framework import serializers
from .models import Product, Batch, Sale, Supplier, BatchPrediction

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class BatchSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True, source='product', queryset=Product.objects.all())
    
    class Meta:
        model = Batch
        fields = ['id','product','product_id','batch_no','expiry_date','quantity','purchase_price','supplier']

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ('date',)

class BatchPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchPrediction
        fields = '__all__'
