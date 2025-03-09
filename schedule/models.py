from django.db import models
from django.utils.timezone import localtime

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.name

class ScheduleItem(models.Model):
    day_of_week = models.CharField(max_length=20)  # строка для дня недели
    time = models.TimeField()
    activity = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    description = models.TextField()
    def formatted_time(self):
        return self.time.strftime('%H:%M')

    def __str__(self):
        return f"{self.day_of_week} {self.time}: {self.activity} ({self.group.name})"
    
    class Meta:
        ordering = ['day_of_week', 'time']
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

    @classmethod
    def get_schedule_for_day(cls, group, day):
        return cls.objects.filter(group=group, day_of_week=day).order_by('time')

    @classmethod
    def get_schedule_for_group(cls, group):
        return cls.objects.filter(group=group).order_by('day_of_week', 'time')

class ScheduleUpdate(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Обновление расписания от {self.updated_at}"
