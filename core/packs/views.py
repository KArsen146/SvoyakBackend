from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Pack
from .serializers import PackSerializer


class PackViewSet(ModelViewSet):
    queryset = Pack.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PackSerializer
