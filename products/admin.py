from django.contrib import admin
from .models import Brand, Category, Product, ProductSpecification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("is_active",)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 3
    fields = ("name", "value", "sort_order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "brand",
        "price",
        "stock_quantity",
        "is_active",
        "is_featured",
    )

    list_filter = (
        "category",
        "brand",
        "is_active",
        "is_featured",
    )

    search_fields = (
        "name",
        "sku",
        "description",
    )

    prepopulated_fields = {"slug": ("name",)}

    inlines = [ProductSpecificationInline]