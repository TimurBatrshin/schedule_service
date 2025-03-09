import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from schedule.models import ScheduleItem, ScheduleUpdate
from django.conf import settings
from users.models import UserProfile, Group  # Импорт модели Group
from django.contrib.auth.models import User
from schedule_service.settings import TELEGRAM_BOT_TOKEN

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Обработчик для получения данных через Telegram Passport
@bot.message_handler(content_types=["passport_data"])
def handle_passport_data(message):
    user_id = message.from_user.id
    passport_data = message.passport_data

    # Получаем данные паспорта (например, номер телефона)
    phone_data = None
    for field in passport_data.data:
        if field.type == "phone_number":
            phone_data = field.data
            break

    if phone_data:
        # Ищем пользователя в базе по Telegram ID
        user_profile = UserProfile.objects.get(telegram_id=user_id)

        if user_profile:
            # Сохраняем данные в профиль
            user_profile.phone_number = phone_data
            user_profile.save()
            bot.send_message(user_id, "Ваш номер телефона успешно подтвержден!")
        else:
            bot.send_message(user_id, "Ваш аккаунт не зарегистрирован, зарегистрируйтесь сначала через команду /start.")
    else:
        bot.send_message(user_id, "Не удалось получить данные паспорта.")

# Команды бота
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    # Проверяем, есть ли пользователь в базе
    user_profile = UserProfile.objects.filter(telegram_id=user_id).first()
    
    if user_profile is None:
        user = User.objects.create(username=username)
        user_profile = UserProfile(user=user, telegram_id=user_id, first_name=first_name)
        user_profile.save()
        bot.send_message(user_id, f"Привет, {first_name}! Ты зарегистрирован в системе.")
    else:
        bot.send_message(user_id, f"Привет, {first_name}! Ты уже авторизован.")
    
    # Получаем персональное расписание для группы
    if not user_profile.group:
        bot.send_message(user_id, "Пожалуйста, укажи свою группу командой /set_group <название_группы>.")
        return
    
    schedule_data = ScheduleItem.objects.filter(group=user_profile.group)

    if schedule_data.exists():
        bot.send_message(user_id, format_schedule(schedule_data))
    else:
        bot.send_message(user_id, "У тебя пока нет запланированных занятий.")

    # Клавиатура с днями недели
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("Сегодня"),
        telebot.types.KeyboardButton("Завтра"),
        telebot.types.KeyboardButton("Понедельник"),
        telebot.types.KeyboardButton("Вторник"),
        telebot.types.KeyboardButton("Среда"),
        telebot.types.KeyboardButton("Четверг"),
        telebot.types.KeyboardButton("Пятница"),
        telebot.types.KeyboardButton("Суббота"),
        telebot.types.KeyboardButton("Воскресенье"),
        telebot.types.KeyboardButton("Вся неделя")
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите день:", reply_markup=keyboard)

# Команда для установки группы
@bot.message_handler(commands=['set_group'])
def set_group(message):
    user_id = message.from_user.id
    group_name = message.text.split(' ', 1)[1]  # Получаем название группы после команды

    user_profile = UserProfile.objects.filter(telegram_id=user_id).first()
    
    if user_profile is None:
        bot.send_message(user_id, "Сначала зарегистрируйтесь в системе командой /start.")
        return
    
    # Проверяем, существует ли группа с таким названием
    try:
        group = Group.objects.get(name=group_name)  # Предполагается, что модель называется Group
    except Group.DoesNotExist:
        bot.send_message(user_id, f"Группа с названием {group_name} не найдена. Пожалуйста, проверьте правильность ввода.")
        return
    
    # Проверяем, не привязан ли пользователь уже к группе
    if user_profile.group:
        bot.send_message(user_id, f"Вы уже привязаны к группе {user_profile.group}. Для изменения группы свяжитесь с администратором.")
        return
    
    user_profile.group = group  # Привязываем пользователя к группе
    user_profile.save()
    bot.send_message(user_id, f"Ваша группа {group_name} успешно установлена.")

# Обработчик для кнопок с днями недели
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    user_profile = UserProfile.objects.filter(telegram_id=user_id).first()
    
    if not user_profile.group:
        bot.send_message(user_id, "Для получения расписания, пожалуйста, укажите свою группу командой /set_group <название_группы>.")
        return
    
    today = datetime.now()
    text = message.text.lower()

    days_mapping = {
        0: "понедельник",
        1: "вторник",
        2: "среда",
        3: "четверг",
        4: "пятница",
        5: "суббота",
        6: "воскресенье"
    }

    if text == "сегодня":
        target_day = days_mapping[today.weekday()]
    elif text == "завтра":
        target_day = days_mapping[(today + timedelta(days=1)).weekday()]
    elif text == "вся неделя":
        schedule_data = ScheduleItem.objects.filter(group=user_profile.group).order_by('day_of_week', 'time')
        bot.send_message(message.chat.id, format_schedule(schedule_data))
        return
    elif text in days_mapping.values():
        target_day = text
    else:
        bot.send_message(user_id, "Неизвестная команда. Выбери день из меню.")
        return

    # Получаем расписание для указанного дня
    schedule_data = ScheduleItem.objects.filter(group=user_profile.group, day_of_week=target_day)

    formatted_schedule = format_schedule(schedule_data, day=target_day)

    bot.send_message(user_id, formatted_schedule if formatted_schedule.strip() else f"Расписание на {target_day} отсутствует.")

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
