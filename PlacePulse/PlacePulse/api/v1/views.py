from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import permissions, status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from rest_framework.filters import SearchFilter
from .mixins import ExcludePutViewSet
from rest_framework.decorators import action

from .serializers import (ReviewSerializer, UserSerializer,
                          UserTokenSerializer,
                          UserSignUpSerializer)
from django.contrib.auth import get_user_model
from .permissions import (IsAdmin, IsAdminModeratorOwnerOrReadOnly)
from .utils import send_message_to_user, make_confirmation_code

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]


class UserSignUpAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            send_message_to_user(username, email, make_confirmation_code(
                get_object_or_404(User, username=username)))
            return Response(request.data, status=status.HTTP_200_OK)
        if ((User.objects.filter(email=email).exists()
             and not User.objects.filter(username=username).exists())
                or (User.objects.filter(username=username).exists()
                    and User.objects.filter(email=email) != email)):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_message_to_user(username, email,
                             make_confirmation_code(serializer.save()))
        return Response(request.data, status=status.HTTP_200_OK)


class UserGetTokenAPIView(APIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        if default_token_generator.check_token(
                username, serializer.data['confirmation_code']
        ):
            token = AccessToken.for_user(username)
            return Response(
                {'token': str(token)}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ExcludePutViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get'],
        url_path='me',
        url_name='me',
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me_get(self, request):
        serializer = UserSerializer(
            self.request.user
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @me_get.mapping.patch
    def me_patch(self, request):
        serializer = UserSerializer(
            self.request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=self.request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
