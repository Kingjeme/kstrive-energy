from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from products.models import Product
from orders.models import Order, OrderItem
from orders.paystack import (
    initialize_transaction,
    verify_transaction,
)

from .cart import Cart
from .delivery import get_delivery_fee
from django.http import JsonResponse


def home(request):
    return render(request, "home.html")


def product_list(request):
    products = Product.objects.filter(
        is_active=True
    ).select_related(
        "category",
        "brand",
    )

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related(
            "category",
            "brand",
        ).prefetch_related(
            "specifications",
        ),
        slug=slug,
        is_active=True,
    )

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
        },
    )

def cart_detail(request):
    cart = Cart(request)

    return render(
        request,
        "store/checkout.html",
        {
            "cart": cart,
            "delivery_fee": 0,
            "total": cart.get_total_price(),
        },
    )


def cart_add(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    if request.method == "POST":
        try:
            quantity = int(
                request.POST.get("quantity", 1)
            )
        except (TypeError, ValueError):
            quantity = 1

        quantity = max(quantity, 1)

        if product.stock_quantity > 0:
            cart = Cart(request)
            cart.add(product, quantity)

    return redirect("cart_detail")


def cart_remove(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    if request.method == "POST":
        cart = Cart(request)
        cart.remove(product)

    return redirect("cart_detail")

def cart_update(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    if request.method == "POST":
        try:
            quantity = int(
                request.POST.get("quantity", 1)
            )
        except (TypeError, ValueError):
            quantity = 1

        quantity = max(quantity, 1)

        cart = Cart(request)
        cart.update(product, quantity)

    return redirect("cart_detail")

def delivery_fee_api(request):
    state = request.GET.get("state", "").strip()

    fee = get_delivery_fee(state)

    return JsonResponse({
        "delivery_fee": str(fee),
    })

def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect("product_list")

    # Convert cart items to a list so we can validate and reuse them.
    cart_items = list(cart)

    # Validate product availability before checkout.
    for item in cart_items:
        product = item["product"]
        requested_quantity = item["quantity"]

        if requested_quantity > product.stock_quantity:
            return render(
                request,
                "store/checkout.html",
                {
                    "cart": cart,
                    "error": (
                        f"Sorry, only {product.stock_quantity} unit(s) "
                        f"of {product.name} are currently available."
                    ),
                },
            )

        if product.stock_quantity <= 0:
            return render(
                request,
                "store/checkout.html",
                {
                    "cart": cart,
                    "error": (
                        f"Sorry, {product.name} is currently unavailable."
                    ),
                },
            )

    if request.method == "POST":
        customer_name = request.POST.get(
            "customer_name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()

        address = request.POST.get(
            "address",
            "",
        ).strip()

        city = request.POST.get(
            "city",
            "",
        ).strip()

        state = request.POST.get(
            "state",
            "",
        ).strip()

        if not all([
            customer_name,
            email,
            phone,
            address,
            city,
            state,
        ]):
            return render(
                request,
                "store/checkout.html",
                {
                    "cart": cart,
                    "error": (
                        "Please complete all required fields."
                    ),
                },
            )

        subtotal = cart.get_total_price()
        delivery_fee = get_delivery_fee(state)
        total = subtotal + delivery_fee

        order = Order.objects.create(
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                product_name=item["product"].name,
                product_sku=item["product"].sku,
                unit_price=item["price"],
                quantity=item["quantity"],
            )

        callback_url = request.build_absolute_uri(
            reverse("payment_callback")
        )

        try:
            payment_data = initialize_transaction(
                order,
                callback_url,
            )

        except ValueError as error:
            return render(
                request,
                "store/checkout.html",
                {
                    "cart": cart,
                    "error": str(error),
                },
            )

        return redirect(
            payment_data["authorization_url"]
        )

    return render(
        request,
        "store/checkout.html",
        {
            "cart": cart,
        },
    )

def payment_callback(request):
    reference = request.GET.get("reference")

    if not reference:
        return render(
            request,
            "store/payment_failed.html",
            {
                "error": "No payment reference was provided.",
            },
        )

    order = get_object_or_404(
        Order,
        order_number=reference,
    )

    # Prevent the same successful payment from reducing stock twice.
    if order.payment_status == "paid":
        return render(
            request,
            "store/payment_success.html",
            {
                "order": order,
            },
        )

    try:
        payment_data = verify_transaction(reference)

    except ValueError as error:
        return render(
            request,
            "store/payment_failed.html",
            {
                "error": str(error),
                "order": order,
            },
        )

    payment_status = payment_data.get("status")
    payment_amount = payment_data.get("amount")
    payment_currency = payment_data.get("currency")
    payment_reference = payment_data.get("reference")

    expected_amount = int(order.total * 100)

    if payment_status != "success":
        return render(
            request,
            "store/payment_failed.html",
            {
                "error": "Payment was not successful.",
                "order": order,
            },
        )

    if payment_reference != order.order_number:
        return render(
            request,
            "store/payment_failed.html",
            {
                "error": "Payment reference does not match this order.",
                "order": order,
            },
        )

    if payment_currency != "NGN":
        return render(
            request,
            "store/payment_failed.html",
            {
                "error": "Invalid payment currency.",
                "order": order,
            },
        )

    if payment_amount != expected_amount:
        return render(
            request,
            "store/payment_failed.html",
            {
                "error": "Payment amount does not match the order total.",
                "order": order,
            },
        )

    # Payment is verified. Now update payment status and stock together.
    with transaction.atomic():
        locked_order = Order.objects.select_for_update().get(
            id=order.id
        )

        # Double-check inside the transaction.
        if locked_order.payment_status == "paid":
            order = locked_order

        else:
            for item in locked_order.items.select_related("product"):
                product = item.product

                if product is None:
                    continue

                # Lock this product row before changing its stock.
                locked_product = Product.objects.select_for_update().get(
                    id=product.id
                )

                if locked_product.stock_quantity < item.quantity:
                    return render(
                        request,
                        "store/payment_failed.html",
                        {
                            "error": (
                                f"Payment was successful, but there is "
                                f"not enough available stock for "
                                f"{item.product_name}. Please contact "
                                f"KSTRIVE ENERGY."
                            ),
                            "order": locked_order,
                        },
                    )

                locked_product.stock_quantity -= item.quantity

                locked_product.save(
                    update_fields=[
                        "stock_quantity",
                        "updated_at",
                    ]
                )

            locked_order.payment_status = "paid"
            locked_order.status = "confirmed"

            locked_order.save(
                update_fields=[
                    "payment_status",
                    "status",
                    "updated_at",
                ]
            )

            order = locked_order

    # Clear the cart only after successful payment and stock update.
    Cart(request).clear()

    return render(
        request,
        "store/payment_success.html",
        {
            "order": order,
        },
    )