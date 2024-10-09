from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    TemplateView,
    ListView,
    DetailView
)

from django.db.models import F, Window
from django.db.models.functions import Lag

from Apps.equipment.models import RodPumpWell, Tank, Environmental, VisualSamplingPoint
from Apps.groups.models import Group
from .models import RodPumpData, TankData, EnvironmentalData, CamVidData

from Apps.users.models import User
from Apps.company.models import Company

class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        CompanyName = User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]
        context = super(CompanyMixin, self).get_context_data(**kwargs)
        context['CompanyName'] = CompanyName
        return context

# LIST OVERVIEW DATA (MAIN SCREEN)
class ListOverview(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "data/data_overview.html"
    login_url = reverse_lazy('user_app:user-login')
    # paginate_by = 2

    def get_queryset(self):
        CompanyName = User.objects.get_company_name(self.request.user)[0]["CompanyId__CompanyName"] # name company: CompanyId__CompanyName
        
        # =================  get analyzers data by company =================
        list_wells = RodPumpWell.objects.filter(SupervisorUser__CompanyId__CompanyName = CompanyName)
        
        wells_data = []
        for well_i in list_wells:

            # DATA FROM EQUIPMENT
            tempPayload = {
                'WellName': well_i.WellName,
                'Field': well_i.FieldName,
                'Battery': well_i.BatteryName,
                'AnalyzerStatus': well_i.Status
            }

            # DATA FROM DATA APP
            dataWell = RodPumpData.objects.filter(IdDevice__IdRodPumpWell__WellName = well_i).last()
            if dataWell != None:
                tempPayload['LastUpdate'] = dataWell.DateCreate
                tempPayload['SPM'] = dataWell.SPM
                tempPayload['PumpFillage'] = dataWell.PumpFillage
                tempPayload['Diagnosis'] = dataWell.Diagnosis
                tempPayload['RunTime'] = dataWell.RunTime

                if datetime.now().date() == dataWell.DateCreate.date():
                    tempPayload['CurrentAnalizerContidition'] = dataWell.Status
                else:
                    tempPayload['CurrentAnalizerContidition'] = "No data today"

            wells_data.append(tempPayload)

        # ================= get tank data by company =================
        list_tanks = Tank.objects.search_tank_by_company(CompanyName)
        #print(list_tanks)
        tanks_data = []
        for tank_i in list_tanks:
            tempPayloadTank = {
                'TankName': tank_i["TankName"],
                'GroupName': tank_i["GroupName__GroupName"],
                'Status': tank_i["Status"],
            }

            TankFactor = tank_i["TankFactor"]
            TankHeight = tank_i["TankHeight"]

            dataTank = TankData.objects.search_last_day_Tankdata(tank_i["TankName"],TankFactor,TankHeight)
            if dataTank != None:
                tempPayloadTank['LastUpdate'] = dataTank["DateCreate"]
                tempPayloadTank['Level'] = dataTank["Level"]
                tempPayloadTank['fluidHeigth'] = dataTank["fluidHeigth"]
                tempPayloadTank['bblOil'] = dataTank["bblOil"]
                tempPayloadTank['TankLevelPer'] = dataTank["TankLevelPer"]
                tempPayloadTank['Temperature'] = dataTank["Temperature"]

                if datetime.now().date() == dataTank["DateCreate"].date():
                    tempPayloadTank['CurrentTankContidition'] = dataTank["Status"]
                else:
                    tempPayloadTank['CurrentTankContidition'] = "No data today"

            tanks_data.append(tempPayloadTank)

        # ================= get enviroment data by company =================
        list_environmental = Environmental.objects.search_environmental_by_company(CompanyName)
        environmental_data = []
        for environmental_i in list_environmental:
            tempPayloadenvironmental = {
                'EnvironmentalName': environmental_i["EnvironmentalName"],
                'GroupName': environmental_i["GroupName__GroupName"],
                'Status': environmental_i["Status"],
            }

            dataEnvironmental = EnvironmentalData.objects.search_last_day_environmentalData(environmental_i["EnvironmentalName"])
            if dataEnvironmental != None:
                tempPayloadenvironmental['LastUpdate'] = dataEnvironmental["DateCreate"]
                tempPayloadenvironmental['Humidity1'] = dataEnvironmental["Humidity1"]
                tempPayloadenvironmental['Temperature1'] = dataEnvironmental["Temperature1"]
                tempPayloadenvironmental['AtmosphericPressure1'] = dataEnvironmental["AtmosphericPressure1"]
                tempPayloadenvironmental['Humidity2'] = dataEnvironmental["Humidity2"]
                tempPayloadenvironmental['Temperature2'] = dataEnvironmental["Temperature2"]
                tempPayloadenvironmental['AtmosphericPressure2'] = dataEnvironmental["AtmosphericPressure2"]

                if datetime.now().date() == dataEnvironmental["DateCreate"].date():
                    tempPayloadenvironmental['CurrentTankContidition'] = dataEnvironmental["Status"]
                else:
                    tempPayloadenvironmental['CurrentTankContidition'] = "No data today"

            environmental_data.append(tempPayloadenvironmental)

        # ================= get cameras data by company =================
        list_VisualSampling = VisualSamplingPoint.objects.search_visual_sampling_by_company(CompanyName)
        camera_data = []
        for VisualSampling_i in list_VisualSampling:
            tempPayloadVisualSamplingPoint = {
                'VisualSamplingPointName': VisualSampling_i["VisualSamplingPointName"],
                'GroupName': VisualSampling_i["GroupName__GroupName"],
                'Status': VisualSampling_i["Status"],
            }

            dataCam= CamVidData.objects.search_last_day_camVidDataData(VisualSampling_i["VisualSamplingPointName"])
            if dataCam != None:
                tempPayloadVisualSamplingPoint['LastUpdate'] = dataCam["DateCreate"]
                tempPayloadVisualSamplingPoint['Humidity'] = dataCam["Humidity"]
                tempPayloadVisualSamplingPoint['Temperature'] = dataCam["Temperature"]
                tempPayloadVisualSamplingPoint['volBat'] = dataCam["volBat"]

                if datetime.now().date() == dataCam["DateCreate"].date():
                    tempPayloadVisualSamplingPoint['CurrentTankContidition'] = dataCam["Status"]
                else:
                    tempPayloadVisualSamplingPoint['CurrentTankContidition'] = "No data today"

            camera_data.append(tempPayloadVisualSamplingPoint) 

        allData = {
            "rodpumpData": wells_data,
            "tankData":tanks_data,
            "environmental":environmental_data,
            "visualSamplingPoint":camera_data
        }

        return allData
    
# TANK HISTORICAL VIEW (SECONDARY SCREEN FOR TANK)
class ListTank(LoginRequiredMixin, CompanyMixin, ListView):
    login_url = reverse_lazy('user_app:user-login')
    template_name = "data/data_tank.html"

    def get_queryset(self):
        TankName = self.kwargs['TankName']
        intervalDate = self.request.GET.get("dateKword", '')

        if intervalDate == "today" or intervalDate =="":
            intervalDate = str(date.today() - timedelta(days = 14)) + " to " + str(date.today())

        #settingTank = Tank.objects.filter(TankName__TankName = TankName).values("TankFactor","TankHeight")
        #CompanyName = User.objects.get_company_name(self.request.user)[0]["CompanyId__CompanyName"]
        settingTank = Tank.objects.search_tank_setting(TankName)[0]

        if settingTank != None:
            TankFactor = settingTank["TankFactor"]
            TankHeight = settingTank["TankHeight"]

        payload = {
            "intervalDate": intervalDate,
            "TankName": TankName,
            "data":TankData.objects.search_tankdata_interval(TankName, TankFactor, TankHeight, intervalDate),
            #"last_day_Tankdata": last_day_Tankdata,
        }
        
        """
        if intervalDate == "today" or intervalDate == "":
            last_15_day_Tankdata = TankData.objects.search_last_15_day_Tankdata(TankName, TankFactor, TankHeight)
            
            last_day_Tankdata = TankData.objects.search_last_day_Tankdata(TankName, TankFactor, TankHeight)
            #allData.append(last_15_day_Tankdata)
            #allData.append(last_day_Tankdata)
        else:
            #interval_Tankdata = TankData.objects.search_interval_Tankdata(intervalDate, TankName, TankFactor,TankHeight)  # .order_by('-DateCreate')
            last_15_day_Tankdata = TankData.objects.search_last_15_day_Tankdata_interval(intervalDate, TankName, TankFactor, TankHeight)
            last_day_Tankdata = TankData.objects.search_last_day_Tankdata_interval(intervalDate, TankName, TankFactor, TankHeight)

        payload = {
            "intervalDate": intervalDate,
            "TankName": TankName,
            "last_15_day_Tankdata":last_15_day_Tankdata,
            "last_day_Tankdata": last_day_Tankdata,
        }
        """

        return payload

# SENSOR HISTORICAL VIEW (SECONDARY SCREEN FOR ENVIRONMENSTAL)
class ListSensor(LoginRequiredMixin, CompanyMixin, ListView):
    login_url = reverse_lazy('user_app:user-login')
    template_name = "data/data_sensor.html"

    def get_queryset(self):
        EnvironmentalName = self.kwargs['EnvironmentalName']
        intervalDate = self.request.GET.get("dateKword", '')

        if intervalDate == "today" or intervalDate =="":
            intervalDate = str(date.today() - timedelta(days = 7)) + " to " + str(date.today())

        payload = {
            "intervalDate": intervalDate,
            "EnvironmentalName": EnvironmentalName,
            "data":EnvironmentalData.objects.search_environmentalData_interval(EnvironmentalName,intervalDate),
            #"last_day_Tankdata": last_day_Tankdata,
        }
        
        """
        if intervalDate == "today" or intervalDate == "":
            last_15_day_Tankdata = TankData.objects.search_last_15_day_Tankdata(TankName, TankFactor, TankHeight)
            
            last_day_Tankdata = TankData.objects.search_last_day_Tankdata(TankName, TankFactor, TankHeight)
            #allData.append(last_15_day_Tankdata)
            #allData.append(last_day_Tankdata)
        else:
            #interval_Tankdata = TankData.objects.search_interval_Tankdata(intervalDate, TankName, TankFactor,TankHeight)  # .order_by('-DateCreate')
            last_15_day_Tankdata = TankData.objects.search_last_15_day_Tankdata_interval(intervalDate, TankName, TankFactor, TankHeight)
            last_day_Tankdata = TankData.objects.search_last_day_Tankdata_interval(intervalDate, TankName, TankFactor, TankHeight)

        payload = {
            "intervalDate": intervalDate,
            "TankName": TankName,
            "last_15_day_Tankdata":last_15_day_Tankdata,
            "last_day_Tankdata": last_day_Tankdata,
        }
        """

        return payload

# SENSOR HISTORICAL VIEW (SECONDARY SCREEN FOR CAMERAS)
class ListCamera(LoginRequiredMixin, CompanyMixin, ListView):
    login_url = reverse_lazy('user_app:user-login')
    template_name = "data/data-camera.html"

    def get_queryset(self):
        VisualSamplingPointName = self.kwargs['VisualSamplingPointName']
        intervalDate = self.request.GET.get("dateKword", '')

        if intervalDate == "today" or intervalDate =="":
            intervalDate = str(date.today() - timedelta(days = 2)) + " to " + str(date.today())

        payload = {
            "intervalDate": intervalDate,
            "VisualSamplingPointName": VisualSamplingPointName,
            "data":CamVidData.objects.search_camVidDataData_interval(VisualSamplingPointName,intervalDate),
            #"last_day_Tankdata": last_day_Tankdata,
        }


        return payload

class DetailCamera(LoginRequiredMixin, CompanyMixin, DetailView):
    login_url = reverse_lazy('user_app:user-login')
    template_name = "data/data-camera-detail.html"
    model = CamVidData

    def get_queryset(self):
        return super().get_queryset().annotate(
            volBat = F("VoltageBattery") * 0.01,
            volPan = F("VoltagePanel") * 0.01,
            rainCounter = F("RainCounter"),
            lastRainCounter=Window(
                expression=Lag('rainCounter'),
                order_by=F('DateCreate').asc()
            ),
            ppt = (F("rainCounter") - F("lastRainCounter")) * 0.3,
            # Add more annotations as needed
        )

class SuccessView(TemplateView):
    template_name = "home/home.html"