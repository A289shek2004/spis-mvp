from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # placeholder to extend later (roles, metadata)
    pass

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    lead_time_days = models.IntegerField(default=7)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    unit = models.CharField(max_length=50, default='strip')
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

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

class Sale(models.Model):
    batch = models.ForeignKey(Batch, related_name='sales', on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    qty_sold = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pharmacist = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Sale {self.id} - {self.qty_sold} of {self.batch}"

class BatchPrediction(models.Model):
    batch = models.OneToOneField(Batch, on_delete=models.CASCADE, related_name='prediction')
    expiry_risk = models.FloatField(default=0.0)  # 0..1
    computed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pred for {self.batch} risk={self.expiry_risk}"
