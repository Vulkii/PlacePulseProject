from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ReviewViewSet, UserGetTokenAPIView, UserSignUpAPIView, UserViewSet
)

api_v1 = DefaultRouter()
api_v1.register(r'reviews',
                ReviewViewSet, basename='reviews')
api_v1.register(r'users', UserViewSet, basename='users')

api_v1.auth = [
    path('signup/', UserSignUpAPIView.as_view(), name='signup'),
    path('token/', UserGetTokenAPIView.as_view(), name='token'),
]

urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include(api_v1.auth)),
]
