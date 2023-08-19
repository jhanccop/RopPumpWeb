from django.db import models

class FieldManager(models.Manager):

    def list_fields_by_companies(self, company_id):
        result = self.filter(
                Company__id=company_id
            ).values("FieldName")
        return result