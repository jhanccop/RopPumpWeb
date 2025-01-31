from django.db import models

class LocationManager(models.Manager):

    def list_locations_by_companies(self, company_id):
        result = self.filter(
                Company__id=company_id
            ).values("LocationName")
        return result