from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ValidationError
from reviews.const import MAX_LENGTH_NAME, MAX_LENGTH_SLUG

User = get_user_model()


class BaseNameSlugModel(models.Model):
    """Абстрактная модель с полями name и slug."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        verbose_name='Слаг'
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)
        verbose_name = 'Название и слаг'
        verbose_name_plural = 'Названия и слаги'


class Category(BaseNameSlugModel):
    """Модель категории произведений."""

    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNameSlugModel):
    """Модель жанра произведений."""

    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения (фильм, книга, музыка и т. д.)."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название произведения'
    )
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(
        blank=True, null=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)


class Review(models.Model):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.PositiveSmallIntegerField(verbose_name='Оценка')

    def validate_score(value):
        if value < 1 or value > 10:
            raise ValidationError('Оценка должна быть от 1 до 10')

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        unique_together = ('title', 'author')


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    def __str__(self):
        return f'Комментарий от {self.author} к {self.review}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
