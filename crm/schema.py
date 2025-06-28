import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from decimal import Decimal
from .models import Customer, Product, Order


# ---------- GraphQL TYPES ----------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


# ---------- QUERIES ----------
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")


# ---------- MUTATIONS ----------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if phone:
            import re
            if not re.fullmatch(r"^\+?\d{10,15}$|^\d{3}-\d{3}-\d{4}$", phone):
                raise Exception("Invalid phone format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customers):
        created, errors = [], []
        with transaction.atomic():
            for c in customers:
                try:
                    if Customer.objects.filter(email=c.email).exists():
                        raise Exception(f"Email {c.email} already exists")
                    if c.phone:
                        import re
                        if not re.fullmatch(r"^\+?\d{10,15}$|^\d{3}-\d{3}-\d{4}$", c.phone):
                            raise Exception(f"Invalid phone format for {c.email}")
                    created.append(
                        Customer.objects.create(name=c.name, email=c.email, phone=c.phone)
                    )
                except Exception as exc:
                    errors.append(str(exc))
        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")
        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


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
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product must be selected")

        products, total = [], Decimal("0.00")
        for pid in product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
                total += product.price
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {pid}")

        order_data = dict(customer=customer, total_amount=total)
        if order_date:
            order_data["order_date"] = order_date

        order = Order.objects.create(**order_data)
        order.products.set(products)
        return CreateOrder(order=order)


# ---------- ROOT MUTATION ----------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# ---------- EXPORT ----------
schema = graphene.Schema(query=Query, mutation=Mutation)