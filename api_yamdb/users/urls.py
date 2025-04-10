from api.views import SignupView, TokenView
from django.urls import path

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('token/', TokenView.as_view())
]
