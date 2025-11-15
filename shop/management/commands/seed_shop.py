from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = "Seed the database with dummy categories and products for the shop"

    def handle(self, *args, **options):
        categories_data = [
            {"name": "Gold", "slug": "gold"},
            {"name": "Diamond", "slug": "diamond"},
            {"name": "Gemstone", "slug": "gemstone"},
        ]

        categories = {}
        for data in categories_data:
            cat, _ = Category.objects.get_or_create(slug=data["slug"], defaults={"name": data["name"]})
            categories[data["slug"]] = cat

        products_data = [
            {"name": "Classic Gold Ring", "category": "gold", "price": 24999, "stock": 25, "metal_type": "Gold"},
            {"name": "Elegant Gold Necklace", "category": "gold", "price": 79999, "stock": 10, "metal_type": "Gold"},
            {"name": "Diamond Stud Earrings", "category": "diamond", "price": 55999, "stock": 15, "gemstone_type": "Diamond"},
            {"name": "Solitaire Diamond Ring", "category": "diamond", "price": 129999, "stock": 8, "gemstone_type": "Diamond"},
            {"name": "Emerald Pendant", "category": "gemstone", "price": 45999, "stock": 12, "gemstone_type": "Emerald", "metal_type": "Gold"},
            {"name": "Ruby Bracelet", "category": "gemstone", "price": 38999, "stock": 20, "gemstone_type": "Ruby", "metal_type": "Gold"},
            {"name": "Sapphire Necklace", "category": "gemstone", "price": 99999, "stock": 6, "gemstone_type": "Sapphire", "metal_type": "Gold"},
            {"name": "Minimal Gold Chain", "category": "gold", "price": 21999, "stock": 30, "metal_type": "Gold"},
        ]

        created_count = 0
        for pdata in products_data:
            category = categories[pdata.pop("category")]
            product, created = Product.objects.get_or_create(
                name=pdata["name"],
                defaults={
                    "category": category,
                    "description": "Beautifully crafted jewellery from Kanak.",
                    **pdata,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seed completed. Categories: {len(categories)}; New products: {created_count}"))


