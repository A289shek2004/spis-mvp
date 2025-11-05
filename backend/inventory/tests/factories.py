import factory
from django.utils import timezone
from inventory.models import Product, Supplier, Batch

class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.Sequence(lambda n: f"Supplier {n}")
    lead_time_days = 7


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    generic_name = factory.Sequence(lambda n: f"Generic {n}")
    unit = "strip"
    category = "general"


class BatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Batch

    product = factory.SubFactory(ProductFactory)
    supplier = factory.SubFactory(SupplierFactory)
    batch_no = factory.Sequence(lambda n: f"B{n:03d}")
    expiry_date = factory.LazyFunction(lambda: timezone.now().date())
    quantity = 10
    purchase_price = 5.0
