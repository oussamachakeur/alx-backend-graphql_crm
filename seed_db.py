import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product

Customer.objects.create(name="Seeded", email="seeded@example.com")
Product.objects.create(name="Keyboard", price=50.0, stock=5)
Product.objects.create(name="Mouse", price=25.0, stock=20)
print("Database seeded.")
