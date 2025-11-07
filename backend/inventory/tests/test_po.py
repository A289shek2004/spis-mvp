import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from inventory.models import Product, Batch, Supplier, Sale

@pytest.mark.django_db
def test_suggest_po_basic():
    supplier = Supplier.objects.create(name="SPO", lead_time_days=5)
    p = Product.objects.create(name="POProd")

    # current stock
    Batch.objects.create(
        product=p,
        batch_no="P1",
        expiry_date=timezone.now().date() + timedelta(days=100),
        quantity=20,
        supplier=supplier,
    )

    # sale history: 30 units in 30 days (≈ 1 per day)
    for i in range(30):
        b = Batch.objects.create(
            product=p,
            batch_no=f"P{i+10}",
            expiry_date=timezone.now().date() + timedelta(days=200),
            quantity=0,
            supplier=supplier,
        )
        Sale.objects.create(batch=b, qty_sold=1, price=10.0)

    client = APIClient()
    resp = client.post("/api/po/suggest/", {"product_id": p.id}, format="json")
    assert resp.status_code == 200
    data = resp.json()
    assert "reorder_qty" in data
    assert isinstance(data["reorder_qty"], int)
