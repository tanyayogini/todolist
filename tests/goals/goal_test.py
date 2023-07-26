import pytest
from rest_framework import status

from goals.models import BoardParticipant
from tests.factories import GoalFactory


@pytest.mark.django_db
def test_create_goal(client, auth_user_response, get_category, goal):
    """Тест на создание цели авторизованным пользователем-участником доски"""
    fields = ["id", "created", "updated", "title", "description", "due_date", "status", "priority", "category"]
    response = client.post('/goals/goal/create', data={"title": goal.title, "category": get_category.id},
                           content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    assert list(response.data.keys()) == fields


@pytest.mark.django_db
def test_create_category_not_perm(client, get_category, auth_user_2_response, goal):
    """Тест на попытку создания цели пользователем-не участником доски"""

    expected_response = {"category": [
        "Нельзя редактировать цели на чужой доске или при роли Читатель"]}

    create_response = client.post('/goals/goal/create',
                                  data={"title": goal.title, "category": get_category.id},
                                  content_type='application/json')

    assert create_response.status_code == status.HTTP_400_BAD_REQUEST
    assert create_response.data == expected_response


@pytest.mark.django_db
def test_get_category_list(client, auth_user_response, user, get_category):
    """Тест на получение списка целей"""
    goals = GoalFactory.create_batch(5, user=user, category=get_category)
    response = client.get("/goals/goal/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5


@pytest.mark.django_db
def test_get_goal_by_id(client, board, user, get_category, auth_user_2_response, get_user_2_with_password):
    """Тест на получение цели пользователем-участником доски  ролью Читатель"""
    goal = GoalFactory(user=user, category=get_category)

    BoardParticipant.objects.create(user=get_user_2_with_password[0], board=board, role=3)
    get_response = client.get(f"/goals/goal/{goal.pk}")

    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.data["title"] == goal.title


@pytest.mark.django_db
def test_update_goal_no_perm(client, board, user, get_category, auth_user_2_response, get_user_2_with_password):
    """Тест на попытку изменения цели пользователем-участником доски ролью Читатель"""
    goal = GoalFactory(user=user, category=get_category)

    expected_response = {"detail": "You do not have permission to perform this action."}

    BoardParticipant.objects.create(user=get_user_2_with_password[0], board=board, role=3)
    update_response = client.patch(f"/goals/goal/{goal.pk}",
                                   data={"title": "updated-category", "category": get_category.id},
                                   content_type='application/json')

    assert update_response.status_code == status.HTTP_403_FORBIDDEN
    assert update_response.data == expected_response
