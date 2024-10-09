import math
from fractions import Fraction

from datetime import date, datetime, timedelta
from django.db.models import Sum, Max, F, Avg, Window, Count, DateField, Q
from django.db.models.functions import Lag
import itertools

from django.db.models.functions import TruncDate, ExtractDay, Upper

from django.db import models


class RPDataManager(models.Manager):
    def search_by_interval_RPdata(self, interval, wellName):
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]
        #print(intervals)
        if len(intervals)==1:
            result = self.filter(
                DateCreate__year=intervals[0].year,
                DateCreate__month=intervals[0].month,
                DateCreate__day=intervals[0].day,
                PumpName__PumpName=wellName
            ).values(
                "DateCreate",
                "SurfaceLoad",
                "SurfacePosition",
                "RunTime",
                "PumpFillage",
                "SPM",
                "Recomendation",
                "Diagnosis",
                "Status"
            ).order_by('-DateCreate')
            return result 
        else:
            result = self.filter(
                DateCreate__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__PumpName=wellName
            ).order_by('-DateCreate')
            return result
        
class TankDataManager(models.Manager):
    # MAIN SEARCH DATA
    def search_tankdata_interval(self,TankName, TankFactor,TankHeight, interval):

        def floatEng(num):
            num = float(num)
            N = math.modf(num)
            ft = int(N[1]) # ft integer 
            M = math.modf(N[0] * 12) 
            inch = int(M[1]) # in integer 
            inF = round(M[0]/0.125) * 0.125
            frac = Fraction(inF).limit_denominator(10)
            if frac == 1:
                frac = 0
                inch = inch + 1
            return str(ft) + "ft - " + str(inch) + "in " + str(frac)
        
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]

        # =========== Creacion de rango de fechas ===========
        rangeDate = [intervals[0] - timedelta(days = 1),None]
        if len(intervals) == 1:
            rangeDate[1] = intervals[0] + timedelta(days = 1)
        else:
            rangeDate[1] = intervals[1] + timedelta(days = 1)

        LastDay = self.filter(
            IdDevice__IdTank__TankName = TankName
            ).values('DateCreate').order_by('DateCreate').last()

        if LastDay == None:
            return None
        LastDay = LastDay["DateCreate"]

        dateTimes = self.filter(
                DateCreate__range = rangeDate,
                IdDevice__IdTank__TankName = TankName,
            ).annotate(
                day=TruncDate('DateCreate', output_field = DateField()),
            ).values(
                'day'
            ).annotate(
                DateTime=Max('DateCreate'),
                #dayLevel = Sum('Level')
            ).values('DateTime').order_by('-DateTime')
        
        ddtt = [i["DateTime"] for i in dateTimes]
        result = self.filter(
                DateCreate__in = ddtt,
                IdDevice__IdTank__TankName = TankName,
            ).annotate(
                Date = TruncDate('DateCreate', output_field = DateField()),
                datetime = F('DateCreate'),
                #ff = Sum(floatEng('Level')),
                fluidLevel = (TankHeight - F("Level") ) * 3.28084,
                oilBbl = (TankHeight - F("Level")) * TankFactor,
            ).values("Date","datetime","fluidLevel","oilBbl","Temperature","Status").order_by('-Date')
        for i in result:
            i["ft"] = floatEng(i["fluidLevel"])
        return result
       
    # SEARCH LAST DAY
    def search_last_day_Tankdata(self,TankName, TankFactor,TankHeight):

        def floatEng(num):
            num = float(num)
            N = math.modf(num)
            ft = N[1] # ft integer 
            M = math.modf(N[0] * 12) 
            inch = M[1] # in integer 
            return str(ft) + " ft " + str(inch) + " - " + str(Fraction(M[0]).limit_denominator(10)) + " in"

        LastDay = self.filter(
            IdDevice__IdTank__TankName = TankName
            ).values('DateCreate').order_by('DateCreate').last()

        if LastDay == None:
            return None
        LastDay = LastDay["DateCreate"]

        result = self.filter(
                DateCreate__gte = LastDay,
                IdDevice__IdTank__TankName = TankName
            ).values(
                "DateCreate",
                "Level",
                "Temperature",
                "Status"
            ).annotate(
                fluidHeigth = (TankHeight - F("Level") ) * 3.28084 ,
                #fluid = F(floatEng('Level')),
                bblOil = (TankHeight - F("Level")) * TankFactor,
                TankLevelPer = (TankHeight - F("Level")) * 100 / TankHeight,
            ).order_by('-DateCreate').last()
        result["ft"] = floatEng(result['Level'])
        return result

class EnvironmentalDataManager(models.Manager):
    # MAIN SEARCH DATA
    def search_environmentalData_interval(self,Name, interval):

        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]

        # =========== Creacion de rango de fechas ===========
        rangeDate = [intervals[0] - timedelta(days = 1),None]
        if len(intervals) == 1:
            rangeDate[1] = intervals[0] + timedelta(days = 1)
        else:
            rangeDate[1] = intervals[1] + timedelta(days = 1)

        result = self.filter(
            DateCreate__range = rangeDate,
            IdDevice__IdEnvironmental__EnvironmentalName = Name
        ).order_by('-DateCreate')

        return result
    
        # SEARCH LAST DAY
    def search_last_day_environmentalData(self,Name):

        result = self.filter(
                IdDevice__IdEnvironmental__EnvironmentalName = Name
            ).values(
                "DateCreate",
                "Humidity1",
                "Temperature1",
                "AtmosphericPressure1",
                "Humidity2",
                "Temperature2",
                "AtmosphericPressure2",
                "Status"
            ).order_by('DateCreate').last()
        return result
    
class CamVidDataManager(models.Manager):
    # MAIN SEARCH DATA
    def search_camVidDataData_interval(self,Name, interval):

        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]

        # =========== Creacion de rango de fechas ===========
        rangeDate = [intervals[0] - timedelta(days = 1),None]
        if len(intervals) == 1:
            rangeDate[1] = intervals[0] + timedelta(days = 1)
        else:
            rangeDate[1] = intervals[1] + timedelta(days = 1)

        result = self.filter(
            DateCreate__range = rangeDate,
            IdDevice__IdVisualSamplingPoint__VisualSamplingPointName = Name
        ).annotate(
            volBat = F("VoltageBattery") * 0.01,
            volPan = F("VoltagePanel") * 0.01,
            lastRainCounter=Window(
                expression=Lag('RainCounter'),
                order_by=F('DateCreate').asc()
            ),
            ppt = (F("RainCounter") - F("lastRainCounter")) * 0.3,
        ).order_by('-DateCreate')

        return result
    
        # SEARCH LAST DAY
    def search_last_day_camVidDataData(self,Name):

        result = self.filter(
                IdDevice__IdVisualSamplingPoint__VisualSamplingPointName = Name
            ).values(
                "DateCreate",
                "Humidity",
                "Temperature",
                "VoltageBattery",
                "Status"
            ).annotate(
                volBat = F("VoltageBattery") * 0.01,
                volPan = F("VoltagePanel") * 0.01,
                lastRainCounter=Window(
                    expression=Lag('RainCounter'),
                    order_by=F('DateCreate').asc()
                ),
                ppt = (F("RainCounter") - F("lastRainCounter")) * 0.3,
                ).order_by('DateCreate').last()
        return result
    

