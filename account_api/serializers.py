from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'account', 'password')
        def validate(self, data):
            user = User(**data)
            password = data.get('password')

            try:
                validate_password(password, user)
            except exceptions.ValidationError as e:
                serializer_errors = serializers.as_serializer_error(e)
                raise exceptions.ValidationError({'password': serializer_errors['non_field_errors']})
            return data

        def create(self, validated_data):
            user = User.objects.create_user(
              first_name=validated_data['first_name'],
              last_name=validated_data['last_name'],
              email=validated_data['email'],
              account=validated_data['account'],
              password=validated_data['password'],
            )

            return user

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'email', 'account')

class MyIssueTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        # token["name"] = "Testing"
        setattr(token, "name", "Testing")
        # ...

        return token