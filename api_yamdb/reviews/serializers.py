from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=False
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=False
    )
    rating = serializers.IntegerField(
        read_only=True,
        default=0
    )

    class Meta:
        model = Title
        fields = "__all__"

    def to_representation(self, instance):
        """Преобразует объект в представление для вывода."""
        representation = super().to_representation(instance)

        if 'category' in representation:
            category_serializer = CategorySerializer(instance.category)
            representation['category'] = category_serializer.data
        if 'genre' in representation:
            genre_serializer = GenreSerializer(instance.genre.all(), many=True)
            representation['genre'] = genre_serializer.data
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'author', 'text', 'score', 'pub_date')
        read_only_fields = ('title', 'author', 'pub_date')

    def validate_score(self, value):
        """Проверяет, что оценка находится в диапазоне от 1 до 10."""
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Оценка должна быть от 1 до 10.'
            )
        return value

    def validate(self, data):
        """Запрещает повторные отзывы от одного пользователя."""
        user = self.context['request'].user
        title = self.context.get('view').kwargs.get('title_id')
        if (Review.objects.filter(title=title, author=user).exists()
                and self.context.get('request').method == 'POST'):
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'review', 'author', 'text', 'pub_date')
        read_only_fields = ('review', 'author', 'pub_date')
