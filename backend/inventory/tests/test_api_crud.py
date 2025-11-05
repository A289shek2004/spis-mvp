import pytest
from rest_framework.test import APIClient
from inventory.models import Product, Supplier, Batch
from django.utils import timezone
from django.urls import reverse
@pytest.mark.django_db
def test_create_product():
    client = APIClient()
    response = client.post('/api/products/', {'name': 'TestProduct'})
    assert response.status_code == 201
    assert Product.objects.filter(name='TestProduct').exists()

@pytest.mark.django_db
def test_list_products():
    Product.objects.create(name='P1')
    Product.objects.create(name='P2')
    client = APIClient()
    response = client.get('/api/products/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

@pytest.mark.django_db
def test_batch_expiring_filter():
    supplier = Supplier.objects.create(name='S1')
    p = Product.objects.create(name='Paracetamol')
    Batch.objects.create(product=p, batch_no='B001',
                         expiry_date=timezone.now().date(), quantity=5, supplier=supplier)
    client = APIClient()
    response = client.get('/api/batches/expiring/?days=30')
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert result[0]['batch_no'] == 'B001'

@pytest.mark.django_db
def test_product_crud():
    client = APIClient()

    # CREATE
    response = client.post('/api/products/', {'name': 'Amoxicillin', 'generic_name': 'Amox', 'unit': 'strip'})
    assert response.status_code == 201
    pid = response.data['id']

    # READ
    get_response = client.get(f'/api/products/{pid}/')
    assert get_response.status_code == 200
    assert get_response.data['name'] == 'Amoxicillin'

    # UPDATE
    patch = client.patch(f'/api/products/{pid}/', {'category': 'Antibiotic'}, format='json')
    assert patch.status_code == 200
    assert patch.data['category'] == 'Antibiotic'

    # DELETE
    delete_response = client.delete(f'/api/products/{pid}/')
    assert delete_response.status_code == 204
    assert Product.objects.count() == 0


@pytest.mark.django_db
def test_batch_filter_and_expiring_action():
    client = APIClient()
    supplier = Supplier.objects.create(name='Supplier A')
    prod = Product.objects.create(name='Paracetamol')
    today = timezone.now().date()

    Batch.objects.create(product=prod, batch_no='B1', expiry_date=today, quantity=10, supplier=supplier)
    Batch.objects.create(product=prod, batch_no='B2', expiry_date=today.replace(year=today.year + 1), quantity=20, supplier=supplier)

    # list filter
    resp = client.get(f'/api/batches/?product={prod.id}')
    assert resp.status_code == 200
    assert len(resp.data) == 2

    # expiring filter
    exp = client.get('/api/batches/expiring/?days=10')
    assert exp.status_code == 200
    assert any(b['batch_no'] == 'B1' for b in exp.data)

