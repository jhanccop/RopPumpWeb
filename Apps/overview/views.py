from datetime import date, datetime, timedelta
import json
import csv
from io import TextIOWrapper

from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    TemplateView,
    ListView
)

from Apps.wells.models import well
from Apps.production.models import ProductionFluid
from Apps.groups.models import Group
from Apps.settings.models import setting
from .models import RodPumpData

from Apps.users.models import User
from Apps.company.models import Company

#from .forms import CreateWellTestForm, CreateSampleTestForm, CreateBuildUpTestForm, SetExposureIndexESPForm, SetImprovementIndexESPForm
#from applications.well.forms import CreateCompletionForm


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
    template_name = "overview/overview.html"
    login_url = reverse_lazy('user_app:user-login')
    # paginate_by = 2

    def get_queryset(self):
        # company = self.kwargs['company']
        company = User.objects.get_company_id(
            self.request.user)[0]["CompanyName"]
        
        # -- get gropus in company --
        list_group = Group.objects.filter(Company=company)

        groupsWells = {}

        # -- get wells in company by groups--
        for group_i in list_group:
            list_wells = well.objects.filter(FieldName__Company=company, GroupName=group_i)
            tempData = []
            for well_i in list_wells:
                tempPayload = {
                    'PumpName': well_i.PumpName,
                    'Field': well_i.FieldName,
                    'Battery': well_i.BatteryName,
                }
                settingWells = setting.objects.filter(PumpName=well_i).values("Status").last()
                if settingWells != None:
                    tempPayload['Status'] = settingWells["Status"]
                pass

                dataWell = RodPumpData.objects.filter(PumpName=well_i).last()
                if dataWell != None:
                    tempPayload['LastUpdate'] = dataWell.DateCreate
                    #tempPayload['Position'] = dataWell.Position
                    #tempPayload['LoadPump'] = dataWell.LoadPump
                    tempPayload['SPM'] = dataWell.SPM
                    tempPayload['PumpFill'] = dataWell.PumpFill
                    tempPayload['Diagnosis'] = dataWell.Diagnosis
                    tempPayload['RunTime'] = dataWell.RunTime

                    if datetime.now().date() == dataWell.DateCreate.date():
                        tempPayload['CurrentContidition'] = dataWell.Status
                    else:
                        tempPayload['CurrentContidition'] = "No data today"

                tempData.append(tempPayload)
            groupsWells[group_i] = tempData
        """
        list_wells = well.objects.filter(
            FieldName__Company=company, PumpType="Sucker Rod Pump")
        rodpumpData = []
        for well_i in list_wells:
            temp2 = {
                'PumpName': well_i.PumpName,
                'Field': well_i.FieldName,
                'Battery': well_i.BatteryName,
            }

            settingWells = setting.objects.filter(
                PumpName=well_i).values("Available").last()
            if settingWells != None:
                temp2['Available'] = settingWells["Available"]

            dataWells2 = RodPumpData.objects.filter(PumpName=well_i).last()
            if dataWells2 != None:
                temp2['LastUpdate'] = dataWells2.DateCreate
                #temp2['Position'] = dataWells2.Position
                #temp2['LoadPump'] = dataWells2.LoadPump
                #temp2['PIP'] = dataWells2.HeadPressure
                temp2['SPM'] = dataWells2.SPM
                temp2['PumpFill'] = dataWells2.PumpFill
                temp2['Diagnosis'] = dataWells2.Diagnosis

                if datetime.now().date() == dataWells2.DateCreate.date():
                    temp2['CurrentContidition'] = dataWells2.Status
                else:
                    temp2['CurrentContidition'] = "No data today"

            rodpumpData.append(temp2)

        wellsByDiagnosis = []
        if len(rodpumpData) != 0:
            TempDiagnosis = dict(Counter(np.concatenate([ x.get("Diagnosis",[]) for x in rodpumpData])))
            wellsByDiagnosis = [",".join(map(str,list(TempDiagnosis.keys()))),",".join(map(str,list(TempDiagnosis.values())))]
        
        """

        allData = {
            #"rodpumpData": rodpumpData,
            #"wellsByDiagnosis":wellsByDiagnosis,
            "groupsWells":groupsWells
        }

        return allData


class ListDataRodPump(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "overview/socked-rod-pump.html"
    login_url = reverse_lazy('user_app:user-login')
    #ordering = ['DateCreate']
    #paginate_by = 20

    def get_queryset(self):
        wellName = self.kwargs['PumpName']
        intervalDate = self.request.GET.get("dateKword", '')

        #pump = well.objects.search_type_pump(wellName)

        if intervalDate == "today" or intervalDate == "Today" or intervalDate == "":
            list_data = RodPumpData.objects.search_today_RPdata(wellName)
        else:
            list_data = RodPumpData.objects.search_by_interval_RPdata(
                intervalDate, wellName)  # .order_by('-DateCreate')
        
        trends_fill_spm = RodPumpData.objects.search_trends_fill_SPM_RPdata(wellName)
        trends_runtime = RodPumpData.objects.search_trends_runTime_RPdata(wellName)

        # ================= GET EXPLORE DATA ===========
        company = User.objects.get_company_id(
            self.request.user)[0]["CompanyName"]
        
        # -- get gropus in company --
        list_group = Group.objects.filter(Company=company)

        groupsWells = {}

        for group_i in list_group:
            list_wells = well.objects.filter(FieldName__Company=company, GroupName=group_i)
            tempData = []
            for well_i in list_wells:
                tempPayload = {
                    'PumpName': well_i.PumpName,
                    'Field': well_i.FieldName,
                    'Battery': well_i.BatteryName,
                }
                settingWells = setting.objects.filter(PumpName=well_i).values("Available").last()
                if settingWells != None:
                    tempPayload['Available'] = settingWells["Available"]
                pass

                dataWell = RodPumpData.objects.filter(PumpName=well_i).last()
                if dataWell != None:
                    tempPayload['LastUpdate'] = dataWell.DateCreate
                    #tempPayload['Position'] = dataWell.Position
                    #tempPayload['LoadPump'] = dataWell.LoadPump
                    tempPayload['SPM'] = dataWell.SPM
                    tempPayload['PumpFill'] = dataWell.PumpFill
                    tempPayload['Diagnosis'] = dataWell.Diagnosis
                    tempPayload['RunTime'] = dataWell.RunTime

                    if datetime.now().date() == dataWell.DateCreate.date():
                        tempPayload['CurrentContidition'] = dataWell.Status
                    else:
                        tempPayload['CurrentContidition'] = "No data today"

                tempData.append(tempPayload)
            groupsWells[group_i] = tempData
        
        productionData = ProductionFluid.objects.search_today(wellName)

        payload = {
            "name": wellName,
            "date": intervalDate,
            "data": list_data,
            "productionData": productionData,
            "trends_fill_spm":trends_fill_spm,
            "trends_runtime":trends_runtime,#trends_runtime_prod
            "groupsWells":groupsWells
        }
        return payload


class SuccessView(TemplateView):
    template_name = "home/home.html"


def compare_headers(headers1, headers2):
    print("comparing headers", headers1)
    print("comparing headers", headers2)
    if len(headers1) != len(headers2):
        print("length error")
        return False
    for i in range(len(headers1)):
        # compare ignoring case and whitespace
        if headers1[i].strip().lower() != headers2[i].strip().lower():
            return False
    return True

