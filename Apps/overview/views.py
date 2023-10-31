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

from Apps.wells.models import well, tank
from Apps.production.models import ProductionFluid
from Apps.groups.models import Group
from Apps.settings.models import setting
from .models import RodPumpData, TankData

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
        
        # --  get wells by company ---
        list_wells = well.objects.filter(UserAuthor__CompanyName=company)
        wells_data = []
        for well_i in list_wells:
            tempPayload = {
                'PumpName': well_i.PumpName,
                'Field': well_i.FieldName,
                'Battery': well_i.BatteryName,
                'AnalyzerStatus': well_i.Status
            }

            dataWell = RodPumpData.objects.filter(PumpName=well_i).last()
            if dataWell != None:
                tempPayload['LastUpdate'] = dataWell.DateCreate
                tempPayload['SPM'] = dataWell.SPM
                tempPayload['PumpFill'] = dataWell.PumpFill
                tempPayload['Diagnosis'] = dataWell.Diagnosis
                tempPayload['RunTime'] = dataWell.RunTime

                if datetime.now().date() == dataWell.DateCreate.date():
                    tempPayload['WellStatus'] = dataWell.Status
                else:
                    tempPayload['WellStatus'] = "No data today"

            wells_data.append(tempPayload)

        # --  get tanks by company ---
        list_tanks = tank.objects.filter(UserAuthor__CompanyName=company)
        tanks_data = []
        for tank_i in list_tanks:
            tempPayloadTank = {
                'TankName': tank_i.TankName,
                'GroupName': tank_i.GroupName,
                'Status': tank_i.Status,
            }

            dataTank = TankData.objects.filter(TankName=tank_i).last()
            if dataTank != None:
                tempPayloadTank['LastUpdate'] = dataTank.DateCreate
                tempPayloadTank['OilLevel'] = dataTank.OilLevel
                tempPayloadTank['WaterLevel'] = dataWell.WaterLevel

                if datetime.now().date() == dataTank.DateCreate.date():
                    tempPayloadTank['CurrentContidition'] = dataTank.Status
                else:
                    tempPayloadTank['CurrentContidition'] = "No data today"

            tanks_data.append(tempPayloadTank) 

        allData = {
            "rodpumpData": wells_data,
            "tankData":tanks_data,
        }

        return allData

class ListOverview_v0(LoginRequiredMixin, CompanyMixin, ListView):
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

            dict_dev = {}

            # ==== get data for well analyzer ====
            tempData = []
            for well_i in list_wells:
                tempPayload = {
                    'PumpName': well_i.PumpName,
                    'Field': well_i.FieldName,
                    'Battery': well_i.BatteryName,
                }
                #TankFactor = 0
                #TankHeight = 0
                settingWellsWA = setting.objects.filter(PumpName = well_i, DeviceType = "Rod Pump Analyzer").values("Status").last()
                if settingWellsWA != None:
                    tempPayload['Status'] = settingWellsWA["Status"]

                #settingWellsTank = setting.objects.filter(PumpName = well_i, DeviceType = "Tank Level Meter").values("TankFactor","TankHeight").last()
                #if settingWellsTank != None:
                #    TankFactor = settingWellsTank["TankFactor"]
                #    TankHeight = settingWellsTank["TankHeight"]

                dataWell = RodPumpData.objects.filter(PumpName=well_i).last()
                if dataWell != None:
                    tempPayload['LastUpdate'] = dataWell.DateCreate
                    #tempPayload['Position'] = dataWell.Position
                    #tempPayload['LoadPump'] = dataWell.LoadPump
                    #tempPayload['bblOil'] = (TankHeight - dataWell.OilLevel) * TankFactor
                    #tempPayload['TankLevel'] = TankHeight - dataWell.OilLevel
                    #tper = (TankHeight - dataWell.TankLevel) * 100/TankHeight
                    #tempPayload['TankLevelPer'] = int(tper) - int(tper) % int(5)
                    tempPayload['SPM'] = dataWell.SPM
                    tempPayload['PumpFill'] = dataWell.PumpFill
                    tempPayload['Diagnosis'] = dataWell.Diagnosis
                    tempPayload['RunTime'] = dataWell.RunTime

                    if datetime.now().date() == dataWell.DateCreate.date():
                        tempPayload['CurrentContidition'] = dataWell.Status
                    else:
                        tempPayload['CurrentContidition'] = "No data today"

                tempData.append(tempPayload)
            
            dict_dev["wells"] = tempData
            

            # ==== get data for tank meter ====
            tempData = []
            list_tanks = tank.objects.filter(GroupName=group_i).values("TankName","Status","TankHeight","TankFactor")
            #print(list_tanks)
            for tank_i in list_tanks:
                #print(tank_i["TankName"])
                tempTankPayload = {
                    'TankName': tank_i["TankName"],
                    'Status': tank_i["Status"]
                }
                TankFactor = tank_i["TankFactor"]
                TankHeight = tank_i["TankHeight"]

                list_data = TankData.objects.search_today_Tankdata(tank_i["TankName"], TankFactor,TankHeight)
                tempTankPayload['list_data'] = list_data

                tempData.append(tempTankPayload)

            dict_dev["tanks"] = tempData

            groupsWells[group_i] = dict_dev
       

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

        TankFactor = 0
        #settingWellsWA = setting.objects.filter(PumpName = wellName, DeviceType = "Rod Pump Analyzer").values("Status").last()
        #if settingWellsWA != None:
        #    tempPayload['Status'] = settingWellsWA["Status"]

        settingWellsTank = setting.objects.filter(PumpName__PumpName = wellName, DeviceType = "Tank Level Meter").values("TankFactor","TankHeight").last()
        if settingWellsTank != None:
            TankFactor = settingWellsTank["TankFactor"]
            TankHeight = settingWellsTank["TankHeight"]

        #pump = well.objects.search_type_pump(wellName)

        if intervalDate == "today" or intervalDate == "Today" or intervalDate == "":
            list_data = RodPumpData.objects.search_today_RPdata(wellName, TankFactor,TankHeight)
        else:
            list_data = RodPumpData.objects.search_by_interval_RPdata(
                intervalDate, wellName, TankFactor,TankHeight)  # .order_by('-DateCreate')
        
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

