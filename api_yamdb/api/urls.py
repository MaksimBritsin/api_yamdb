from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include('users.urls')),
    path('v1/', include('reviews.urls'))
]
