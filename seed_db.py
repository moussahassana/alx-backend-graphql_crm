import os
import django
from decimal import Decimal
from crm.models import Customer, Product, Order

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

# ——— Clear tables ———
Customer.objects.all().delete()
Product.objects.all().delete()
Order.objects.all().delete()

# ——— Customers ———
Customer.objects.bulk_create(
    [
        Customer(name="Alice", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol", email="carol@example.com"),
    ]
)

# ——— Products ———
Product.objects.bulk_create(
    [
        Product(name="Laptop", price=Decimal("999.99"), stock=10),
        Product(name="Phone", price=Decimal("499.99"), stock=20),
        Product(name="Mouse", price=Decimal("29.99"), stock=50),
    ]
)

# ——— One sample order ———
alice = Customer.objects.get(email="alice@example.com")
order = Order.objects.create(customer=alice, total_amount=Decimal("0.00"))
order.products.set(Product.objects.filter(name__in=["Laptop", "Mouse"]))
order.total_amount = sum(p.price for p in order.products.all())
order.save()

print("✅ Database seeded successfully.")
