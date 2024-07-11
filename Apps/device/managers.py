from django.db import models

class TankDeviceManager(models.Manager):
    def search_tank_devices(self, company):
        result = self.filter(
            Owner__CompanyId__CompanyName = company
        ).values("id",
                "DeviceName",
                "DeviceMacAddress",
                "DeviceStatus",
                "SamplingRate",
                "IdTank__TankName",
                )
        return result

class EnvironmentalDeviceManager(models.Manager):
    def search_Environmental_devices(self, company):
        result = self.filter(
            Owner__CompanyId__CompanyName = company
        ).values("id",
                "DeviceName",
                "DeviceMacAddress",
                "DeviceStatus",
                "SamplingRate",
                "IdEnvironmental__EnvironmentalName",
                )
        return result

class AnalyzerDeviceManager(models.Manager):
    def search_Analyzer_devices(self, company):
        result = self.filter(
            Owner__CompanyId__CompanyName = company
        ).values("id",
                "DeviceName",
                "DeviceMacAddress",
                "DeviceStatus",
                "SamplingRate",
                "IdRodPumpWell__WellName",
                )
        return result