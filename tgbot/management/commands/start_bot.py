from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from tgbot.management.commands.scheduler_config import start_scheduler
from tgbot.bot import bot

import os
import django
# Указываем Django файл настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_service.settings')
django.setup()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        start_scheduler(bot)
        try:
            bot.polling(none_stop=True, interval=0, timeout=10)
        except Exception as e:
            print(f"Ошибка при запуске бота: {e}")
        finally:
            print("Бот завершил свою работу.")
