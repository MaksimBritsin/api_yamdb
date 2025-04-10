from api.permissions import AdminUserOrReadOnly, IsAuthorModeratorOrReadOnly
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from reviews.base import BaseCategoryGenreViewSet, NestedViewSet
from reviews.filters import TitleFilter
from reviews.models import Category, Genre, Review, Title
from reviews.serializers import (CategorySerializer, CommentSerializer,
                                 GenreSerializer, ReviewSerializer,
                                 TitleSerializer)


class CategoryViewSet(BaseCategoryGenreViewSet):
    """Вьюсет для категорий произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    """Вьюсет для жанров произведений."""

    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = (
        Title.objects
        .select_related('category')
        .prefetch_related('genre')
        .annotate(rating=Avg('reviews__score'))
        .order_by('name')
    )
    serializer_class = TitleSerializer
    permission_classes = (AdminUserOrReadOnly,)
    http_method_names = ['get', 'post', 'delete', 'patch']
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TitleFilter
    search_fields = ['name']


class ReviewViewSet(NestedViewSet):
    """Вьюсет для отзывов на произведения."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorOrReadOnly,)
    http_method_names = ['get', 'post', 'delete', 'patch']
    parent_model = Title
    parent_lookup = 'title'
    queryset_related_name = 'reviews'


class CommentViewSet(NestedViewSet):
    """Вьюсет для комментариев к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    parent_model = Review
    parent_lookup = 'review'
    queryset_related_name = 'comments'
