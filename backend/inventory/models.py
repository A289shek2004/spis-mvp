from django.db import models
from django.contrib.auth.models import AbstractUser

# 👤 Custom user (can add roles later)
class User(AbstractUser):
    pass


# 🏭 Supplier: companies who provide products
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    lead_time_days = models.IntegerField(default=7)  # average days for delivery

    def __str__(self):
        return self.name


# 💊 Product: medicine or item
class Product(models.Model):
    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    unit = models.CharField(max_length=50, default='strip')
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


# 📦 Batch: stock of each product with expiry
class Batch(models.Model):
    product = models.ForeignKey(Product, related_name='batches', on_delete=models.CASCADE)
    batch_no = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity = models.IntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=['expiry_date']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.batch_no}"


# 💰 Sale: tracks each sale
class Sale(models.Model):
    batch = models.ForeignKey(Batch, related_name='sales', on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    qty_sold = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pharmacist = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Sale {self.id} - {self.qty_sold} x {self.batch}"

class BatchPrediction(models.Model):
    batch = models.OneToOneField(Batch, on_delete=models.CASCADE, related_name='prediction')
    expiry_risk = models.FloatField(default=0.0)  # Range 0–1 (0 = safe, 1 = high risk)
    computed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.batch.batch_no} → risk {self.expiry_risk:.2f}"

class RiskHistory(models.Model):
    date = models.DateField(unique=True)
    high_risk_count = models.IntegerField(default=0)
    medium_risk_count = models.IntegerField(default=0)
    low_risk_count = models.IntegerField(default=0)
    total_predictions = models.IntegerField(default=0)

    def __str__(self):
        return f"RiskHistory {self.date}"
