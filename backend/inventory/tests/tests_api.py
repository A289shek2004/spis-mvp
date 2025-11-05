import pytest
from rest_framework.test import APIClient
from inventory.models import Product

@pytest.mark.django_db
def test_product_list_api():
    # Setup test data
    Product.objects.create(name="Vitamin C", generic_name="Ascorbic Acid")
    Product.objects.create(name="Amoxicillin", generic_name="Antibiotic")

    client = APIClient()
    response = client.get("/api/products/")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Vitamin C" or data[1]["name"] == "Vitamin C"

@pytest.mark.django_db
def test_health_endpoint():
    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
