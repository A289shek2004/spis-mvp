from datetime import date, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from inventory.models import Batch, BatchPrediction
from inventory.models import RiskHistory

@api_view(['GET'])
def dashboard_summary(request):
    """
    Returns combined expiry + risk summary for dashboard
    """
    today = date.today()

    # 1. Expiry stats
    next_30 = today + timedelta(days=30)
    next_90 = today + timedelta(days=90)

    expiring_30 = Batch.objects.filter(expiry_date__lte=next_30).count()
    expiring_90 = Batch.objects.filter(expiry_date__lte=next_90).count()
    total_batches = Batch.objects.count()

    # 2. Risk stats
    high_risk = BatchPrediction.objects.filter(expiry_risk__gte=0.7).count()
    med_risk = BatchPrediction.objects.filter(expiry_risk__gte=0.3, expiry_risk__lt=0.7).count()
    low_risk = BatchPrediction.objects.filter(expiry_risk__lt=0.3).count()
    total_preds = BatchPrediction.objects.count()

    # 3. Low stock (optional)
    low_stock = Batch.objects.filter(quantity__lte=10).aggregate(total=Count('id'))['total']

    # 4. Combine results
    data = {
        "summary_date": str(today),
        "expiry_summary": {
            "total_batches": total_batches,
            "expiring_30_days": expiring_30,
            "expiring_90_days": expiring_90,
        },
        "risk_summary": {
            "total_predicted": total_preds,
            "high_risk": high_risk,
            "medium_risk": med_risk,
            "low_risk": low_risk,
        },
        "low_stock_batches": low_stock,
    }

    return Response(data)

@api_view(['GET'])
def risk_trend(request):
    """
    Returns risk summary for last N days (default 7)
    """
    days = int(request.query_params.get('days', 7))
    qs = RiskHistory.objects.order_by('-date')[:days]
    data = [
        {
            "date": rh.date,
            "high": rh.high_risk_count,
            "medium": rh.medium_risk_count,
            "low": rh.low_risk_count,
            "total": rh.total_predictions,
        }
        for rh in reversed(qs)  # reverse so earliest first
    ]
    return Response(data)
