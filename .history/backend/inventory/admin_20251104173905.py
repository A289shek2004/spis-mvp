from django.contrib import admin
from .models import User, Supplier, Product, Batch, Sale, BatchPrediction

admin.site.register(User)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Batch)
admin.site.register(Sale)
admin.site.register(BatchPrediction)
