# backend/inventory/serializers.py
from rest_framework import serializers
from .models import Product, Batch, Sale, Supplier

# 🏭 Supplier Serializer
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

# 💊 Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# 📦 Batch Serializer (includes product and supplier)
class BatchSerializer(serializers.ModelSerializer):
    # show nested info when reading
    product = ProductSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)

    # allow writing by IDs when creating
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='product',
        queryset=Product.objects.all()
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='supplier',
        queryset=Supplier.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Batch
        fields = [
            'id',
            'product',
            'product_id',
            'batch_no',
            'expiry_date',
            'quantity',
            'purchase_price',
            'supplier',
            'supplier_id'
        ]

# 💰 Sale Serializer
class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ('date',)
