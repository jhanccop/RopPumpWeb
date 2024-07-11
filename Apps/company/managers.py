from django.db import models

class CompanyManager(models.Manager):
    def list_companies(self, company):
        return self.all()

    def get_company_name(self, company_id):
        result = self.filter(
                id = company_id
            ).values("CompanyName")
        return result
        
