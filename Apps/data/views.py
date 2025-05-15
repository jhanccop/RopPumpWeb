import numpy as np
import json
from datetime import date, datetime, timedelta
from django.http import JsonResponse
from django.middleware.csrf import get_token

from django.http import UnreadablePostError

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    View
)

from django.db.models import F, Window
from django.db.models.functions import Lag

from Apps.equipment.models import (
    RodPumpWell, 
    Tank,
    Environmental,
    VisualSamplingPoint,
    InsectMonitoring
)

from Apps.location.models import (
    Location
)

from Apps.device.models import TrapView, WeatherStation

from Apps.groups.models import Group
from .models import (
    RodPumpData,
    TankData,
    EnvironmentalData,
    CamVidData,
    TrapViewData,
    WeatherStationData
)

from Apps.users.models import User
from Apps.company.models import Company

from .serializers import TrapViewDataSerializer, WeatherStationDataSerializer

class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        CompanyName = User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]
        context = super(CompanyMixin, self).get_context_data(**kwargs)
        context['CompanyName'] = CompanyName
        return context

# API FOR SAVE DATA
class CsrfTokenView(APIView):
    def get(self, request):
        return JsonResponse({'csrfToken': get_token(request)})

class ApiPost(APIView):
    try:
        queryset = TrapViewData.objects.all()
        serializer_class = TrapViewDataSerializer

        def post(self, request, *args, **kwargs):
            data = json.loads(request.body)

            ID, OBJETIVE = self.IdDeviceMac(data['DeviceMacAddress'])
            ND, IMGBOOL = self.nnProcess(data['img64'])

            data['IdDevice'] = ID

            data['Humidity'] = float(data['Humidity'])
            data['Temperature'] = float(data['Temperature'])
            data['VoltageBattery'] = float(data['VoltageBattery'])

            data['Objective'] = OBJETIVE
            data['nDetected'] = ND
            data['img_bool'] = IMGBOOL
            
            data['Status'] = self.batStatus(data['VoltageBattery'])

            del(data["DeviceMacAddress"])

            serializer = self.serializer_class(data = data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        
        def IdDeviceMac(self, valor):
            result = TrapView.objects.get(DeviceMacAddress = valor)
            return result.id, result.Objective
        
        def nnProcess(self, valor):
            ND = 0
            IB = True
            if valor == None or valor == "":
                IB = False
            else:
                ND = 4
            return ND, IB
        
        def batStatus(self, valor):
            result = '0'
            if float(valor) < 3.6:
                result = '1'
            return result
    
    except UnreadablePostError:
        print("error en post")

class WeatherStationApiPost(APIView):
    try:
        queryset = WeatherStationData.objects.all()
        serializer_class = WeatherStationDataSerializer

        def post(self, request, *args, **kwargs):
            data = json.loads(request.body)

            ID = self.IdDeviceMac(data['DeviceMacAddress'])

            data['IdDevice'] = ID

            if data.get('Humidity',"") == "nan" or "":
                data['Humidity'] = float(data['Humidity'])
            if data.get('Temperature',"") == "nan" or "":
                data['Temperature'] = float(data['Temperature'])
            if data.get('WindVelocity',"") == "nan" or "":
                data['WindVelocity'] = float(data['WindVelocity'])
            if data.get('WindDirection',"") == "nan" or "":
                data['WindDirection'] = float(data['WindDirection'])
            if data.get('RainCounter',"") == "nan" or "":
                data['RainCounter'] = int(data['RainCounter'])
            if data.get('Radiation',"") == "nan" or "":
                data['Radiation'] = float(data['Radiation'])

            data['VoltageBattery'] = float(data['VoltageBattery'])
            data['Status'] = self.batStatus(data['VoltageBattery'])

            del(data["DeviceMacAddress"])

            serializer = self.serializer_class(data = data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        
        def IdDeviceMac(self, valor):
            result = WeatherStation.objects.get(DeviceMacAddress = valor)
            return result.id
        
        def batStatus(self, valor):
            result = '0'
            if float(valor) < 3.6:
                result = '1'
            return result
    
    except UnreadablePostError:
        print("error en post")

# OVERVIEW by LOCATION (MAIN SCREEN)
class OverviewAllLocation(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "data/overview-location.html"
    login_url = reverse_lazy('user_app:user-login')

    def get_queryset(self):
        # GET COMPANY NAME FROM USER LOGING
        CompanyName = self.request.user.CompanyId

        list_locations = Location.objects.filter(Field__Company__CompanyName = CompanyName)
        overviewData = []

        for location in list_locations:
            TVD = TrapViewData.objects.get_last_TrapViewData_by_locations(location)
            overviewData.append({"TVD":TVD})
        allData = {
            "locations": list_locations,
            "trapView": overviewData,
        }

        return allData
    
# =================== MONITOREO FAUNA POR UBICACION PUBLICO FREE (MAIN SCREEN) ===================
class MonitoreoFaunaPorUbicacionView(ListView):
    template_name = "data/monitoreo-fauna.html"
    context_object_name = "dev"

    def get_queryset(self):
        location = self.kwargs['ubicacion']
        intervalDate = self.request.GET.get("dateKword", '')

        if intervalDate == "today" or intervalDate =="":
            intervalDate = str(date.today() - timedelta(days = 2)) + " to " + str(date.today())

        WS = WeatherStationData.objects.get_weatherStation_data_by_locations(location, intervalDate)
        TV = TrapViewData.objects.get_trapView_data_by_locations(location, intervalDate)
 
        allData = {
            "intervalDate": intervalDate,
            "location": location,
            "WS": WS,
            "TV": TV,
        }

        return allData

# OVERVIEW by LOCATION (MAIN SCREEN)
class OverviewByLocation(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "data/overview-location.html"
    login_url = reverse_lazy('user_app:user-login')

    def get_queryset(self):
        location = self.kwargs['pk']
        intervalDate = self.request.GET.get("dateKword", '')

        if intervalDate == "today" or intervalDate =="":
            intervalDate = str(date.today() - timedelta(days = 7)) + " to " + str(date.today())

        TVD = TrapViewData.objects.get_last_TrapViewData_by_locations(location, intervalDate)
        ATVD = TrapViewData.objects.get_all_TrapViewData_by_locations(location, intervalDate)
        #WS = 
        #GW = 
        #CON = 
 
        allData = {
            "intervalDate": intervalDate,
            "location": location,
            "TVD": TVD,
            "ATVD": ATVD,
        }

        return allData

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

        # ================= get insect monitoring by company =================

        listTrapView = TrapViewData.objects.get_last_data_insect_by_company(CompanyName)

        allData = {
            "rodpumpData": wells_data,
            "tankData":tanks_data,
            "environmental":environmental_data,
            "visualSamplingPoint":camera_data,
            "insects":listTrapView
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

# SENSOR HISTORICAL VIEW (SECONDARY SCREEN FOR ENVIRONMENTAL)
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

class ListTrapView(LoginRequiredMixin, CompanyMixin, ListView):
    login_url = reverse_lazy('user_app:user-login')
    template_name = "data/data-trapView.html"

    def get_queryset(self):
        name = self.kwargs['name']
        intervalDate = self.request.GET.get("dateKword", '')

        if intervalDate == "today" or intervalDate =="":
            intervalDate = str(date.today() - timedelta(days = 2)) + " to " + str(date.today())

        payload = {
            "intervalDate": intervalDate,
            "name": name,
            "data":TrapViewData.objects.search_TrapViewData_interval(name,intervalDate),
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

class DetailTrapView(LoginRequiredMixin, CompanyMixin, DetailView):
    login_url = reverse_lazy('user_app:user-login')
    template_name = "data/data-trapView-detail.html"
    model = TrapViewData

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

# ================== VIEW FOR OVERVIEW OIL AND GAS ==================
class ListOilOverview(LoginRequiredMixin, CompanyMixin, ListView):
    # LIST EQUIPMENT
    login_url = reverse_lazy('user_app:user-login')
    template_name = "data/list-oil-overview.html"
    context_object_name = 'devices'

    def get_queryset(self):
        idCompany = self.request.user.CompanyId.id
        # --  get wells by company ---
        list_wells = RodPumpWell.objects.search_rodpump_by_id_company(idCompany)
        wells_data = []
        for well_i in list_wells:
            # DATA FROM EQUIPMENT
            tempPayload = {
                'WellName': well_i["WellName"],
                'Field': well_i["FieldName__FieldName"],
                'Battery': well_i["BatteryName__BatteryName"],
                'Lat': well_i["LatLocation"],
                'Long': well_i["LonLocation"]
            }

            # DATA FROM DATA APP

            dataWell = RodPumpData.objects.search_last_RPdata(well_i["WellName"])

            if dataWell != None:
                wells_data.append(dataWell)

            #dataWell = RodPumpData.objects.filter(IdDevice__IdRodPumpWell__WellName = well_i["WellName"]).last()
            #if dataWell != None:
            #    tempPayload['LastUpdate'] = dataWell.DateCreate
            #    tempPayload['SPM'] = dataWell.SPM
            #    tempPayload['PumpFillage'] = dataWell.PumpFillage
            #    tempPayload['Diagnosis'] = dataWell.Diagnosis
            #    tempPayload['RunTime'] = dataWell.RunTime

            #    if datetime.now().date() == dataWell.DateCreate.date():
            #        tempPayload['CurrentAnalizerContidition'] = dataWell.Status
            #    else:
            #        tempPayload['CurrentAnalizerContidition'] = "No data today"

            #wells_data.append(dataWell)

        # ================= get tank data by company =================
        list_tanks = Tank.objects.search_tank_by_id_company(idCompany)
        #print(list_tanks)
        tanks_data = []
        for tank_i in list_tanks:
            tempPayloadTank = {
                'TankName': tank_i["TankName"],
                'Field': well_i["FieldName__FieldName"],
                'Battery': well_i["BatteryName__BatteryName"],
                'Lat': well_i["LatLocation"],
                'Long': well_i["LonLocation"]
            }

            TankFactor = tank_i["TankFactor"]
            TankHeight = tank_i["TankHeight"]
            #dataTank = TankData.objects.search_last_day_Tankdata(tank_i["TankName"],TankFactor,TankHeight)
            dataTank = TankData.objects.search_last_TankData(tank_i["TankName"],TankFactor,TankHeight)

            if dataTank != None:
                tanks_data.append(dataTank)
            
            #if dataTank != None:
            #    tempPayloadTank['LastUpdate'] = dataTank["DateCreate"]
            #    tempPayloadTank['Level'] = dataTank["Level"]
            #    tempPayloadTank['fluidHeigth'] = dataTank["fluidHeigth"]
            #    tempPayloadTank['bblOil'] = dataTank["bblOil"]
            #    tempPayloadTank['TankLevelPer'] = dataTank["TankLevelPer"]
            #    tempPayloadTank['Temperature'] = dataTank["Temperature"]

            #    if datetime.now().date() == dataTank["DateCreate"].date():
            #        tempPayloadTank['CurrentTankContidition'] = dataTank["Status"]
            #    else:
            #        tempPayloadTank['CurrentTankContidition'] = "No data today"

            

        allData = {
            "rodpumpData": wells_data,
            "tankData":tanks_data,
        }

        return allData

class ListDataRodPump(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = "data/socked-rod-pump.html"
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'data'

    def get_queryset(self):
        wellName = self.kwargs['WellName']
        intervalDate = self.request.GET.get("dateKword", '')

        if intervalDate == "today" or intervalDate == "Today" or intervalDate == "":
            list_data = RodPumpData.objects.search_today_RPdata(wellName)
        else:
            list_data = RodPumpData.objects.search_by_interval_RPdata(intervalDate,wellName) #.order_by('-DateCreate')
        
        payload = {
            "name":wellName,
            "date":intervalDate,
            #"type":pump["PumpType"],
            "data":list_data
            }
                
        return payload

class SuccessView(TemplateView):
    template_name = "home/home.html"