import pytest

from goals.models import BoardParticipant
from tests.factories import UserFactory, GoalCategoryFactory


@pytest.mark.django_db
@pytest.fixture
def auth_user_response(user, client):
    """Фикстура с авторизацией зарегистрированного пользователя"""
    password = user.password
    user.set_password(user.password)
    user.save()
    response = client.post("/core/login", data={
        "username": user.username,
        "password": password
    }, content_type='application/json')

    return response


@pytest.mark.django_db
@pytest.fixture
def get_user_2_with_password():
    """Фикстура со вторым пользователем для проверки доступов.
    Возвращает кортеж из пользователя и его пароля в нехешированном виде"""
    user_2 = UserFactory(username='user2', password='fndkivhtb13')
    password = user_2.password
    user_2.set_password(user_2.password)
    user_2.save()
    return user_2, password


@pytest.mark.django_db
@pytest.fixture
def auth_user_2_response(get_user_2_with_password, client):
    """Фикстура с авторизацией второго пользователя"""
    response = client.post("/core/login", data={
        "username": get_user_2_with_password[0].username,
        "password": get_user_2_with_password[1]}, content_type='application/json')

    return response


@pytest.mark.django_db
@pytest.fixture
def get_category(board, user):
    """Фикстура с категорией, относящейся к доске с созданным участником-пользователем
    Возвращает категорию"""
    BoardParticipant.objects.create(user=user, board=board)
    goal_category = GoalCategoryFactory.create(user=user, board=board)
    return goal_category
