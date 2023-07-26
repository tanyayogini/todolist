import pytest
from rest_framework import status

from goals.models import BoardParticipant
from tests.factories import BoardFactory


@pytest.mark.django_db
def test_board_creat(client, auth_user_response, board):
    """Тест на создание доски авторизованным пользователем"""
    fields = ["id", "created", "updated", "title", "is_deleted"]
    response = client.post('/goals/board/create', data={"title": board.title},
                           content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    assert list(response.data.keys()) == fields
    assert response.data["title"] == board.title


@pytest.mark.django_db
def test_board_creat_not_authorized(client, board):
    """Тест на попытку создания доски неавторизованным пользователем"""
    response = client.post('/goals/board/create', data={"title": board.title},
                           content_type='application/json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_board_get(client, auth_user_response, user):
    """Тест на получение списка досок, в которых пользователь является участником"""
    boards = BoardFactory.create_batch(5)
    BoardParticipant.objects.create(user=user, board=boards[0])
    BoardParticipant.objects.create(user=user, board=boards[1])
    BoardParticipant.objects.create(user=user, board=boards[2])

    response = client.get("/goals/board/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3


@pytest.mark.django_db
def test_board_get_by_id(client, auth_user_response, user, board):
    """Тест на получение доски по id пользователем-участником"""
    BoardParticipant.objects.create(user=user, board=board)

    response = client.get(f"/goals/board/{board.pk}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == board.title
