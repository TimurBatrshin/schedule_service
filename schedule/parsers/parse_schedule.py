# parsers.py
import openpyxl
from schedule.models import ScheduleItem, Group
import logging

logger = logging.getLogger(__name__)

def parse_schedule_new(excel_file):
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active

    # Проходим по всем строкам
    for row in sheet.iter_rows(min_row=2, values_only=True):
        group_name = row[0]
        day_of_week = row[1]
        time = row[2]
        activity = row[3]
        location = row[4]
        description = row[5]

        logger.debug(f"Группа: {group_name}, День недели: {day_of_week}, Время: {time}, Активность: {activity}, Место: {location}, Описание: {description}")

        group, created = Group.objects.get_or_create(name=group_name)

        ScheduleItem.objects.create(
            group=group,
            day_of_week=day_of_week,
            time=time,
            activity=activity,
            location=location,
            description=description,
        )
    logger.debug("Парсинг завершен.")
