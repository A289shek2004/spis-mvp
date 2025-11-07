from datetime import timedelta
from django.utils import timezone
from django.db import models
from inventory.models import Sale, Batch, Product

def suggest_reorder_for_product(product_id: int, safety_days: int = 7):
    """
    Compute reorder quantity suggestion for a product.
    Uses last 30 days of sales, current stock, and supplier lead time.
    """
    end = timezone.now()
    start = end - timedelta(days=30)

    # recent sales (last 30 days)
    sales_qs = Sale.objects.filter(batch__product_id=product_id, date__gte=start)
    total_sold = sum(s.qty_sold for s in sales_qs)
    avg_daily = total_sold / 30 if total_sold else 0.1  # fallback to small number

    # total stock across batches
    current_stock = (
        Batch.objects.filter(product_id=product_id)
        .aggregate(total_qty=models.Sum("quantity"))
        .get("total_qty")
        or 0
    )

    # use first batch’s supplier lead time (fallback 7 days)
    product = Product.objects.get(id=product_id)
    first_batch = product.batches.first()
    lead_time = (
        first_batch.supplier.lead_time_days
        if first_batch and first_batch.supplier
        else 7
    )

    # reorder qty = (lead_time + safety_days)*avg_daily – current_stock
    reorder_qty = max(
        0,
        int(lead_time * avg_daily + safety_days * avg_daily - current_stock),
    )

    return {
        "product_id": product_id,
        "avg_daily": avg_daily,
        "current_stock": int(current_stock),
        "lead_time": int(lead_time),
        "safety_days": int(safety_days),
        "reorder_qty": reorder_qty,
    }
