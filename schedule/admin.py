# admin.py
from django.contrib import admin

# admin.py
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from .models import ScheduleItem, Group
from .parsers.parse_schedule import parse_schedule_new  # Функция парсинга
from django import forms
import logging
logger = logging.getLogger(__name__)

class ScheduleUploadForm(forms.Form):
    excel_file = forms.FileField()

class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'time', 'activity', 'group', 'location', 'description')
    list_filter = ('day_of_week', 'group')
    search_fields = ('activity', 'group__name', 'day_of_week')
    ordering = ('day_of_week', 'time')

    fieldsets = (
        (None, {
            'fields': ('day_of_week', 'time', 'activity', 'group', 'location', 'description')
        }),
    )

    # Кастомизация страницы списка объектов админки
    change_list_template = 'admin/schedule_item_change_list.html'

    def save_model(self, request, obj, form, change):
        """Добавление/обновление объекта расписания."""
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload_schedule/', self.admin_site.admin_view(self.upload_schedule), name='schedule_scheduleitem_upload_schedule')
        ]
        return custom_urls + urls

    def upload_schedule(self, request):
        if request.method == "POST" and request.FILES.get("excel_file"):
            file = request.FILES["excel_file"]
            try:
                # Логируем начало парсинга
                logger.debug("Начало парсинга файла...")
                parse_schedule_new(file)
                logger.debug("Парсинг завершен успешно.")
                self.message_user(request, "Расписание успешно загружено!")
            except Exception as e:
                self.message_user(request, f"Ошибка при загрузке расписания: {str(e)}", level="error")
                logger.error(f"Ошибка при загрузке расписания: {str(e)}")
            return HttpResponse("Файл загружен успешно")
        else:
            # Логируем, если файл не был загружен
            logger.debug("Нет загруженного файла.")
            
        form = ScheduleUploadForm()
        return render(request, "admin/upload_schedule.html", {"form": form})


# Регистрация админки
admin.site.register(ScheduleItem, ScheduleItemAdmin)
