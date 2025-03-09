# scheduler_config.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from schedule.models import ScheduleItem, ScheduleUpdate
from users.models import UserProfile

def start_scheduler(bot):
    def send_morning_schedule():
        print("Отправка утреннего расписания...")
        today = datetime.now()
        days_mapping = {
            0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье"
        }
        
        day = days_mapping[today.weekday()]
        
        schedule_data = get_schedule_for_day(day)
        for user_profile in UserProfile.objects.all():
            morning_schedule = format_schedule(schedule_data, day)
            if morning_schedule.strip():
                bot.send_message(user_profile.telegram_id, f"Расписание на сегодня:\n{morning_schedule}")
        print("Утреннее расписание отправлено.")

    def send_evening_schedule():
        print("Отправка вечернего расписания...")
        tomorrow = datetime.now() + timedelta(days=1)
        
        days_mapping = {
            0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье"
        }
        
        day = days_mapping[tomorrow.weekday()]

        schedule_data = get_schedule_for_day(day)
        for user_profile in UserProfile.objects.all():
            tomorrow_schedule = format_schedule(schedule_data, day)
            if tomorrow_schedule.strip():
                bot.send_message(user_profile.telegram_id, f"Расписание на завтра:\n{tomorrow_schedule}")
        print("Вечернее расписание отправлено.")

    # Функция для отправки уведомлений о изменениях расписания
    def send_schedule_update_notification():
        try:
            last_update = ScheduleUpdate.objects.latest('updated_at')
            last_update_time = last_update.updated_at
            users = UserProfile.objects.all()  # Получаем всех пользователей

            for user_profile in users:
                bot.send_message(user_profile.telegram_id, f"Обновление расписания: {last_update_time}")
            
            print(f"Уведомления о изменениях отправлены: {last_update_time}")
        except ScheduleUpdate.DoesNotExist:
            print("Нет обновлений расписания.")
            
    # Парсинг расписания из базы данных
    def get_schedule_for_day(day):
        schedule_data = ScheduleItem.objects.filter(day_of_week=day).order_by('time')
        return schedule_data

    # Форматирование расписания
    def format_schedule(schedule_data, day=None):
        if not schedule_data:
            return "Расписание не найдено."
        
        formatted_schedule = ""
        if day is None:
            for item in schedule_data:
                formatted_schedule += f"{item.day_of_week} {item.time.strftime('%H:%M')}: {item.activity}\n"
        else:
            formatted_schedule = f"Расписание ({day.lower()}):\n"
            for item in schedule_data:
                if item.day_of_week.lower() == day.lower():
                    formatted_schedule += f"{item.time.strftime('%H:%M')}: {item.activity}\n"
        
        return formatted_schedule

    # Функция для проверки изменений
    def check_schedule_update():
        try:
            print("Проверка обновлений расписания...")
            last_update = ScheduleUpdate.objects.latest('updated_at')
            last_update_time = last_update.updated_at
            users = UserProfile.objects.all()

            for user in users:
                if user.telegram_id:
                    print(f"Отправка уведомления пользователю {user.telegram_id}")
                    bot.send_message(user.telegram_id, f"Внимание! Расписание было обновлено: {last_update_time}")
            print(f"Уведомления о изменениях отправлены в {last_update_time}")
        except ScheduleUpdate.DoesNotExist:
            print("Расписание ещё не обновлялось.")



    scheduler = BackgroundScheduler()
    scheduler.add_job(send_morning_schedule, 'cron', hour=8, minute=0)
    scheduler.add_job(send_evening_schedule, 'cron', hour=20, minute=0)
    scheduler.add_job(send_schedule_update_notification, 'interval', hours=24)
    scheduler.add_job(check_schedule_update, 'interval', hours=24)
    try:
        scheduler.start()
        print("Планировщик задач запущен.")
    except Exception as e:
        print(f"Ошибка при запуске планировщика: {e}")
    
