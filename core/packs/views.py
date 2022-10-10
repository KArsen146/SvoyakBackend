from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Pack
from .serializers import PackSerializer, PackShortSerializer, PackSuperShortSerializer
from .pagination import PacksListPagination


class PackViewSet(ModelViewSet):
    queryset = Pack.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PackSerializer
    pagination_class = PacksListPagination

    def get_serializer_class(self):
        print(self.request.method)
        if self.action != 'list':
            return PackSerializer

        if self.request.query_params.get('themes', 0) == 0:
            return PackSuperShortSerializer
        else:
            return PackShortSerializer
