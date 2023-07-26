import time
from typing import Optional

from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, GoalCategory
from todolist.settings import HOST


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
        if msg.text and msg.text.startswith('/'):
            match msg.text:
                case '/goals':
                    goals_str = self.get_goals(tg_user=tg_user)
                    self.tg_client.send_message(msg.message_from.id, goals_str)
                case '/create':
                    categories = self.get_categories(tg_user=tg_user)
                    categories_list = list(categories.keys())
                    if categories_list:
                        category = self.check_category(categories_list, tg_user=tg_user)
                        if category:
                            goal_link = self.create_new_goal(tg_user=tg_user, category=categories[category])
                            self.tg_client.send_message(
                                tg_user.telegram_chat_id,
                                goal_link)
                    else:
                        self.tg_client.send_message(msg.message_from.id,
                                                    'У Вас нет ни одной категории, невозможно создать цель')
                case '/cancel':
                    pass

                case _:
                    self.tg_client.send_message(msg.message_from.id, 'Неизвестная команда')
        else:
            self.tg_client.send_message(msg.message_from.id, 'Неизвестная команда без/')

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

    def get_categories(self, tg_user: TgUser) -> dict:
        categories = GoalCategory.objects.filter(user=tg_user.user, is_deleted=False)
        categories_dict: dict = {category.title: category for category in categories}
        return categories_dict

    def check_category(self, categories_list: list[str], tg_user: TgUser) -> Optional[str]:
        categories_str = '\n'.join(categories_list)
        category = ''
        while category not in categories_list:
            self.tg_client.send_message(tg_user.telegram_chat_id,
                                        f'Выберете категорию для создания цели: {categories_str}')
            time.sleep(10)

            category_response = self.tg_client.get_updates().result[-1].message.text
            if category_response in categories_list:
                category = category_response
                self.tg_client.send_message(tg_user.telegram_chat_id, "Категория выбрана")
                return category
            elif category_response == '/cancel':
                self.tg_client.send_message(tg_user.telegram_chat_id, "Операция отменена")
                break
            else:
                self.tg_client.send_message(tg_user.telegram_chat_id, "У вас нет такой категории")

        return None

    def create_new_goal(self, tg_user: TgUser, category: GoalCategory) -> str:
        self.tg_client.send_message(tg_user.telegram_chat_id, f'Название вашей цели?')
        time.sleep(30)
        title = self.tg_client.get_updates().result[-1].message.text
        goal = Goal.objects.create(category=category, title=title, user=tg_user.user)
        goal_link = f'Цель создана по адресу ' \
                    f'http://{HOST}/boards/{category.board.pk}/categories/{category.id}/goals?goal={goal.pk}'
        return goal_link
