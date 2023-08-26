from django.db import models

class WellManager(models.Manager):

    def search_type_pump(self, wellName):
        result = self.filter(
            PumpName=wellName
        ).values("PumpType")
        return result[0]

    def search_id_pump(self, wellName):
        result = self.filter(
            PumpName=wellName
        ).values("id").first()
        return result

    def search_info_pump(self, wellName):
        result = self.filter(
            PumpName=wellName
        ).first()
        return result

