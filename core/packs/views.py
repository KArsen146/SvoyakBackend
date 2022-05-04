from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Pack
from .serializers import PackSerializer, PackSuperShortSerializer
from .pagination import PacksListPagination


class PackViewSet(ModelViewSet):
    queryset = Pack.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PackSerializer
    pagination_class = PacksListPagination

    def get_serializer_class(self):
        print(self.request.method)
        if self.action == 'list':
            return PackSuperShortSerializer
        return PackSerializer
