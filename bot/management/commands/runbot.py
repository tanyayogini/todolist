from typing import Callable, Any

from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, GoalCategory
from todolist.settings import HOST
from pydantic import BaseModel


class FSM(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


users: dict[int, FSM] = {}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0

        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message) -> None:
        tg_user, _ = TgUser.objects.get_or_create(
            telegram_chat_id=msg.message_from.id,
            defaults={'username': msg.message_from.username})
        if not tg_user.is_verified:
            tg_user.update_verification_code()
            verification_code = tg_user.verification_code
            text = f'Здравствуйте! Введите на сайте код верификации: {verification_code}'
            self.tg_client.send_message(chat_id=msg.message_from.id, text=text)
        else:
            self.handle_auth_user(tg_user, msg)

    def handle_auth_user(self, tg_user: TgUser, msg: Message) -> None:
        """Обработка сообщений от авторизованных пользователей"""
        if msg.text == '/goals':
            goals_str = self.get_goals(tg_user=tg_user)
            self.tg_client.send_message(msg.message_from.id, goals_str)
        elif msg.text == '/create':
            self.send_categories(tg_user=tg_user)
        elif msg.text == '/cancel':
            users.pop(tg_user.telegram_chat_id, None)
        elif msg.message_from.id in users:
            users[tg_user.telegram_chat_id].next_handler(tg_user, msg)
        else:
            self.tg_client.send_message(tg_user.telegram_chat_id, 'Неизвестная команда')

    def send_categories(self, tg_user: TgUser):
        """Отправка пользователю списка категорий для создания цели"""
        categories = GoalCategory.objects.filter(user=tg_user.user, is_deleted=False)
        categories_dict: dict = {category.title: category for category in categories}
        categories_list = list(categories_dict.keys())
        if categories_list:
            categories_str = '\n'.join(categories_list)
            self.tg_client.send_message(tg_user.telegram_chat_id,
                                        f'Выберете категорию для создания цели: {categories_str}')
            users[tg_user.telegram_chat_id] = FSM(next_handler=self.handle_get_category)
            users[tg_user.telegram_chat_id].data.update({'categories': categories_dict})
        else:
            self.tg_client.send_message(tg_user.telegram_chat_id,
                                        'У Вас нет ни одной категории, невозможно создать цель')

    def handle_get_category(self, tg_user: TgUser, msg):
        """Получение категории для создания цели от пользователя"""
        categories_list = list(users[tg_user.telegram_chat_id].data["categories"].keys())
        if msg.text:
            if msg.text in categories_list:
                self.tg_client.send_message(tg_user.telegram_chat_id, "Категория выбрана")
                self.tg_client.send_message(tg_user.telegram_chat_id, f'Название вашей цели?')
                users[msg.message_from.id].data.update({"category": msg.text})
                users[msg.message_from.id].next_handler = self.handle_create_goal
            else:
                self.tg_client.send_message(tg_user.telegram_chat_id, "У вас нет такой категории")
                users.pop(tg_user.telegram_chat_id, None)
                self.send_categories(tg_user=tg_user)

    def handle_create_goal(self, tg_user: TgUser, msg):
        """Создание новой цели и отправка пользователю ссылки на нее"""
        if msg.text:
            category_str = users[tg_user.telegram_chat_id].data.get('category')
            category = users[tg_user.telegram_chat_id].data["categories"][category_str]
            goal = Goal.objects.create(category=category, title=msg.text, user=tg_user.user)
            self.tg_client.send_message(msg.message_from.id,
                                        f'Цель создана по адресу http://{HOST}/boards/{category.board.pk}'
                                        f'/categories/{category.id}/goals?goal={goal.pk}')
            users.pop(msg.message_from.id, None)

    def get_goals(self, tg_user: TgUser) -> str:
        goals = Goal.objects.filter(
            user=tg_user.user,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)
        goals_list: list[str] = [
            f'Цель: {goal.title}, дедлайн {goal.due_date}'
            for goal in goals]

        if goals_list:
            goals_str = '\n'.join(goals_list)
        else:
            goals_str = 'Цели не найдены'

        return goals_str
