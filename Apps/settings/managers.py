from datetime import date, datetime, timedelta
from django.db.models import Sum

#from unittest import result
from django.db import models

class SettingManager(models.Manager):
    # =========================== all devices table ========================
    def search_all(self, company):
        result = self.filter(
            PumpName__UserAuthor__CompanyName=company
        ).values("id",
                "DeviceName",
                "PumpName__PumpName",
                "DeviceType",
                "Available",
                "MacAddress",
                "IpAddress",
                "Status",
                "TimeOn",
                "TimeOff",
                "ThresholdAlert1",
                "ThresholdAlert2",
                "ThresholdStop",
                "TankHeight",
                "TankFactor"
                
                 ).order_by('PumpName')
        return result

    