from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)

from Apps.users.models import User
#from Apps.company.models import Company
from Apps.equipment.models import RodPumpWell, Tank, Environmental

from .forms import TankForm, RodPumpWellForm,EnvironmentalForm

class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        CompanyName = User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]
        context = super(CompanyMixin, self).get_context_data(**kwargs)
        context['CompanyName'] = CompanyName
        return context

# =================== LIST OVERVIEW ===========================
class ListOverview(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "equipment/equipment_overview.html"
    login_url = reverse_lazy('user_app:user-login')

    def get_queryset(self):
        CompanyName = User.objects.get_company_name(self.request.user)[0]["CompanyId__CompanyName"]

        RodPumpWell_list = RodPumpWell.objects.search_rodpump_by_company(CompanyName)
        Tank_list = Tank.objects.search_tank_by_company(CompanyName)
        Environmental_list = Environmental.objects.search_environmental_by_company(CompanyName)

        allEquipment = {
            "RodPumpWell_list":RodPumpWell_list,
            "Tank_list": Tank_list,   
            "Environmental_list": Environmental_list,   
        }
        return allEquipment

# =================== TANK ===========================
class TankView(LoginRequiredMixin, CompanyMixin,DetailView):
    model = Tank
    template_name = "equipment/equipment_tank_view.html"
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'Tank'

    def get_context_data(self, **kwargs):
        context = super(TankView, self).get_context_data(**kwargs)
        #toot un proceso
        #context['titulo'] = 'Empleado del mes'
        return context

class TankAddView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = "equipment/equipment_tank_add.html"
    login_url = reverse_lazy('user_app:user-login')
    model = Tank
    form_class = TankForm
    success_url = reverse_lazy('equipment_app:equipments')

    def get_form_kwargs(self,**kwargs):
        context = super(TankAddView, self).get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

class TankUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "equipment/equipment_tank_update.html"
    login_url = reverse_lazy('user_app:user-login')
    model = Tank
    form_class = TankForm
    success_url = reverse_lazy('equipment_app:equipments')

    def get_form_kwargs(self,**kwargs):
        context = super(TankUpdateView, self).get_form_kwargs(**kwargs)
        #kwargs = super().get_form_kwargs()
        #print(context)
        context['request'] = self.request
        return context

class TankRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "equipment/equipment_tank_remove.html"
    login_url = reverse_lazy('user_app:user-login')
    model = Tank
    success_url = reverse_lazy('equipment_app:equipments')


# =================== Environmental ===========================
class EnvironmentalAddView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = "equipment/equipment_environmental_add.html"
    login_url = reverse_lazy('user_app:user-login')
    model = Environmental
    form_class = EnvironmentalForm
    success_url = reverse_lazy('equipment_app:equipments')

    def get_form_kwargs(self,**kwargs):
        context = super(EnvironmentalAddView, self).get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

class EnvironmentalUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "equipment/equipment_environmental_update.html"
    login_url = reverse_lazy('user_app:user-login')
    model = Environmental
    form_class = EnvironmentalForm
    success_url = reverse_lazy('equipment_app:equipments')

    def get_form_kwargs(self,**kwargs):
        context = super(EnvironmentalUpdateView, self).get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

class EnvironmentalRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "equipment/equipment_environmental_remove.html"
    login_url = reverse_lazy('user_app:user-login')
    model = Environmental
    success_url = reverse_lazy('equipment_app:equipments')

# =================== ANALYZER ===========================
class RodPumpWellAddView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = "equipment/equipment_RodPumpWell_add.html"
    login_url = reverse_lazy('user_app:user-login')
    model = RodPumpWell
    form_class = RodPumpWellForm

    def get_initial(self):
        company_id = User.objects.get_company_id(self.request.user)[0]["CompanyName"]
        payload = {
            "CompanyId": company_id,
            "UserAuthor": self.request.user,
        }
        return payload

    success_url = reverse_lazy('equipment_app:equipments')

class RodPumpWellUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = "equipment/equipment_RodPumpWell_update.html"
    login_url = reverse_lazy('user_app:user-login')

    model = RodPumpWell
    form_class = RodPumpWellForm
    
    success_url = reverse_lazy('equipment_app:equipments')

class RodPumpWellRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = "equipment/equipment_RodPumpWell_remove.html"
    login_url = reverse_lazy('user_app:user-login')

    model = RodPumpWell
    success_url = reverse_lazy('equipment_app:equipments')

# =================== SUCCESS ===========================
class SuccessView(TemplateView):
    template_name = "home/home.html"