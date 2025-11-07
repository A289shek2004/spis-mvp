import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from inventory.models import RiskHistory

@pytest.mark.django_db
def test_risk_trend_api_returns_recent_data():
    for i in range(5):
        RiskHistory.objects.create(
            date=date.today() - timedelta(days=i),
            high_risk_count=i,
            medium_risk_count=i+1,
            low_risk_count=i+2,
            total_predictions=10
        )
    client = APIClient()
    resp = client.get("/api/reports/risk-trend/?days=3")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert "high" in data[0]
