from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.product_list,
        name="product_list",
    ),

    path(
        "cart/",
        views.cart_detail,
        name="cart_detail",
    ),

    path(
        "cart/add/<int:product_id>/",
        views.cart_add,
        name="cart_add",
    ),

    path(
        "cart/update/<int:product_id>/",
        views.cart_update,
        name="cart_update",
    ),

    path(
        "cart/remove/<int:product_id>/",
        views.cart_remove,
        name="cart_remove",
    ),

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    path(
        "payment/callback/",
        views.payment_callback,
        name="payment_callback",
    ),

    path("delivery-fee/", views.delivery_fee_api, name="delivery_fee_api"),

    path(
        "<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
]