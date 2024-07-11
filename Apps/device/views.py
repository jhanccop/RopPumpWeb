from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from Apps.users.models import User
#from Apps.company.models import Company
from Apps.device.models import TankDevice, WellAnalyzerDevice, EnvironmentalDevice

from .forms import TankForm, AnalyzerDataForm, EnvironmentalForm

class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        CompanyName = User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]
        context = super(CompanyMixin, self).get_context_data(**kwargs)
        context['CompanyName'] = CompanyName
        return context

# =================== LIST OVERVIEW ===========================
class ListOverview(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "device/device_overview.html"
    login_url = reverse_lazy('user_app:user-login')

    def get_queryset(self):
        CompanyName = User.objects.get_company_name(self.request.user)[0]["CompanyId__CompanyName"]

        tank_device_list = TankDevice.objects.search_tank_devices(CompanyName)
        analyzer_device_list = WellAnalyzerDevice.objects.search_Analyzer_devices(CompanyName)
        Environmental_list = EnvironmentalDevice.objects.search_Environmental_devices(CompanyName)

        allDevices = {
            "Tank_list": tank_device_list,
            "RodPumpWell_list":analyzer_device_list,
            "Environmental_list": Environmental_list,
        }
        return allDevices

# =================== TANK ===========================
class TankAddView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = "device/device_tank_add.html"
    login_url = reverse_lazy('user_app:user-login')
    model = TankDevice
    form_class = TankForm
    success_url = reverse_lazy('device_app:devices')

    def get_form_kwargs(self,**kwargs):
        context = super(TankAddView, self).get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

class TankUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "device/device_tank_update.html"
    login_url = reverse_lazy('user_app:user-login')
    model = TankDevice
    form_class = TankForm
    success_url = reverse_lazy('device_app:devices')

    def get_form_kwargs(self,**kwargs):
        context = super(TankUpdateView, self).get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

class TankRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "device/device_tank_remove.html"
    login_url = reverse_lazy('user_app:user-login')

    model = TankDevice
    success_url = reverse_lazy('device_app:devices')

# =================== ENVINRONMETNAL ===========================
class EnvironmentalAddView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = "device/device_environmental_add.html"
    login_url = reverse_lazy('user_app:user-login')
    model = EnvironmentalDevice
    form_class = EnvironmentalForm
    success_url = reverse_lazy('device_app:devices')

    def get_form_kwargs(self,**kwargs):
        context = super(EnvironmentalAddView, self).get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

class EnvironmentalUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "device/device_environmental_update.html"
    login_url = reverse_lazy('user_app:user-login')
    model = EnvironmentalDevice
    form_class = EnvironmentalForm
    success_url = reverse_lazy('device_app:devices')

    def get_form_kwargs(self,**kwargs):
        context = super(EnvironmentalUpdateView, self).get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

class EnvironmentalRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "device/device_environmental_remove.html"
    login_url = reverse_lazy('user_app:user-login')

    model = EnvironmentalDevice
    success_url = reverse_lazy('device_app:devices')

# =================== ANALYZER ===========================
class AnalyzerAddView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = "device/device_analyzer_add.html"
    login_url = reverse_lazy('user_app:user-login')
    model = WellAnalyzerDevice
    form_class = AnalyzerDataForm

    def get_initial(self):
        company_id = User.objects.get_company_id(self.request.user)[0]["CompanyName"]
        payload = {
            "CompanyId": company_id,
            "UserAuthor": self.request.user,
        }
        return payload

    success_url = reverse_lazy('device_app:devices')

class AnalyzerUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "device/device_analyzer_update.html"
    login_url = reverse_lazy('user_app:user-login')

    model = WellAnalyzerDevice
    form_class = AnalyzerDataForm
    
    success_url = reverse_lazy('device_app:devices')

class AnalyzerRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "device/device_analyzer_remove.html"
    login_url = reverse_lazy('user_app:user-login')

    model = WellAnalyzerDevice
    success_url = reverse_lazy('device_app:devices')

# =================== SUCCESS ===========================
class SuccessView(TemplateView):
    template_name = "home/home.html"