import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

data_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../../../static/data')


class Command(BaseCommand):
    """Команда для загрузки данных из CSV-файлов в базу данных."""

    help = 'Load data from CSV files into the database'

    def handle(self, *args, **kwargs):
        """Основной метод команды, загружает все данные."""
        self.load_categories()
        self.load_genres()
        self.load_titles()
        self.load_users()
        self.load_reviews()
        self.load_comments()
        self.stdout.write(self.style.SUCCESS('Successfully loaded all data!'))

    def load_categories(self):
        """Загружает категории из CSV-файла."""
        with open(
            os.path.join(data_path, 'category.csv'), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Category.objects.bulk_create(
                [Category(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                ) for row in reader]
            )

    def load_genres(self):
        """Загружает жанры из CSV-файла."""
        with open(
            os.path.join(data_path, 'genre.csv'), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Genre.objects.bulk_create(
                [Genre(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                ) for row in reader]
            )

    def load_titles(self):
        """Загружает произведения из CSV-файла."""
        with open(
            os.path.join(data_path, 'titles.csv'), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Title.objects.bulk_create(
                [Title(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=Category.objects.get(id=row['category'])
                ) for row in reader]
            )

    def load_users(self):
        """Загружает пользователей из CSV-файла."""
        with open(
            os.path.join(data_path, 'users.csv'), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            User.objects.bulk_create(
                [User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role']
                ) for row in reader]
            )

    def load_reviews(self):
        """Загружает отзывы из CSV-файла."""
        with open(
            os.path.join(data_path, 'review.csv'), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Review.objects.bulk_create(
                [Review(
                    id=row['id'],
                    title=Title.objects.get(id=row['title_id']),
                    author=User.objects.get(id=row['author']),
                    text=row['text'],
                    score=row['score']
                ) for row in reader]
            )

    def load_comments(self):
        """Загружает комментарии из CSV-файла."""
        with open(
            os.path.join(data_path, 'comments.csv'), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Comment.objects.bulk_create(
                [Comment(
                    id=row['id'],
                    review=Review.objects.get(id=row['review_id']),
                    author=User.objects.get(id=row['author']),
                    text=row['text']
                ) for row in reader]
            )
