import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from inventory.models import Product, Batch, BatchPrediction

@pytest.mark.django_db
def test_dashboard_summary_view():
    client = APIClient()
    product = Product.objects.create(name="P1")

    b1 = Batch.objects.create(product=product, batch_no="B1", expiry_date=date.today() + timedelta(days=10), quantity=5)
    b2 = Batch.objects.create(product=product, batch_no="B2", expiry_date=date.today() + timedelta(days=60), quantity=20)

    BatchPrediction.objects.create(batch=b1, expiry_risk=0.8)
    BatchPrediction.objects.create(batch=b2, expiry_risk=0.2)

    resp = client.get("/api/reports/dashboard/")
    data = resp.json()

    assert resp.status_code == 200
    assert "expiry_summary" in data
    assert "risk_summary" in data
    assert data["risk_summary"]["high_risk"] == 1
