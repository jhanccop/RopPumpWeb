import json
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from Apps.users.mixins import AppAccessMixin, AdminRequiredMixin
from .forms import TankStationForm
from .models import TankStation, TankIoTReading


class TankMixin(AppAccessMixin):
    required_app = 'oilfield'


class TankAdminMixin(AdminRequiredMixin):
    pass


# ── Lista de estaciones ───────────────────────────────────────────────────────

class TankStationListView(TankMixin, ListView):
    model               = TankStation
    template_name       = 'OILFIELD/tank/station_list.html'
    context_object_name = 'stations'
    ordering            = ['Name']

    def get_queryset(self):
        return TankStation.objects.select_related('Tank', 'Tank__Battery').order_by('Name')


# ── Añadir estación ───────────────────────────────────────────────────────────

class TankStationAddView(TankAdminMixin, CreateView):
    model         = TankStation
    form_class    = TankStationForm
    template_name = 'OILFIELD/tank/station_form.html'

    def get_success_url(self):
        return reverse_lazy('oilfield_tank:detail', kwargs={'pk': self.object.pk})


# ── Editar estación ───────────────────────────────────────────────────────────

class TankStationEditView(TankAdminMixin, UpdateView):
    model         = TankStation
    form_class    = TankStationForm
    template_name = 'OILFIELD/tank/station_form.html'

    def get_success_url(self):
        return reverse_lazy('oilfield_tank:detail', kwargs={'pk': self.object.pk})


# ── Detalle / histórico ───────────────────────────────────────────────────────

class TankStationDetailView(TankMixin, DetailView):
    model               = TankStation
    template_name       = 'OILFIELD/tank/station_detail.html'
    context_object_name = 'station'

    def get_context_data(self, **kwargs):
        from Apps.OILFIELD.models import TankReading
        ctx   = super().get_context_data(**kwargs)
        days  = int(self.request.GET.get('days', 1))
        since = datetime.utcnow() - timedelta(days=days)

        # Fuente unificada: TankReading filtrado por estación IoT
        readings_list = list(
            TankIoTReading.objects
            .filter(Station=self.object)
            .filter(ReadingDate__gte=since)
            .select_related('Tank', 'Station__Tank')
            .order_by('ReadingDate')
        )
        ctx['readings'] = readings_list
        ctx['days']     = days
        ctx['latest']   = readings_list[-1] if readings_list else None

        def _f(val):
            if val is None:
                return None
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        def _mm_to_cm(val):
            v = _f(val)
            return round(v / 10, 1) if v is not None else None

        ctx['chart_dates']  = json.dumps([r.ReadingDate.strftime('%Y-%m-%dT%H:%M:%S') for r in readings_list if r.ReadingDate])
        ctx['level_data']   = json.dumps([_mm_to_cm(r.Level)    for r in readings_list if r.ReadingDate])
        ctx['water_data']   = json.dumps([_mm_to_cm(r.WaterLevel) for r in readings_list if r.ReadingDate])
        ctx['volume_data']  = json.dumps([_f(r.Volume)           for r in readings_list if r.ReadingDate])
        ctx['battery_data'] = json.dumps([_f(r.VoltageBattery)   for r in readings_list if r.ReadingDate])
        return ctx


# ── API JSON para polling ─────────────────────────────────────────────────────

class TankReadingsAPI(TankMixin, View):
    def get(self, request, pk):
        from Apps.OILFIELD.models import TankReading
        days  = int(request.GET.get('days', 1))
        since = datetime.utcnow() - timedelta(days=days)
        readings = list(
            TankReading.objects
            .filter(Station__pk=pk, ReadingDate__gte=since)
            .order_by('ReadingDate')
            .values('ReadingDate', 'LocalTimestamp', 'Source', 'TypeConn',
                    'Level', 'Temperature', 'WaterLevel', 'Volume', 'VoltageBattery')
        )
        return JsonResponse({'readings': readings}, safe=False)
