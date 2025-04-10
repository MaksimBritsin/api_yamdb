from api.permissions import AdminUserOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets


class BaseCategoryGenreViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """Базовый ViewSet для категорий и жанров."""

    permission_classes = (AdminUserOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class NestedViewSet(viewsets.ModelViewSet):
    """
    Универсальный ViewSet для вложенных ресурсов.
    Требуется определить:
    - parent_model: модель родителя (например, Title или Review)
    - parent_lookup: имя поля для связи (например, 'title' или 'review')
    """

    parent_model = None
    parent_lookup = None

    def get_parent_object(self):
        """Получает объект родителя на основе URL-параметра."""
        parent_id = self.kwargs.get(f"{self.parent_lookup}_id")
        return get_object_or_404(self.parent_model, pk=parent_id)

    def get_queryset(self):
        """Возвращает queryset для вложенного ресурса."""
        parent = self.get_parent_object()
        return getattr(parent, self.queryset_related_name).all()

    def perform_create(self, serializer):
        """Сохраняет объект, привязанный к родителю и текущему пользователю."""
        parent = self.get_parent_object()
        serializer.save(
            **{self.parent_lookup: parent}, author=self.request.user)
