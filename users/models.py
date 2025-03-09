from django.db import models
from django.contrib.auth.models import User
from schedule.models import Group  # Импортируем модель группы
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.IntegerField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    telegram_link = models.URLField(blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)  # Добавляем связь с группой
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Новое поле для телефона

    # Поле для связи с пользователем, зарегистрированным на сайте
    website_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="telegram_profile")

    def __str__(self):
        return self.user.username

    def set_telegram_id(self, telegram_id):
        self.telegram_id = telegram_id
        self.save()

    @classmethod
    def get_by_telegram_id(cls, telegram_id):
        return cls.objects.filter(telegram_id=telegram_id).first()

    @classmethod
    def get_by_website_user(cls, website_user):
        return cls.objects.filter(website_user=website_user).first()
    
    def create_user_profile(telegram_id, first_name, username):
        try:
            # Создаем пользователя, если его нет
            user, created = User.objects.get_or_create(username=username)
            
            # Получаем или создаем профиль для пользователя
            user_profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'telegram_id': telegram_id,
                    'first_name': first_name,
                    'username': username,
                }
            )

            if profile_created:
                print("Профиль пользователя создан.")
            else:
                print("Профиль пользователя уже существует.")
            
            return user_profile
        except Exception as e:
            print(f"Ошибка при создании профиля пользователя: {e}")
    
# Сигнал, который создаст UserProfile, если его нет
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Сигнал, который сохранит UserProfile при изменении User
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
