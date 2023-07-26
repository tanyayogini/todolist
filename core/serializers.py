from typing import Dict

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password_repeat']

    def validate(self, attrs: Dict) -> Dict:
        if attrs.get("password") != attrs.pop("password_repeat"):
            raise ValidationError("Пароли должны совпадать!")
        return attrs

    def create(self, validated_data: Dict) -> User:
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        self.user = user

        return user


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UpdatePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        read_only_fields = ("id",)
        fields = ['old_password', 'new_password']

    def validate(self, attrs: Dict) -> Dict:
        user = self.instance
        old_password = attrs.get("old_password")
        if not user.check_password(old_password):
            raise ValidationError("Неправильный старый пароль!")
        return attrs

    def update(self, instance: User, validated_data: Dict) -> User:
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
