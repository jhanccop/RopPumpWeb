
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect

from django.views.generic import (
    View,
    CreateView
)

from django.views.generic.edit import (
    FormView
)

from .forms import UserRegisterForm, LoginForm
from .models import User

class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = '/'

    def form_valid(self, form):

        User.objects.create_user(
            form.cleaned_data['UserName'],
            form.cleaned_data['Email'],
            form.cleaned_data['password1'],
            Name = form.cleaned_data['Name'],
            LastName = form.cleaned_data['LastName'],
            CompanyName = form.cleaned_data['CompanyName'],
        )

        return super(UserRegisterView, self).form_valid(form)

class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('overview_app:overview')

    def form_valid(self, form):
        user = authenticate(
            username = form.cleaned_data['username'],
            password = form.cleaned_data['password'],
        )
        login(self.request, user)
        return super(LoginUser, self).form_valid(form)

class LogoutView(View):
    def get(self, request, *args, **kargs):
        logout(request)

        return HttpResponseRedirect(
            reverse(
                'home_app:home'
            )
        )
