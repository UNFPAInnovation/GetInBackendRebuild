from datetime import datetime

from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveDestroyAPIView, \
    CreateAPIView, UpdateAPIView
from rest_framework.permissions import *

# todo create user using authentication
from app.models import Girl
from app.serializers import UserSerializer, User, UserGetSerializer, GirlSerializer


class UserCreateView(CreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User


class UserView(ListAPIView):
    """
    Returns all users in the system.
    """
    serializer_class = UserGetSerializer
    permission_classes = (IsAdminUser,)
    # filter_backends = (OrderingFilter, DjangoFilterBackend)
    # filter_class = UserFilter
    # '&ordering=-last_login' gives most active users
    # '&ordering=last_login' gives domant users
    ordering_fields = ('last_login',)

    def get_queryset(self):
        return User.objects.all()


class GirlCreateView(CreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = [AllowAny]
    serializer_class = GirlSerializer
    queryset = Girl


class GirlView(ListCreateAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class GirlDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    # permission_classes = (IsAdminUser,)
