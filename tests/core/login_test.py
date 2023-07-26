import pytest
from rest_framework import status


@pytest.mark.django_db
def test_login(client, auth_user_response):
    """Тест на авторизацию зарегистрированного пользователя"""
    assert auth_user_response.status_code == status.HTTP_201_CREATED
