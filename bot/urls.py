from django.urls import path

from bot.apps import BotConfig
from bot.views import VerificationView

app_name = BotConfig.name
urlpatterns = [
    path('verify', VerificationView.as_view(), name='verify-bot')
]