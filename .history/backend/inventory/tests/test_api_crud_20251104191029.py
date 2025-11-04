import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from inventory.models import Product, Supplier, Batch

@pytest.mark.django_db
def test_create_and_list_products():
    client = APIClient()
    # Create
    res = client.post('/api/products/', {'name': 'Paracetamol'})
    assert res.status_code == 201
    # List
    res = client.get('/api/products/')
    assert res.status_code == 200
    assert any(p['name'] == 'Paracetamol' for p in res.json())

@pytest.mark.django_db
def test_expiring_batches_endpoint():
    p = Product.objects.create(name='Aspirin')
    s = Supplier.objects.create(name='Supplier1')
    Batch.objects.create(product=p, supplier=s, batch_no='B1', expiry_date=timezone.now().date(), quantity=10)
    client = APIClient()
    res = client.get('/api/batches/expiring/?days=30')
    assert res.status_code == 200
    assert len(res.json()) >= 1
