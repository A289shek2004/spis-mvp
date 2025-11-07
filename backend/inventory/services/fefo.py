from datetime import date
from typing import Dict
from inventory.models import Batch

def generate_fefo_picklist(product_id: int, required_qty: int) -> Dict:
    """
    FEFO (First Expiry First Out) picklist generator.
    Returns batches sorted by earliest expiry,
    choosing from earliest first until the requested qty is fulfilled.
    """
    batches = Batch.objects.filter(
        product_id=product_id,
        quantity__gt=0
    ).order_by('expiry_date')

    remaining = required_qty
    picks = []

    for b in batches:
        if remaining <= 0:
            break
        take = min(b.quantity, remaining)
        picks.append({
            'batch_id': b.id,
            'batch_no': b.batch_no,
            'expiry_date': b.expiry_date,
            'pick_qty': take
        })
        remaining -= take

    return {
        'requested': required_qty,
        'fulfilled': required_qty - remaining,
        'picks': picks
    }
