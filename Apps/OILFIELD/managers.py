from django.db import models
from django.db.models import Prefetch, Q


# ---------------------------------------------------------------------------
# BatteryManager
# ---------------------------------------------------------------------------

class BatteryManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )


# ---------------------------------------------------------------------------
# TankManager
# ---------------------------------------------------------------------------

class TankManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )

    def get_by_battery(self, battery_id):
        return self.filter(Battery_id=battery_id)


# ---------------------------------------------------------------------------
# WellManager
# ---------------------------------------------------------------------------

class WellManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )

    def get_by_battery(self, battery_id):
        return self.filter(Battery_id=battery_id)

    def get_producing(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name,
            Status='producing',
        )

    def get_with_latest_reading(self, company_name):
        from Apps.OILFIELD.models import PumpingReading
        return (
            self.get_by_company(company_name)
            .prefetch_related(
                Prefetch(
                    'pumping_readings',
                    queryset=PumpingReading.objects.order_by('-DateCreate'),
                    to_attr='latest_readings',
                )
            )
        )


# ---------------------------------------------------------------------------
# WellDailyProductionManager
# ---------------------------------------------------------------------------

class WellDailyProductionManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Well__Owner__CompanyId__CompanyName=company_name
        )

    def get_by_well(self, well_id):
        return self.filter(Well_id=well_id)

    def get_by_date_range(self, company_name, date_from, date_to):
        return self.filter(
            Well__Owner__CompanyId__CompanyName=company_name,
            OperativeDate__range=(date_from, date_to),
        )


# ---------------------------------------------------------------------------
# OperationalAlertManager
# ---------------------------------------------------------------------------

class OperationalAlertManager(models.Manager):

    def get_active_by_company(self, company_name):
        return self.filter(
            Q(Well__Owner__CompanyId__CompanyName=company_name)
            | Q(Tank__Owner__CompanyId__CompanyName=company_name),
            Status='active',
        ).distinct()

    def get_critical(self, company_name):
        return self.filter(
            Q(Well__Owner__CompanyId__CompanyName=company_name)
            | Q(Tank__Owner__CompanyId__CompanyName=company_name),
            Status='active',
            Severity__in=('high', 'critical'),
        ).distinct()

    def get_by_well(self, well_id):
        return self.filter(Well_id=well_id)
