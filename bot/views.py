from django.shortcuts import render

from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient


# Create your views here.
class VerificationView(generics.GenericAPIView):
    serializer_class = TgUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request: Request, *args, **kwargs) -> Response:
        serializer = TgUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_user: TgUser = serializer.save(user=request.user)
        TgClient().send_message(chat_id=tg_user.telegram_chat_id, text='Телеграм-бот верифицирован!')
        return Response(serializer.data)
