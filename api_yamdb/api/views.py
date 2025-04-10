from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .helpers import get_confirmation_code
from .permissions import AdminPermission
from .serializers import SignupSerializer, TokenSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями. Доступно только администратору."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminPermission,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=UserSerializer,
        pagination_class=None
    )
    def me(self, request):
        """Возвращает или обновляет данные текущего пользователя."""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        if 'role' in request.data:
            return Response(
                {"detail": "Изменение роли пользователя запрещено."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(views.APIView):
    """Регистрация нового пользователя."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Создаёт пользователя или отправляет код подтверждения."""
        username = request.data.get('username')
        email = request.data.get('email')
        username_exists = User.objects.filter(username=username)
        email_exists = User.objects.filter(email=email)

        if username_exists:
            user = username_exists[0]
            if user.email != email:
                return Response({
                    'message': 'неверный адрес электронной почты',
                    'username': user.username,
                    'email': user.email
                }, status=status.HTTP_400_BAD_REQUEST)
            send_confirmation_code(user)

        if email_exists:
            user = email_exists[0]
            if user.username != username:
                return Response({
                    'message': 'неверное имя пользователя',
                    'username': user.username,
                    'email': user.email
                }, status=status.HTTP_400_BAD_REQUEST)

        else:
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                send_confirmation_code(user)

        return Response({
            'email': user.email,
            'username': user.username
        }, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    """Получение JWT-токена по коду подтверждения."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Выдаёт JWT-токен, если код подтверждения верный."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        if user.confirmation_code != confirmation_code:
            return Response(
                {'error': 'Отсутствует обязательное поле или оно некорректно'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = AccessToken.for_user(user)

        return Response({'token': str(token)}, status=status.HTTP_200_OK)


def send_confirmation_code(user):
    """Отправляет пользователю код подтверждения по email."""
    confirmation_code = get_confirmation_code()
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Ваш код подтверждения',
        f'Ваш код подтверждения: {user.confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
