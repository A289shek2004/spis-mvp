import pytest
from django.utils import timezone
from inventory.models import Product, Batch, Supplier

@pytest.mark.django_db
def test_create_batch():
    p = Product.objects.create(name='P1')
    s = Supplier.objects.create(name='S1')
    b = Batch.objects.create(product=p, batch_no='B1', expiry_date=timezone.now().date(), quantity=10, supplier=s)
    assert b.product == p
    assert b.quantity == 10
    assert str(b).startswith('P1')
