from decimal import Decimal

from products.models import Product


CART_SESSION_ID = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)

        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}

        self.cart = cart

    def add(self, product, quantity=1):
        if product.stock_quantity <= 0:
            return

        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(product.price),
            }

        self.cart[product_id]["quantity"] += quantity

        if self.cart[product_id]["quantity"] > product.stock_quantity:
            self.cart[product_id]["quantity"] = product.stock_quantity

        self.save()

    def update(self, product, quantity):
        product_id = str(product.id)

        if quantity <= 0:
            self.remove(product)
            return

        if quantity > product.stock_quantity:
            quantity = product.stock_quantity

        if product_id in self.cart:
            self.cart[product_id]["quantity"] = quantity
            self.save()

    def remove(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()

        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True,
        )

        products_by_id = {
            str(product.id): product
            for product in products
        }

        for product_id, item in self.cart.items():
            product = products_by_id.get(product_id)

            if product is None:
                continue

            item["product"] = product
            item["price"] = Decimal(str(product.price))
            item["total_price"] = (
                item["price"] * item["quantity"]
            )

            yield item

    def __len__(self):
        return sum(
            item["quantity"]
            for item in self.cart.values()
        )

    def get_total_price(self):
        return sum(
            item["total_price"]
            for item in self
        )

    def clear(self):
        del self.session[CART_SESSION_ID]
        self.session.modified = True