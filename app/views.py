from datetime import datetime

from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveDestroyAPIView, \
    CreateAPIView, UpdateAPIView
from rest_framework.permissions import *

# todo create user using authentication
from app.serializers import UserSerializer, User


class UserCreateView(CreateAPIView):
    """
    Allows creation of user.
    The only operation acceptable is buying products until they upgrade to Vendor, Driver, Courier.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User


# # use base APIView when you dont want to use the
# # native functionality like GET, PUT, DELETE, POST..
# class UserLoginAPIView(APIView):
#     """
#     Allows the users to login into the system.
#     Returns a token that will be used for accessing other endpoints.
#     """
#     permission_classes = [AllowAny]
#     serializer_class = UserLoginSerializer
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         serializer = UserLoginSerializer(data=data)
#         if serializer.is_valid(raise_exception=True):
#             new_data = serializer.data
#             return Response(new_data, status=HTTP_200_OK)
#         return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
#
#
# class UserView(ListAPIView):
#     """
#     Returns all users in the system(admins, vendors, users, drivers, couriers).
#     """
#     serializer_class = UserGetSerializer
#     permission_classes = (IsAdminUser,)
#     filter_backends = (OrderingFilter, DjangoFilterBackend)
#     filter_class = UserFilter
#     # '&ordering=-last_login' gives most active users
#     # '&ordering=last_login' gives domant users
#     ordering_fields = ('last_login',)
#
#     def get_queryset(self):
#         return User.objects.all()
#
#
# class UserDetailsView(RetrieveUpdateDestroyAPIView):
#     """
#     Allows RUD user
#     """
#     permission_classes = (IsAdminUser,)
#     queryset = User.objects.all()
#     serializer_class = UserGetSerializer