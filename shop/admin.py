from django.contrib import admin
from .models import Category, SubCategory, Product, Cart, CartItem, Order, OrderItem, HomepageSection


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    fields = ("name", "slug", "image")


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug", "created_at")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    fields = ("category", "name", "slug", "image")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "subcategory", "category", "price", "stock")
    list_filter = ("subcategory__category", "subcategory")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("session_key", "created_at", "updated_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "paid", "created_at")
    inlines = [OrderItemInline]


@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    search_fields = ("title",)
    filter_horizontal = ("categories", "subcategories")
    prepopulated_fields = {"slug": ("title",)}
    fields = ("title", "slug", "is_active", "display_order", "categories", "subcategories")

