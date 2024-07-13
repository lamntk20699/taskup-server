from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserCreateSerializer, UserSerializer
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from taskup_api.models import MemberInfo

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        data = request.data

        serializer = UserCreateSerializer(data=data)

        if not serializer.is_valid():
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.create(serializer.validated_data)
        user = UserSerializer(user)

        return Response(user.data, status=status.HTTP_201_CREATED)

class RetrieveUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user = UserSerializer(user)

        return Response(user.data, status=status.HTTP_200_OK)

class HomeView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request):
        content = {'message': 'Welcome to the JWT Authentication page using React Js and Django!'}
        return Response(content)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ObtainTokenResponseView(jwt_views.TokenObtainPairView):
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        email = request.data.get('email')
        userId = 'admin'

        try:
            serializer.is_valid(raise_exception=True)
            memberInfo = MemberInfo.objects.filter(email=email)
            if memberInfo.exists():
                userId = memberInfo[0].memberId
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response({ "uName": email, "userId": userId, "token": serializer.validated_data["access"]}, status=status.HTTP_200_OK)