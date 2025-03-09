from django.urls import path
from .views import schedule_list, today_schedule, tomorrow_schedule, show_daily_schedule, week_schedule

urlpatterns = [
    path('schedules/', schedule_list, name='schedule_list'),  # Список всех расписаний
    path('today/', today_schedule, name='today'),  # Расписание на сегодня
    path('tomorrow/', tomorrow_schedule, name='tomorrow'),  # Расписание на завтра
    path('<str:day>/', show_daily_schedule, name="show_day"),  # Расписание на конкретный день
    path('week/', week_schedule, name='week_schedule'),  # Расписание на всю неделю
]
