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

from .models import ProductionFluid

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
    template_name = "production/production.html"
    login_url = reverse_lazy('user_app:user-login')
    # paginate_by = 2

    def get_queryset(self):
        # company = self.kwargs['company']
        company = User.objects.get_company_id(
            self.request.user)[0]["CompanyName"]
        
        # -- get gropus in company --
        list_Batteries = Battery.objects.filter(Company=company)

        batteryWells = {}

        # -- get wells in company by groups--
        for battery in list_Batteries:
            list_wells = well.objects.filter(FieldName__Company=company, BatteryName=battery)
            tempData = []
            for well_i in list_wells:
                tempPayload = {
                    'PumpName': well_i.PumpName,
                    'FieldName': well_i.FieldName,
                }
                
                tempData.append(tempPayload)
            batteryWells[battery] = tempData
        

        allData = {
            #"rodpumpData": rodpumpData,
            #"wellsByDiagnosis":wellsByDiagnosis,
            "batteryWells":batteryWells
        }

        return allData
    
class ListProduction(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "production/production_view.html"
    login_url = reverse_lazy('user_app:user-login')
    # ordering = ['DateCreate']
    # paginate_by = 10

    def get_queryset(self):
        wellName = self.kwargs['PumpName']
        intervalDate = self.request.GET.get("dateKword", '')

        #pump = well.objects.search_type_pump(wellName)

        if intervalDate == "this month" or intervalDate == "This Month" or intervalDate == "":
            list_data = ProductionFluid.objects.search_today(wellName)
        else:
            list_data = ProductionFluid.objects.search_by_interval(
                intervalDate, wellName)  # .order_by('-DateCreate')

        company = User.objects.get_company_id(
            self.request.user)[0]["CompanyName"]
        
        # -- get gropus in company --
        list_Batteries = Battery.objects.filter(Company=company)

        batteryWells = {}

        # -- get wells in company by groups--
        for battery in list_Batteries:
            list_wells = well.objects.filter(FieldName__Company=company, BatteryName=battery)
            tempData = []
            for well_i in list_wells:
                tempPayload = {
                    'PumpName': well_i.PumpName,
                    'FieldName': well_i.FieldName,
                }
                
                tempData.append(tempPayload)
            batteryWells[battery] = tempData

        payload = {
            "name": wellName,
            "date": intervalDate,
            "data": list_data,
            "batteryWells":batteryWells
        }

        return payload
    
class DataCreateView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = "production/production_add.html"
    login_url = reverse_lazy('user_app:user-login')

    model = ProductionFluid
    form_class = CreateDataForm
    

    def get_initial(self):
        wellName = self.kwargs['PumpName']
        pumpId = well.objects.search_id_pump(wellName)['id']
        payload = {
            #"name": wellName,
            "PumpName": pumpId,
            "UserAuthor": self.request.user,
        }
        return payload

    def get_success_url(self):
        self.success_url = reverse_lazy('production_app:view', kwargs={
                                        'PumpName': self.kwargs['PumpName']})

        return self.success_url.format(**self.object.__dict__)

    def get_context_data(self, **kwargs):
        upload_url = reverse_lazy(
            "production_app:view", kwargs={"PumpName": self.kwargs['PumpName']})
        context = super().get_context_data(**kwargs)
        context['PumpName'] = self.kwargs['PumpName']
        context['UserAuthor'] = self.request.user
        context['upload_url'] = upload_url
        return context

class DataUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "production/production_update.html"
    login_url = reverse_lazy('user_app:user-login')

    model = ProductionFluid

    fields = [
        'PumpName',
        'OilProd',
        'WaterProd'
    ]
    success_url = reverse_lazy('production_app:view')
    

class DataRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "production/production_remove.html"
    login_url = reverse_lazy('user_app:user-login')

    model = ProductionFluid
    success_url = reverse_lazy('production_app:view')

    

class SuccessView(TemplateView):
    template_name = "home/home.html"