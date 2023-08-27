from datetime import date, datetime, timedelta
from django.db.models import Sum

#from unittest import result
from django.db import models

class ProductionManager(models.Manager):
    # =========================== SPECIFIC WELL table ========================
    def search_by_interval(self, interval, wellName):
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]
        print(intervals)
        if len(intervals)==1:
            result = self.filter(
                DateTest__year=intervals[0].year,
                DateTest__month=intervals[0].month,
                DateTest__day=intervals[0].day,
                PumpName__PumpName=wellName
            ).values("id","DateTest","UserAuthor__UserName","OilProd","WaterProd").order_by('-DateTest')
            return result 
        else:
            result = self.filter(
                DateTest__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__PumpName=wellName
            ).values("id","DateTest","UserAuthor__UserName","OilProd","WaterProd").order_by('-DateTest')
            return result

    def search_today(self,wellName):
        Today = date.today()
        result = self.filter(
                DateTest__year=Today.year,
                DateTest__month=Today.month,
                #DateCreate__day=Today.day,
                PumpName__PumpName=wellName
            ).values("id","DateTest","UserAuthor__UserName","OilProd","WaterProd").order_by('-DateTest')
        return result
    
    # =========================== MAIN table ========================
    def search_by_interval_all(self, interval, company):
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]
        print(intervals)
        if len(intervals)==1:
            result = self.filter(
                DateTest__year=intervals[0].year,
                DateTest__month=intervals[0].month,
                DateTest__day=intervals[0].day,
                PumpName__UserAuthor__CompanyName=company
            ).values("id","PumpName__PumpName","DateTest","UserAuthor__UserName","OilProd","WaterProd").order_by('-DateCreate')
            return result 
        else:
            result = self.filter(
                DateTest__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__UserAuthor__CompanyName=company
            ).values("id","PumpName__PumpName","DateTest","UserAuthor__UserName","OilProd","WaterProd").order_by('-DateCreate')
            return result

    def search_today_all(self,company):
        Today = date.today()
        result = self.filter(
                DateTest__year=Today.year,
                DateTest__month=Today.month,
                #DateCreate__day=Today.day,
                PumpName__UserAuthor__CompanyName=company
            ).values("id","PumpName__PumpName","DateTest","UserAuthor__UserName","OilProd","WaterProd").order_by('-DateCreate')
        return result
    
    # =========================== MAIN graphs ========================

    def search_by_interval_all_plot(self, interval, company):
        Intervals = interval.split(' to ')
        intervals = [ datetime.strptime(dt,"%Y-%m-%d") for dt in Intervals]
        print(intervals)
        if len(intervals)==1:
            result = self.filter(
                DateTest__year=intervals[0].year,
                DateTest__month=intervals[0].month,
                DateTest__day=intervals[0].day,
                PumpName__UserAuthor__CompanyName=company
            ).values("PumpName__PumpName").annotate(
                total_oil = Sum("OilProd"),
                total_water = Sum("WaterProd"))
            return result 
        else:
            result = self.filter(
                DateTest__range=(intervals[0],intervals[1]+timedelta(days=1)),
                PumpName__UserAuthor__CompanyName=company
            ).values("PumpName__PumpName").annotate(
                total_oil = Sum("OilProd"),
                total_water = Sum("WaterProd"))
            return result

    def search_today_all_plot(self,company):
        Today = date.today()
        result = self.filter(
                DateTest__year=Today.year,
                DateTest__month=Today.month,
                #DateCreate__day=Today.day,
                PumpName__UserAuthor__CompanyName=company
            ).values("PumpName__PumpName").annotate(
                total_oil = Sum("OilProd"),
                total_water = Sum("WaterProd"))
        return result