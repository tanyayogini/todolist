from django.db import models
from django.utils.crypto import get_random_string

from core.models import User


class TgUser(models.Model):
    telegram_chat_id = models.BigIntegerField(primary_key=True, editable=False, unique=True)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, null=True, blank=True)
    verification_code = models.CharField(max_length=20, unique=True, null=True, blank=True)

    @staticmethod
    def _generate_verification_code() -> str:
        return get_random_string(20)

    def update_verification_code(self) -> None:
        self.verification_code = self._generate_verification_code()
        self.save(update_fields=['verification_code'])

    @property
    def is_verified(self) -> bool:
        return bool(self.user)





