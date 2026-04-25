from django.db import models
from django.db.models import Max, Count, Sum
from django.db.models.functions import Coalesce


class CameraStationManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )

    def list_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        ).values(
            'id', 'StationName', 'Description',
            'Latitude', 'Longitude', 'Altitude',
            'Status',
        )


class CameraCaptureManager(models.Manager):

    def get_by_station(self, station_id):
        return (
            self.filter(Station__id=station_id)
            .prefetch_related('detections')
            .order_by('-DateCapture')
        )

    def get_latest_by_station(self, station_id):
        return (
            self.filter(Station__id=station_id)
            .prefetch_related('detections')
            .order_by('-DateCapture')
            .first()
        )

    def get_range_by_station(self, station_id, date_from, date_to):
        return self.filter(
            Station__id=station_id,
            DateCapture__date__gte=date_from,
            DateCapture__date__lte=date_to,
        ).order_by('DateCapture')

    def get_range_by_company(self, company_name, date_from, date_to, species=None):
        qs = self.filter(
            Station__Owner__CompanyId__CompanyName=company_name,
            DateCapture__date__gte=date_from,
            DateCapture__date__lte=date_to,
        ).select_related('Station').prefetch_related('detections')
        if species:
            qs = qs.filter(detections__Species__icontains=species).distinct()
        return qs.order_by('Station__StationName', 'DateCapture')

    def get_latest_per_station(self, company_name):
        latest_ids = (
            self.filter(Station__Owner__CompanyId__CompanyName=company_name)
            .values('Station')
            .annotate(last_id=Max('id'))
            .values('last_id')
        )
        return (
            self.filter(id__in=latest_ids)
            .select_related('Station')
            .prefetch_related('detections')
            .order_by('Station__StationName')
        )

    def species_summary(self, company_name, date_from=None, date_to=None):
        from Apps.FAUNA.camera.models import CaptureDetection
        qs = CaptureDetection.objects.filter(
            Capture__Station__Owner__CompanyId__CompanyName=company_name
        )
        if date_from:
            qs = qs.filter(Capture__DateCapture__date__gte=date_from)
        if date_to:
            qs = qs.filter(Capture__DateCapture__date__lte=date_to)
        return (
            qs.values('Species')
            .annotate(captures=Count('Capture', distinct=True), total_individuals=Sum('Count'))
            .order_by('-captures')
        )
