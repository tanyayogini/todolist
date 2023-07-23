from typing import Any

import requests

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse, GetUpdatesResponseSchema, SendMessageResponseSchema
from todolist import settings


class TgClient:
    def __init__(self, token: str | None = None):
        self.__token = token if token else settings.BOT_TOKEN

    def __get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.__token}/{method}"

    def _get(self, command: str, **params: Any) -> dict:
        url = self.__get_url(command)
        params.setdefault('timeout', 60)
        response = requests.get(url, params=params)
        if not response.ok:
            raise NotImplementedError

        return response.json()

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        data = self._get('getUpdates', offset=offset, timeout=timeout)
        return GetUpdatesResponseSchema().load(data)

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        data = self._get('sendMessage', chat_id=chat_id, text=text)
        return SendMessageResponseSchema().load(data)

