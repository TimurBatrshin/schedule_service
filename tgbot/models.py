# tgbot/models.py
from django.db import models

class TelegramChat(models.Model):
    chat_id = models.IntegerField(unique=True)
    
    def __str__(self):
        return str(self.chat_id)
