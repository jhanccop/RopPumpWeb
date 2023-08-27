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

from Apps.wells.models import well
from Apps.batteries.models import Battery

from Apps.users.models import User
from Apps.company.models import Company

from .forms import CreateDataForm

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
    template_name = "wells/wells.html"
    login_url = reverse_lazy('user_app:user-login')

    def get_queryset(self):
        # company = self.kwargs['company']
        company = User.objects.get_company_id(
            self.request.user)[0]["CompanyName"]
        
        well_list = well.objects.search_all_pump(company)

        #print(well_list)
        
        allData = {
            "well_list": well_list,
        }

        return allData
    
class DataUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "wells/wells_update.html"
    login_url = reverse_lazy('user_app:user-login')

    model = well
    form_class = CreateDataForm
    
    
    success_url = reverse_lazy('wells_app:overview')
    
class DataRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "wells/wells_remove.html"
    login_url = reverse_lazy('user_app:user-login')

    model = well
    success_url = reverse_lazy('wells_app:overview')
    
class SuccessView(TemplateView):
    template_name = "home/home.html"