from django import forms
from .models import ScheduleItem, Group

class ScheduleItemForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all())

    class Meta:
        model = ScheduleItem
        fields = ['day_of_week', 'time', 'activity', 'group', 'location', 'description']
