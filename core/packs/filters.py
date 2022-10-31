import django_filters
from django_property_filter import PropertyFilterSet, PropertyNumberFilter

from core.packs.models import Pack


class AuthorFilter(PropertyFilterSet):
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='contains')
    title = django_filters.CharFilter(field_name='title', lookup_expr='contains')
    rounds_count = PropertyNumberFilter(field_name='rounds_count', lookup_expr='exact')

    class Meta:
        model = Pack
        fields = ['author', 'title', 'rounds_count']
