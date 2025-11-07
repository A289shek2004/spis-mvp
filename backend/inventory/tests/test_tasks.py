import pytest
from datetime import date, timedelta
from inventory.models import Product, Batch, BatchPrediction
from inventory.tasks import compute_expiry_risks

@pytest.mark.django_db
def test_compute_expiry_risks_creates_predictions():
    # Create test product and batches
    product = Product.objects.create(name="TestProduct")
    today = date.today()

    b1 = Batch.objects.create(product=product, batch_no="B1", expiry_date=today + timedelta(days=10), quantity=10)
    b2 = Batch.objects.create(product=product, batch_no="B2", expiry_date=today + timedelta(days=30), quantity=10)
    b3 = Batch.objects.create(product=product, batch_no="B3", expiry_date=today + timedelta(days=90), quantity=10)

    # Run the Celery task directly (synchronously)
    result = compute_expiry_risks()

    # Check task return message
    assert "Updated expiry risk" in result

    # Validate predictions created
    preds = BatchPrediction.objects.all()
    assert preds.count() == 3

    # Check risk values
    risks = [p.expiry_risk for p in preds]
    assert all(0.0 <= r <= 1.0 for r in risks)

    # Check ordering — earliest expiry → highest risk
    pred_b1 = BatchPrediction.objects.get(batch=b1)
    pred_b3 = BatchPrediction.objects.get(batch=b3)
    assert pred_b1.expiry_risk > pred_b3.expiry_risk

@pytest.mark.django_db
def test_compute_expiry_risks_async(monkeypatch):
    called = {"done": False}

    def fake_run():
        called["done"] = True
        return "ok"

    monkeypatch.setattr("inventory.tasks.compute_expiry_risks.run", fake_run)
    compute_expiry_risks.delay()
    assert called["done"] is True
