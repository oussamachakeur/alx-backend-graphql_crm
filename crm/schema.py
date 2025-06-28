import re
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene import relay

# -------------------
# Object Types
# -------------------

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# -------------------
# CreateCustomer Mutation
# -------------------

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")

        if phone and not re.match(r'^(\+?\d{10,15}|(\d{3}-\d{3}-\d{4}))$', phone):
            raise Exception("Invalid phone format. Use +1234567890 or 123-456-7890")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

# -------------------
# BulkCreateCustomers Mutation
# -------------------

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created = []
        errors = []

        for i, entry in enumerate(input):
            try:
                name = entry["name"]
                email = entry["email"]
                phone = entry.get("phone")

                if Customer.objects.filter(email=email).exists():
                    raise Exception(f"Email already exists: {email}")

                if phone and not re.match(r'^(\+?\d{10,15}|(\d{3}-\d{3}-\d{4}))$', phone):
                    raise Exception(f"Invalid phone format for {name}: {phone}")

                cust = Customer(name=name, email=email, phone=phone)
                cust.save()
                created.append(cust)

            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")

        return BulkCreateCustomers(customers=created, errors=errors)

# -------------------
# CreateProduct Mutation
# -------------------

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be a positive number.")
        if stock < 0:
            raise Exception("Stock must be zero or a positive number.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

# -------------------
# CreateOrder Mutation
# -------------------

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer not found.")

        if not product_ids:
            raise Exception("At least one product ID must be provided.")

        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise Exception("Some product IDs are invalid.")

        total = sum([p.price for p in products])

        order = Order(customer=customer, total_amount=total)
        order.order_date = order_date if order_date else now()
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)

# -------------------
# Root Mutation & Query
# -------------------

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()





# Object Types with relay support
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)


class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(
        CustomerNode, filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductNode, filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(
        OrderNode, filterset_class=OrderFilter
    )