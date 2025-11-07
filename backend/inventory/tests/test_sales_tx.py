import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from inventory.models import Product, Batch, Supplier

@pytest.mark.django_db
def test_create_sale_allocates_fefo():
    supplier = Supplier.objects.create(name="S1")
    p = Product.objects.create(name="ProdTX")
    today = date.today()
    # Batches order: earliest expiry first
    b1 = Batch.objects.create(product=p, batch_no="T1", expiry_date=today + timedelta(days=5), quantity=5, supplier=supplier)
    b2 = Batch.objects.create(product=p, batch_no="T2", expiry_date=today + timedelta(days=15), quantity=10, supplier=supplier)
    client = APIClient()

    resp = client.post("/api/transactions/sales/", {"product_id": p.id, "qty": 7}, format='json')
    assert resp.status_code == 201, f"unexpected status {resp.status_code} {resp.content}"
    data = resp.json()
    # at least one sale created (could be two)
    assert "sales" in data or "sale_id" in data

    # Check quantities reduced
    b1.refresh_from_db()
    b2.refresh_from_db()
    assert b1.quantity == 0
    assert b2.quantity == 8

@pytest.mark.django_db
def test_create_sale_insufficient_stock():
    p = Product.objects.create(name="ProdIns")
    Batch.objects.create(product=p, batch_no="I1", expiry_date=date.today() + timedelta(days=5), quantity=2)
    client = APIClient()
    resp = client.post("/api/transactions/sales/", {"product_id": p.id, "qty": 5}, format='json')
    assert resp.status_code == 400
    assert resp.json().get("error") == "Insufficient total stock"
