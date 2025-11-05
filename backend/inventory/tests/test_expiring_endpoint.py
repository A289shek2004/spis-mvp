import pytest
from rest_framework.test import APIClient
from datetime import timedelta
from django.utils import timezone
from inventory.tests.factories import BatchFactory

@pytest.mark.django_db
def test_expiring_batches_endpoint():
    today = timezone.now().date()
    # Batch expiring tomorrow
    BatchFactory(expiry_date=today + timedelta(days=1))
    # Batch expiring in 60 days (should NOT show up for ?days=30)
    BatchFactory(expiry_date=today + timedelta(days=60))

    client = APIClient()
    response = client.get("/api/batches/expiring/?days=30")

    assert response.status_code == 200
    data = response.json()

    # Expect only the soon-expiring one
    assert len(data) == 1
    assert data[0]["batch_no"].startswith("B")
    assert (timezone.datetime.strptime(data[0]["expiry_date"], "%Y-%m-%d").date() - today).days <= 30
