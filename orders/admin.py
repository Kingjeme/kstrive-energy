from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    fields = (
        "product",
        "product_name",
        "product_sku",
        "unit_price",
        "quantity",
        "total_price",
    )

    readonly_fields = (
        "product",
        "product_name",
        "product_sku",
        "unit_price",
        "quantity",
        "total_price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "customer_name",
        "phone",
        "total",
        "status",
        "payment_status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "state",
        "created_at",
    )

    search_fields = (
        "order_number",
        "customer_name",
        "email",
        "phone",
        "payment_reference",
    )

    readonly_fields = (
        "order_number",
        "subtotal",
        "total",
        "payment_reference",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "status",
                    "payment_status",
                    "payment_reference",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Customer Information",
            {
                "fields": (
                    "customer_name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Delivery Information",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                )
            },
        ),
        (
            "Payment Summary",
            {
                "fields": (
                    "subtotal",
                    "delivery_fee",
                    "total",
                )
            },
        ),
    )

    inlines = [
        OrderItemInline,
    ]

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    list_per_page = 25