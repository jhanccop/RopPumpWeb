from django.db import models
from django.db.models import Prefetch


class TransformerManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )

    def get_operational(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name,
            Status='operational',
        )

    def get_with_latest_reading(self, company_name):
        from Apps.TRANSFORMADOR.models import ElectricalReading
        return (
            self.get_by_company(company_name)
            .prefetch_related(
                Prefetch(
                    'readings',
                    queryset=ElectricalReading.objects.order_by('-DateCreate'),
                    to_attr='latest_readings',
                )
            )
        )


class SubstationManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )


class AlertManager(models.Manager):

    def get_active_by_company(self, company_name):
        return self.filter(
            Transformer__Owner__CompanyId__CompanyName=company_name,
            Status='active',
        )

    def get_by_transformer(self, transformer_id):
        return self.filter(Transformer_id=transformer_id)

    def get_critical(self, company_name):
        return self.filter(
            Transformer__Owner__CompanyId__CompanyName=company_name,
            Status='active',
            Severity__in=('critical', 'emergency'),
        )
