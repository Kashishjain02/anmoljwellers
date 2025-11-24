from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class SubCategory(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    image = models.ImageField(upload_to="subcategories/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "SubCategories"
        unique_together = ["category", "name"]  # Same subcategory name can exist in different categories

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.category.name} - {self.name}"


class Product(TimeStampedModel):
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    gemstone_type = models.CharField(max_length=120, blank=True)
    metal_type = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            self.slug = base
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @property
    def category(self):
        """Get the parent category through the subcategory"""
        if not self.subcategory:
            return None
        return self.subcategory.category


class Cart(TimeStampedModel):
    session_key = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return f"Cart {self.session_key}"

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.items.all())


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self) -> float:
        return float(self.product.price) * self.quantity


class Order(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    paid = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.first_name} {self.last_name}"

    @property
    def total(self) -> float:
        return sum(item.total_price for item in self.items.all())


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self) -> float:
        return float(self.price) * self.quantity


class HomepageSection(TimeStampedModel):
    """Admin-configurable homepage sections.

    Admins can choose a label, and pick specific categories and/or subcategories
    to show on the homepage. The template/view can read these to render tiles.
    """

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="featured_in_sections")
    subcategories = models.ManyToManyField(SubCategory, blank=True, related_name="featured_in_sections")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
