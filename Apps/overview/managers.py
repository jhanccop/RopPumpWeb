from datetime import date, datetime, timedelta
from django.db.models.functions import TruncDate, TruncDay
from django.db.models import Sum, Max, F
from django.utils.timezone import now

from unittest import result
from django.db import models

import math


class DataManager(models.Manager):
    def search_by_interval_data(self, interval, wellName):
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]
        print(intervals)
        if len(intervals)==1:
            result = self.filter(
                DateCreate__year=intervals[0].year,
                DateCreate__month=intervals[0].month,
                DateCreate__day=intervals[0].day,
                PumpName__PumpName=wellName
            ).values("DateCreate","MotorCurrent","HeadTemperature","MotorFrequency","MotorTemperature", "PumpIntakePressure").order_by('-DateCreate')
            return result 
        else:
            result = self.filter(
                DateCreate__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__PumpName=wellName
            ).order_by('-DateCreate')
            return result

    def search_today_data(self, interval, wellName):
        Today = date.today()
        result = self.filter(
                DateCreate__year=Today.year,
                DateCreate__month=Today.month,
                DateCreate__day=Today.day,
                PumpName__PumpName=wellName
            ).values("DateCreate","MotorCurrent","HeadTemperature","MotorFrequency","MotorTemperature", "PumpIntakePressure").order_by('-DateCreate')
        return result
    
    def search_today_data_overview(self, interval, wellName):
        Today = date.today()
        result = self.filter(
                DateCreate__year=Today.year,
                DateCreate__month=Today.month,
                DateCreate__day=Today.day,
                PumpName__PumpName=wellName
            ).values("DateCreate","MotorCurrent")
        return result

    def search_by_interval_data_all(self, interval, wellName):
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]
        if len(intervals)==1:
            result = self.filter(
                DateCreate__year=intervals[0].year,
                DateCreate__month=intervals[0].month,
                DateCreate__day=intervals[0].day,
                PumpName__PumpName=wellName
            ).order_by('-DateCreate')
            return result 
        else:
            result = self.filter(
                DateCreate__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__PumpName=wellName
            ).order_by('-DateCreate')
            return result

    def search_today_data_all(self, interval, wellName):
        Today = date.today()
        result = self.filter(
                DateCreate__year=Today.year,
                DateCreate__month=Today.month,
                DateCreate__day=Today.day,
                PumpName__PumpName=wellName
            ).order_by('-DateCreate')
        return result

    def search_last_data(self, wellName):
        result = self.filter(
                PumpName__PumpName=wellName
            ).last()
        return result


class RPDataManager(models.Manager):
    def search_by_interval_RPdata(self, interval, wellName, TankFactor,TankHeight):
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
                "PumpFill",
                "SPM",
                "Recomendation",
                "Diagnosis",
                "TankLevel",
                "Status"
            ).annotate(
                bblOil = F("TankLevel") * TankFactor,
                TankLevelPer = F("TankLevel") * 100 / TankHeight
            ).order_by('-DateCreate')
            return result 
        else:
            result = self.filter(
                DateCreate__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__PumpName=wellName
            ).order_by('-DateCreate')
            return result

    def search_today_RPdata(self,wellName, TankFactor,TankHeight):
        Today = date.today()
        result = self.filter(
                DateCreate__year=Today.year,
                DateCreate__month=Today.month,
                DateCreate__day=Today.day,
                PumpName__PumpName=wellName
            ).values(
                "id",
                "DateCreate",
                "SurfaceLoad",
                "SurfacePosition",
                "DownLoad",
                "DownPosition",
                "RunTime",
                "PumpFill",
                "SPM",
                "Recomendation",
                "Diagnosis",
                "TankLevel",
                "Status"
            ).annotate(
                bblOil = F("TankLevel") * TankFactor,
                TankLevelPer = F("TankLevel") * 100 / TankHeight
            ).order_by('-DateCreate')[:16]
        return result

    def search_trends_fill_SPM_RPdata(self,wellName):
        Today = date.today()
        result = self.filter(
                #DateCreate__year=Today.year,
                DateCreate__month=Today.month,
                #DateCreate__day=Today.day,
                PumpName__PumpName=wellName
            ).values(
                "DateCreate",
                "PumpFill",
                "SPM"
            ).order_by('DateCreate')
        return result
    
    def search_trends_runTime_RPdata(self,wellName):
        Today = date.today()
        now_ = now()
        result = self.filter(
                #DateCreate__year=Today.year,
                PumpName__PumpName=wellName,
                DateCreate__month=Today.month,
                DateCreate__date__range=((now_-timedelta(weeks=52)), now_)
                #DateCreate__day=Today.day, 
            ).annotate(
                date=TruncDay('DateCreate__date')
            ).values(
                "date"
            ).annotate(
                Bydays = Max("RunTime"),
            ).values(
                "date",
                "Bydays"
            ).order_by(
                '-date'
            )
        return result


    def search_trends_runTime_RPdata_or(self,wellName):
        Today = date.today()
        now_ = now()
        result = self.filter(
                #DateCreate__year=Today.year,
                PumpName__PumpName=wellName,
                DateCreate__month=Today.month,
                DateCreate__date__range=((now_-timedelta(weeks=52)), now_)
                #DateCreate__day=Today.day, 
            ).annotate(
                date=TruncDay('DateCreate__date')
            ).values(
                "date"
            ).annotate(
                Bydays = Sum("RunTime"),
            ).values(
                "date",
                "Bydays"
            ).order_by(
                'date'
            )
        return result

class TankDataManager(models.Manager):
    def search_today_Tankdata(self,TankName, TankFactor,TankHeight):
        Today = date.today()
        result = self.filter(
                DateCreate__year = Today.year,
                DateCreate__month = Today.month,
                DateCreate__day = Today.day,
                TankName__TankName = TankName
            ).values(
                "id",
                "DateCreate",
                "OilLevel",
                "WaterLevel",
                "Status"
            ).annotate(
                total = F("OilLevel") + F("WaterLevel"),
                bblOil =  (F("OilLevel") - F("WaterLevel")) * TankFactor,
                TankLevelPer = (F("OilLevel") - F("WaterLevel")) * 100 / TankHeight,
                #inches = math.floor(((TankHeight - F("OilLevel")[0] - F("WaterLevel")[0]) % 1) * 12)
            ).order_by('-DateCreate')
        return result