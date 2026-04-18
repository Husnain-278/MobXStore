import django_filters
from .models import Mobile

class MobileFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name="brand__slug", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="icontains")

    min_price  = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Mobile
        fields = ['brand', 'category']