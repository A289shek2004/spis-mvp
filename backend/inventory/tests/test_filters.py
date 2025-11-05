import pytest
from rest_framework.test import APIClient
from inventory.tests.factories import ProductFactory, BatchFactory

@pytest.mark.django_db
def test_search_products_by_name():
    ProductFactory(name="Paracetamol")
    ProductFactory(name="Amoxicillin")

    client = APIClient()
    response = client.get("/api/products/?search=Paracetamol")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Paracetamol"


@pytest.mark.django_db
def test_filter_batches_by_product():
    product1 = ProductFactory(name="Product A")
    product2 = ProductFactory(name="Product B")
    BatchFactory(product=product1)
    BatchFactory(product=product2)

    client = APIClient()
    response = client.get(f"/api/batches/?product={product1.id}")

    assert response.status_code == 200
    data = response.json()
    assert all(batch["product"]["name"] == "Product A" for batch in data)
