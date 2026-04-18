from django.contrib import admin

from .models import (
	Brand,
	Category,
	Mobile,
	MobileImage,
	MobileSpecification,
	Specification,
)


class MobileSpecificationInline(admin.TabularInline):
	model = MobileSpecification
	extra = 1
	autocomplete_fields = ("specification",)


class MobileImageInline(admin.TabularInline):
	model = MobileImage
	extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	list_display_links = ['name']
	search_fields = ("name",)
	ordering = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "slug")
	list_display_links = ['name']
	prepopulated_fields = {"slug": ("name",)}
	search_fields = ("name", "slug")
	ordering = ("name",)


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)
	ordering = ("name",)
	list_display_links = ['name']


@admin.register(Mobile)
class MobileAdmin(admin.ModelAdmin):
	list_display = (
		"name",
		"brand",
		"category",
		"price",
		"stock",
	)
	list_filter = ("brand", "category", "created_at", "updated_at")
	search_fields = ("name", "slug", "description", "brand__name", "category__name")
	readonly_fields = ("created_at", "updated_at")
	autocomplete_fields = ("brand", "category")
	prepopulated_fields = {"slug": ("name",)}
	inlines = (MobileSpecificationInline, MobileImageInline)
	ordering = ("-created_at",)
	list_display_links = ['name']


@admin.register(MobileSpecification)
class MobileSpecificationAdmin(admin.ModelAdmin):
	list_display = ("id", "mobile", "specification", "value")
	list_filter = ("specification",)
	search_fields = ("mobile__name", "specification__name", "value")
	autocomplete_fields = ("mobile", "specification")


@admin.register(MobileImage)
class MobileImageAdmin(admin.ModelAdmin):
	list_display = ("id", "mobile", "is_primary")
	list_filter = ("is_primary",)
	search_fields = ("mobile__name",)
	autocomplete_fields = ("mobile",)
