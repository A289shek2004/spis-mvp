from celery import shared_task
from datetime import date
from inventory.models import BatchPrediction, RiskHistory

@shared_task
def log_daily_risk_summary():
    """
    Count how many batches are high/medium/low risk
    and store in RiskHistory for today's date.
    """
    today = date.today()
    high = BatchPrediction.objects.filter(expiry_risk__gte=0.7).count()
    med = BatchPrediction.objects.filter(expiry_risk__gte=0.3, expiry_risk__lt=0.7).count()
    low = BatchPrediction.objects.filter(expiry_risk__lt=0.3).count()
    total = BatchPrediction.objects.count()

    obj, _ = RiskHistory.objects.update_or_create(
        date=today,
        defaults={
            'high_risk_count': high,
            'medium_risk_count': med,
            'low_risk_count': low,
            'total_predictions': total,
        }
    )
    return {"logged_date": str(today), "total_predictions": total}
