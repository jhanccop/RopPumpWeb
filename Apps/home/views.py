from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class InitView(TemplateView):
    template_name = "home/home.html"

class LoginView(TemplateView):
    template_name = "home/login.html"
