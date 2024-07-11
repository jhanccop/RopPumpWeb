from django.db import models
from django.db.models import Sum, Max, F, Avg, Subquery, Count, DateField, Q, OuterRef, FilteredRelation

class WellManager(models.Manager):

    def search_type_pump(self, WellName):
        result = self.filter(
            PumpName=WellName
        ).values("PumpType")
        return result[0]

    def search_id_pump(self, WellName):
        result = self.filter(
            PumpName=WellName
        ).values("id").first()
        return result

    def search_info_pump(self, WellName):
        result = self.filter(
            PumpName=WellName
        ).first()
        return result
    
    def search_rodpump_by_company(self, CompanyName):
        result = self.filter(
            Owner__CompanyId__CompanyName = CompanyName
        ).values(
                 "WellName",
                 "FieldName__FieldName",
                 "BatteryName__BatteryName",
                 "GroupName__GroupName",
                 "EngineType",
                 "Status",
                 )
        return result

class TankManager(models.Manager):
    def search_tank_by_company(self, CompanyName):
        result = self.filter(
            Owner__CompanyId__CompanyName = CompanyName
        ).values(
            "id",
            "TankName",
            "FieldName__FieldName",
            "BatteryName__BatteryName",
            "GroupName__GroupName",
            "Status",
            "TankFactor",
            "TankHeight",
        )
        return result
    
    def search_tank_by_company_complete(self, CompanyName):
        result = self.filter(
            SupervisorUser__CompanyId__CompanyName = CompanyName
        ).values(
            "id"
            "TankName",
            "FieldName__FieldName",
            "BatteryName__BatteryName",
            "GroupName",
            "LonLocation",
            "LatLocation",
            "Status",
            "SupervisorUser",
            "TankFactor",
            "TankHeight",
            "WellsAssigned"
        )
        return result

    def search_tank_setting(self, TankName):
        result = self.filter(
            TankName = TankName
        ).values(
            "TankFactor",
            "TankHeight",
        )
        return result

class EnvironmentalManager(models.Manager):
    def search_environmental_by_company(self, CompanyName):
        result = self.filter(
            Owner__CompanyId__CompanyName = CompanyName
        ).values(
            "id",
            "EnvironmentalName",
            "GroupName__GroupName",
            "Status",
        )
        return result