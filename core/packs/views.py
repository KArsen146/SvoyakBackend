from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import AuthorFilter
from .models import Pack
from .permissions import IsOwnerOrReadOnly
from .serializers import PackSerializer, PackShortSerializer, PackSuperShortSerializer
from .pagination import PacksListPagination
from ..players.models import Player


class PackViewSet(ModelViewSet):
    queryset = Pack.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = PackSerializer
    pagination_class = PacksListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AuthorFilter
    search_fields = ['title', 'author']

    def get_queryset(self):
        return super().get_queryset().filter(is_deprecated=False)

    def get_serializer_class(self):
        print(self.request.method)
        if self.action != 'list':
            return PackSerializer

        if self.request.query_params.get('themes', 0) == 0:
            return PackSuperShortSerializer
        else:
            return PackShortSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Pack.objects.filter(title=serializer.validated_data['title'], is_deprecated=False).count():
            msg = 'Pack with this title already exists'
            return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)
        player = Player.objects.get(pk=request.user.id)
        serializer.save(author=player)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
            Метод преопределяется для следующего кейса:
            Если Author(Player) хочет изменить Pack, но он в данный момент используется в какой-то из игр, то:
                - создается новая модель пака с тем же названием, но с increased(version)
                - старой модели ставится is_deprecated = True
                - после каждого удаления комнаты проверяется, используется ли еще старый пак в играх
                    - если нет, то он удаляется
                - Pack с is_deprecated не показывается в списке паков и не используется в новых играх
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        player = Player.objects.get(pk=request.user.id)
        title = serializer.validated_data['title']
        packs_with_same_title = Pack.objects.filter(title=title, is_deprecated=False).count()
        if instance.title != title and packs_with_same_title:
            msg = 'Pack with this title already exists'
            return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(author=player)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.rooms_with_pack.count():
            self.perform_destroy(instance)
        else:
            instance.is_deprecated = True
        return Response(status=status.HTTP_204_NO_CONTENT)
