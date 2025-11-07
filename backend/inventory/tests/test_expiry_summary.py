import pytest
from datetime import date, timedelta
from inventory.models import Product, Batch
from rest_framework.test import APIClient

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
