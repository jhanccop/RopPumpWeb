from django.db import models

class GroupManager(models.Manager):

    def list_gropus_by_companies(self, company_id):
        result = self.filter(
                Company__id=company_id
            ).values("GroupName")
        return result