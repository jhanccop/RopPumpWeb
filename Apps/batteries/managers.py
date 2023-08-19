from django.db import models

class BatteryManager(models.Manager):

    def list_batteries_by_companies(self, company_id):
        result = self.filter(
                Company__id=company_id
            ).values("BatteryName")
        return result