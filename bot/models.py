from django.db import models

from core.models import User


class TgUser(models.Model):
    telegram_chat_id = models.BigIntegerField(primary_key=True, editable=False, unique=True)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, null=True, blank=True)
    verification_code = models.CharField(max_length=255, unique=True, null=True, blank=True)



