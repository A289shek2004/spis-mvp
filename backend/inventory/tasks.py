from celery import shared_task
from datetime import date
from inventory.models import Batch, BatchPrediction

@shared_task
def compute_expiry_risks():
    """
    Computes expiry risk for each batch.
    Simple heuristic:
      risk = 1 - (days_to_expiry / 30)
      Clipped between 0 and 1
    """
    today = date.today()
    updated = 0

    for b in Batch.objects.filter(quantity__gt=0):
        days_to_expiry = (b.expiry_date - today).days
        # Normalize risk: close to expiry → higher risk
        risk = max(0.0, min(1.0, 1 - (days_to_expiry / 30)))

        pred, _ = BatchPrediction.objects.get_or_create(batch=b)
        pred.expiry_risk = risk
        pred.save()
        updated += 1

    return f"Updated expiry risk for {updated} batches"
