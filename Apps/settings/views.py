from django.shortcuts import render, redirect
from datetime import date, datetime, timedelta
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .forms import CreateDataForm, UpdateDataForm

from Apps.wells.models import well

from Apps.users.models import User
from Apps.company.models import Company
from Apps.settings.models import setting

class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        company = User.objects.get_company_id(
            self.request.user)[0]["CompanyName"]
        company_name = Company.objects.get_company_name(company)[
            0]["CompanyName"]
        context = super(CompanyMixin, self).get_context_data(**kwargs)
        context['CompanyName'] = company_name
        return context

class ListOverview(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "settings/settings_view.html"
    login_url = reverse_lazy('user_app:user-login')
    # paginate_by = 2

    def get_queryset(self):
        # company = self.kwargs['company']
        company = User.objects.get_company_id(
            self.request.user)[0]["CompanyName"]
        
        allSettings = setting.objects.search_all(company)
        
        allData = {
            "allSettings":allSettings,
        }
        return allData

class NewCreateView(LoginRequiredMixin, CompanyMixin,CreateView):
    template_name = "settings/settings_add.html"
    login_url = reverse_lazy('user_app:user-login')
    model = setting
    form_class = CreateDataForm

    def get_initial(self):
        company_id = User.objects.get_company_id(self.request.user)[0]["CompanyName"]
        payload = {
            "CompanyId": company_id,
            "UserAuthor": self.request.user,
        }
        return payload

    success_url = reverse_lazy('devices_app:overview')

class DataUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "settings/settings_update.html"
    login_url = reverse_lazy('user_app:user-login')
    model = setting
    form_class = UpdateDataForm
    
    success_url = reverse_lazy('devices_app:overview')

class DataRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "settings/settings_remove.html"
    login_url = reverse_lazy('user_app:user-login')

    model = setting
    success_url = reverse_lazy('devices_app:overview')

class SuccessView(TemplateView):
    template_name = "home/home.html"