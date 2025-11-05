import pytest
from django.utils import timezone
from inventory.models import Product, Supplier, Batch

@pytest.mark.django_db
def test_create_batch():
    # Create sample data
    supplier = Supplier.objects.create(name="ABC Pharma", lead_time_days=5)
    product = Product.objects.create(name="Paracetamol", generic_name="Acetaminophen")
    
    batch = Batch.objects.create(
        product=product,
        batch_no="B001",
        expiry_date=timezone.now().date(),
        quantity=50,
        supplier=supplier
    )

    # Assertions (checks)
    assert batch.product.name == "Paracetamol"
    assert batch.quantity == 50
    assert batch.supplier.name == "ABC Pharma"
