from datetime import date, datetime, timedelta

from unittest import result
from django.db import models

class ProductionManager(models.Manager):
    def search_by_interval(self, interval, wellName):
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]
        print(intervals)
        if len(intervals)==1:
            result = self.filter(
                DateCreate__year=intervals[0].year,
                DateCreate__month=intervals[0].month,
                DateCreate__day=intervals[0].day,
                PumpName__PumpName=wellName
            ).values("id","DateCreate","UserAuthor","OilProd","WaterProd").order_by('-DateCreate')
            return result 
        else:
            result = self.filter(
                DateCreate__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__PumpName=wellName
            ).order_by('-DateCreate')
            return result

    def search_today(self,wellName):
        Today = date.today()
        result = self.filter(
                DateCreate__year=Today.year,
                DateCreate__month=Today.month,
                #DateCreate__day=Today.day,
                PumpName__PumpName=wellName
            ).values("id","DateCreate","UserAuthor","OilProd","WaterProd").order_by('-DateCreate')
        return result