from django.shortcuts import render, redirect
from .models import ScheduleItem, ScheduleUpdate
from users.models import UserProfile
from .forms import ScheduleItemForm 
import datetime

# Функция для получения названия дня недели по его номеру
def get_weekday_name(day_number):
    days_map = {
        0: "понедельник", 1: "вторник", 2: "среда", 3: "четверг",
        4: "пятница", 5: "суббота", 6: "воскресенье"
    }
    return days_map[day_number]

# Список всех расписаний пользователя, отсортированных по дню недели и времени
def schedule_list(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    group = user_profile.group
    return render(request, 'schedule/schedule_list.html', {'group': group})
# Показывает расписание на выбранный день (по умолчанию на сегодня)
def show_daily_schedule(request, day=None):
    user = request.user
    group = user.userprofile.group
    
    if not day:
        day = get_weekday_name(datetime.datetime.today().weekday())
    
    valid_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    if day not in valid_days:
        return render(request, 'schedule/error.html', {'message': 'Неверный день недели.'})

    # Получаем расписание на выбранный день
    schedules = ScheduleItem.objects.filter(group=group, day_of_week=day)
    
    # Индекс текущего дня
    day_index = valid_days.index(day)
    
    # Рассчитываем предыдущий и следующий день
    previous_day = valid_days[(day_index - 1) % len(valid_days)]
    next_day = valid_days[(day_index + 1) % len(valid_days)]

    return render(request, 'schedule/daywise.html', {
        'schedules': schedules,
        'day': day,
        'previous_day': previous_day,
        'next_day': next_day
    })


# Функция для добавления или редактирования расписания
def add_or_edit_schedule(request, schedule_id=None):
    if schedule_id:
        schedule_item = ScheduleItem.objects.get(id=schedule_id, user=request.user)
    else:
        schedule_item = None

    if request.method == 'POST':
        form = ScheduleItemForm(request.POST, instance=schedule_item)
        if form.is_valid():
            form.save()
            ScheduleUpdate.objects.create()  # Добавляем запись об обновлении расписания
            return redirect('schedule:schedule_list')  # Перенаправляем на список расписаний
    else:
        form = ScheduleItemForm(instance=schedule_item)

    return render(request, 'schedule/add_or_edit_schedule.html', {'form': form})

# Расписание на сегодня
def today_schedule(request):
    today_day_name = get_weekday_name(datetime.datetime.today().weekday())
    schedules_today = ScheduleItem.objects.filter(group=request.user.userprofile.group, day_of_week=today_day_name)

    valid_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    
    day_index = valid_days.index(today_day_name)
    
    # Рассчитываем предыдущий и следующий день
    previous_day = valid_days[(day_index - 1) % len(valid_days)]
    next_day = valid_days[(day_index + 1) % len(valid_days)]

    return render(request, 'schedule/daywise.html', {
        'schedules': schedules_today,
        'day': today_day_name,
        'previous_day': previous_day,
        'next_day': next_day
    })

# Расписание на завтра
def tomorrow_schedule(request):
    tomorrow_day_name = get_weekday_name((datetime.datetime.today().weekday() + 1) % 7)
    schedules_tomorrow = ScheduleItem.objects.filter(group=request.user.userprofile.group, day_of_week=tomorrow_day_name)
    valid_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    
    day_index = valid_days.index(tomorrow_day_name)
    
    # Рассчитываем предыдущий и следующий день
    previous_day = valid_days[(day_index - 1) % len(valid_days)]
    next_day = valid_days[(day_index + 1) % len(valid_days)]

    return render(request, 'schedule/daywise.html', {
        'schedules': schedules_tomorrow,
        'day': tomorrow_day_name,
        'previous_day': previous_day,
        'next_day': next_day
    })

# Показывает расписание на всю неделю
def week_schedule(request):
    # Получаем расписание на все дни недели для текущего пользователя
    schedules = {}
    for day_number in range(7):
        day_name = get_weekday_name(day_number)
        schedules[day_name] = ScheduleItem.objects.filter(user=request.user, day_of_week=day_name).order_by('time')
    
    return render(request, 'schedule/week_schedule.html', {'schedules': schedules})
