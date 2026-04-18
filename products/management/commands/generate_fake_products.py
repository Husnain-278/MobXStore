from faker import Faker
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
import random

import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from products.models import Brand, Category, Mobile, MobileImage, MobileSpecification, Specification


class Command(BaseCommand):
    help = "Generate fake brand/mobile data with images from assets/."

    def __init__(self):
        super().__init__()
        self._upload_cache = {}

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=12,
            help="Total number of fake mobiles to generate (default: 12).",
        )
        parser.add_argument(
            "--category-count",
            type=int,
            default=6,
            help="Total number of categories to ensure (default: 6).",
        )

    def _get_faker(self):
        """Do not import Faker here; user requested manual Faker import."""
        faker_cls = globals().get("Faker")
        if faker_cls is None:
            raise CommandError(
                "Faker is not imported in this command file. "
                "Please add 'from faker import Faker' yourself."
            )
        return faker_cls()

    def _group_assets_by_brand(self):
        assets_path = Path(settings.BASE_DIR) / "assets"
        if not assets_path.exists():
            raise CommandError(f"Assets folder not found: {assets_path}")

        allowed_ext = {".webp", ".jpg", ".jpeg", ".png"}
        image_groups = defaultdict(list)

        for image_path in sorted(assets_path.iterdir()):
            if not image_path.is_file() or image_path.suffix.lower() not in allowed_ext:
                continue

            stem = image_path.stem.lower()
            brand_token = stem.split("-")[0].strip()
            if not brand_token:
                continue

            image_groups[brand_token].append(image_path)

        if not image_groups:
            raise CommandError("No usable image files found in assets/.")

        return image_groups

    def _save_brand_logo(self, brand, logo_path):
        brand.logo = self._upload_image(logo_path, folder="brands")
        brand.save(update_fields=["logo"])

    def _save_mobile_primary(self, mobile, image_path):
        mobile.primary_image = self._upload_image(image_path, folder="mobiles/primary")
        mobile.save(update_fields=["primary_image"])

    def _upload_image(self, image_path, folder):
        cache_key = f"{folder}:{str(image_path)}"
        if cache_key in self._upload_cache:
            return self._upload_cache[cache_key]

        with image_path.open("rb") as file_obj:
            upload_result = cloudinary.uploader.upload(
                file_obj,
                folder=folder,
                resource_type="image",
                use_filename=True,
                unique_filename=True,
                overwrite=False,
            )

        public_id = upload_result["public_id"]
        self._upload_cache[cache_key] = public_id
        return public_id

    def _build_categories(self, fake, category_count):
        base_categories = ["Budget Phones", "Midrange Phones", "Flagship Phones"]
        categories = [
            Category.objects.get_or_create(name=name, defaults={"slug": slugify(name)})[0]
            for name in base_categories
        ]

        category_count = max(category_count, len(base_categories))
        while len(categories) < category_count:
            name = f"{fake.word().title()} {fake.word().title()}"
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)},
            )
            if created:
                categories.append(category)

        return categories

    @transaction.atomic
    def handle(self, *args, **options):
        fake = self._get_faker()
        count = max(1, options["count"])
        category_count = max(1, options["category_count"])
        image_groups = self._group_assets_by_brand()

        categories = self._build_categories(fake, category_count)

        spec_names = ["RAM", "Storage", "Battery", "Display", "Chipset"]
        specs = {
            name: Specification.objects.get_or_create(name=name)[0]
            for name in spec_names
        }

        brands = sorted(image_groups.keys())
        per_brand = count // len(brands)
        remainder = count % len(brands)

        created_mobile_count = 0

        for index, brand_key in enumerate(brands):
            brand_images = image_groups[brand_key]
            if not brand_images:
                continue

            target_count = per_brand + (1 if index < remainder else 0)
            if target_count == 0:
                continue

            brand_name = brand_key.capitalize()
            brand, _ = Brand.objects.get_or_create(name=brand_name)

            if not brand.logo:
                self._save_brand_logo(brand, brand_images[0])

            for _ in range(target_count):
                chosen_primary = random.choice(brand_images)

                product_name = (
                    f"{brand_name} {fake.word().title()} {fake.random_int(min=100, max=999)}"
                )

                mobile = Mobile.objects.create(
                    name=product_name,
                    brand=brand,
                    category=random.choice(categories),
                    slug="",
                    price=Decimal(
                        str(
                            fake.pydecimal(
                                left_digits=4,
                                right_digits=2,
                                positive=True,
                                min_value=199,
                                max_value=2999,
                            )
                        )
                    ),
                    description="\n\n".join(fake.paragraphs(nb=3)),
                    stock=fake.random_int(min=4, max=80),
                )

                self._save_mobile_primary(mobile, chosen_primary)

                extra_images = [img for img in brand_images if img != chosen_primary]
                random.shuffle(extra_images)
                for gallery_image in extra_images[:3]:
                    MobileImage.objects.create(
                        mobile=mobile,
                        image=self._upload_image(gallery_image, folder="mobiles/gallery"),
                        is_primary=False,
                    )

                MobileSpecification.objects.get_or_create(
                    mobile=mobile,
                    specification=specs["RAM"],
                    defaults={"value": random.choice(["4 GB", "6 GB", "8 GB", "12 GB"])},
                )
                MobileSpecification.objects.get_or_create(
                    mobile=mobile,
                    specification=specs["Storage"],
                    defaults={"value": random.choice(["64 GB", "128 GB", "256 GB", "512 GB"])},
                )
                MobileSpecification.objects.get_or_create(
                    mobile=mobile,
                    specification=specs["Battery"],
                    defaults={"value": random.choice(["5000 mAh", "5200 mAh", "6000 mAh"])},
                )
                MobileSpecification.objects.get_or_create(
                    mobile=mobile,
                    specification=specs["Display"],
                    defaults={"value": random.choice(["6.5 inch", "6.67 inch", "6.78 inch"])},
                )
                MobileSpecification.objects.get_or_create(
                    mobile=mobile,
                    specification=specs["Chipset"],
                    defaults={"value": fake.lexify(text="Helio ???")},
                )

                created_mobile_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_mobile_count} fake mobiles across {len(brands)} brands "
                f"with {len(categories)} categories."
            )
        )