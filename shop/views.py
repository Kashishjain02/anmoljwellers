from typing import Optional
from urllib.parse import quote_plus
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse
from .models import Category, Product, Cart, CartItem, Order, OrderItem, HomepageSection


def _get_cart(request: HttpRequest) -> Cart:
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def home(request: HttpRequest) -> HttpResponse:
    # Load featured categories/subcategories from HomepageSection
    featured = (
        HomepageSection.objects.filter(is_active=True)
        .prefetch_related("categories", "subcategories")
        .order_by("display_order")
    )
    # Build sections: each active HomepageSection becomes a section
    sections: list[dict] = []
    if featured.exists():
        for sec in featured:
            sec_categories = Category.objects.filter(
                Q(featured_in_sections=sec) |
                Q(subcategories__featured_in_sections=sec)
            ).distinct().order_by("name")
            sections.append({
                "title": sec.title,
                "categories": sec_categories,
            })
    else:
        sections.append({
            "title": "Shop by Category",
            "categories": Category.objects.all(),
        })
    new_arrivals = Product.objects.order_by("-created_at")[:8]
    best_sellers = Product.objects.order_by("-stock")[:8]
    collections = [
        {"title": "Gold Classics", "slug": "gold", "cta": "Shop Gold"},
        {"title": "Diamond Elegance", "slug": "diamond", "cta": "Shop Diamonds"},
        {"title": "Gemstone Luxe", "slug": "gemstone", "cta": "Shop Gemstones"},
    ]
    return render(
        request,
        "shop/home.html",
        {
            "sections": sections,
            "new_arrivals": new_arrivals,
            "best_sellers": best_sellers,
            "collections": collections,
        },
    )


def catalog(request: HttpRequest, category_slug: Optional[str] = None) -> HttpResponse:
    category = None
    products = Product.objects.all().select_related("subcategory", "subcategory__category")
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(subcategory__category=category)
    categories = Category.objects.all()
    return render(
        request,
        "shop/catalog.html",
        {"category": category, "categories": categories, "products": products},
    )


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    return render(request, "shop/product_detail.html", {"product": product})


@require_POST
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()

    # return redirect("cart")
    product_link = request.build_absolute_uri(reverse("product_detail", args=[product.slug]))
    message = (
        f"Hello! I'm interested in the {product.name} (ID: {product.id}). "
        f"Here is the product link: {product_link}"
    )
    whatsapp_url = f"https://wa.me/918226066667?text={quote_plus(message)}"
    return redirect(whatsapp_url)


def cart_view(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    return render(request, "shop/cart.html", {"cart": cart})


@require_POST
def update_cart_item(request: HttpRequest, item_id: int) -> HttpResponse:
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get("action")
    if action == "inc":
        item.quantity += 1
        item.save()
    elif action == "dec":
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == "remove":
        item.delete()
    return redirect("cart")


def checkout(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    if request.method == "POST":
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        email = request.POST.get("email", "")
        address = request.POST.get("address", "")
        city = request.POST.get("city", "")
        postal_code = request.POST.get("postal_code", "")
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            city=city,
            postal_code=postal_code,
            paid=True,
        )
        for item in cart.items.select_related("product"):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
            )
        cart.items.all().delete()
        return render(request, "shop/thank_you.html", {"order": order})
    return render(request, "shop/checkout.html", {"cart": cart})


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category") or ""
    min_price = request.GET.get("min_price") or ""
    max_price = request.GET.get("max_price") or ""
    metal = request.GET.get("metal") or ""
    gemstone = request.GET.get("gemstone") or ""
    sort = request.GET.get("sort") or ""

    products = Product.objects.all().select_related("subcategory", "subcategory__category")
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(subcategory__category__name__icontains=query)
            | Q(gemstone_type__icontains=query)
            | Q(metal_type__icontains=query)
        )
    if category_slug:
        products = products.filter(subcategory__category__slug=category_slug)
    if min_price.isdigit():
        products = products.filter(price__gte=min_price)
    if max_price.isdigit():
        products = products.filter(price__lte=max_price)
    if metal:
        products = products.filter(metal_type__icontains=metal)
    if gemstone:
        products = products.filter(gemstone_type__icontains=gemstone)

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "new":
        products = products.order_by("-created_at")

    categories = Category.objects.all()
    return render(
        request,
        "shop/search.html",
        {
            "query": query,
            "products": products,
            "categories": categories,
            "active": {
                "category": category_slug,
                "min_price": min_price,
                "max_price": max_price,
                "metal": metal,
                "gemstone": gemstone,
                "sort": sort,
            },
        },
    )


# Create your views here.
