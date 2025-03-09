from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import View
from django.contrib import messages
from .forms import RegistrationForm
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import UserProfile

# Регистрация пользователя
class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Вы успешно зарегистрированы!")
            return redirect('login')  # Перенаправление на страницу входа
        else:
            messages.error(request, "Ошибка при регистрации. Пожалуйста, попробуйте снова.")
        return render(request, 'registration/register.html', {'form': form})

# Вход пользователя
class UserLoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect('schedule_list')  # Перенаправление на расписание
        else:
            messages.error(request, "Неверный логин или пароль.")
        return render(request, 'registration/login.html', {'form': form})

# Выход пользователя
class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Вы успешно вышли из системы.")
        return redirect('login')
