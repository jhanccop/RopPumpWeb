import json
import csv
from datetime import timedelta, timezone as dt_utc, datetime
from zoneinfo import ZoneInfo

_LIMA_TZ = ZoneInfo('America/Lima')

def _today_lima():
    return datetime.now(tz=_LIMA_TZ).date()

def _to_lima(dt):
    """Convierte datetime naive (asumido UTC) o aware a hora Lima sin usar Django localtime."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_utc.utc)
    return dt.astimezone(_LIMA_TZ)

from django.db.models import F, FloatField, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from Apps.users.mixins import AppAccessMixin
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    FormView,
)

from Apps.users.models import User
from .models import HydroStation, HydroReading
from .managers import READING_FIELDS, lima_day_bounds
from .forms import HydroStationForm, HydroReadingForm, ReportFilterForm


# Columnas del CSV: (campo, encabezado)
CSV_COLUMNS = (
    ('Temperature',      'Temperatura ambiente (°C)'),
    ('Humidity',         'Humedad (%)'),
    ('WindDirection',    'Dirección viento (°)'),
    ('WindSpeed',        'Velocidad viento (m/s)'),
    ('Precipitation',    'Precipitación (mm)'),
    ('SolarRadiation',   'Radiación solar (W/m²)'),
    ('RawDistance',      'Distancia medida (m)'),
    ('WaterLevel',       'Altura del flujo (m)'),
    ('WaterPH',          'pH agua'),
    ('WaterTemperature', 'Temperatura agua (°C)'),
)


# =================== HELPERS ===========================
def _round(v, nd):
    return round(v, nd) if v is not None else None


def _stations_geojson(stations, latest_by_station):
    """GeoJSON de estaciones con la última medición en las propiedades (para popups)."""
    features = []
    for st in stations:
        if st['Latitude'] and st['Longitude']:
            r = latest_by_station.get(st['id'])
            features.append({
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [st['Longitude'], st['Latitude']]},
                'properties': {
                    'id': st['id'],
                    'name': st['StationName'],
                    'status': st['Status'],
                    'water_body': st['WaterBodyName'] or '',
                    'temp':  _round(r.Temperature, 1) if r else None,
                    'hum':   _round(r.Humidity, 1) if r else None,
                    'rain':  _round(r.Precipitation, 1) if r else None,
                    'rad':   _round(r.SolarRadiation, 0) if r else None,
                    'wind':  _round(r.WindSpeed, 1) if r else None,
                    'level': _round(r.WaterLevel, 2) if r else None,
                    'level_state': r.Station.level_state(r.WaterLevel) if r else None,
                    'ph':    _round(r.WaterPH, 2) if r else None,
                    'twater': _round(r.WaterTemperature, 1) if r else None,
                    'date': _to_lima(r.DateCreate).strftime('%d/%m/%Y %H:%M') if r else None,
                },
            })
    return json.dumps({'type': 'FeatureCollection', 'features': features})


def _chart_context(readings):
    """Series JSON para Plotly a partir de una lista de dicts ordenada por fecha ascendente."""
    ctx = {
        'chart_dates': json.dumps([
            _to_lima(r['DateCreate']).strftime('%Y-%m-%d %H:%M:%S') for r in readings
        ]),
        'display_dates': json.dumps([
            _to_lima(r['DateCreate']).strftime('%d/%m/%Y %H:%M') for r in readings
        ]),
        'chart_dates_dev': json.dumps([
            _to_lima(r['LocalTimestamp']).strftime('%Y-%m-%d %H:%M:%S') if r['LocalTimestamp'] else None
            for r in readings
        ]),
        'display_dates_dev': json.dumps([
            _to_lima(r['LocalTimestamp']).strftime('%d/%m/%Y %H:%M') if r['LocalTimestamp'] else '—'
            for r in readings
        ]),
        'chart_battery': json.dumps([r['VoltageBattery'] for r in readings]),
    }
    for field in READING_FIELDS:
        ctx[f'chart_{field}'] = json.dumps([r[field] for r in readings])
    return ctx


_SERIES_FIELDS = ('DateCreate', 'LocalTimestamp', *READING_FIELDS, 'VoltageBattery')


# =================== MIXINS ===========================
class HidrometAccessMixin(AppAccessMixin):
    required_app = 'hidromet'
    login_url = reverse_lazy('user_app:user-login')


class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['CompanyName'] = self.get_company_name()
        return context

    def get_company_name(self):
        return User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]


class CompanyStationMixin(CompanyMixin):
    """Restringe las vistas de detalle/edición a las estaciones de la compañía del usuario."""
    def get_queryset(self):
        return HydroStation.objects.get_by_company(self.get_company_name())


# =================== PUBLIC VIEWS ===========================
class PublicHydroView(TemplateView):
    """Vista pública de la red hidrometeorológica — sin autenticación."""
    template_name = 'HIDROMET/hm_public.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stations = list(
            HydroStation.objects.filter(Status='Active')
            .values('id', 'StationName', 'Description', 'Latitude', 'Longitude',
                    'Altitude', 'Status', 'WaterBodyName')
        )
        latest_readings = list(HydroReading.objects.get_latest_per_station())
        latest_by_station = {r.Station.id: r for r in latest_readings}

        context['stations_geojson'] = _stations_geojson(stations, latest_by_station)
        context['latest_readings'] = latest_readings
        context['stations'] = stations
        context['total_stations'] = HydroStation.objects.count()
        context['active_stations'] = len(stations)
        context['stations_with_reading'] = len(latest_by_station)
        return context


class PublicHydroDetailView(TemplateView):
    """Vista pública de historial de una estación — sin autenticación."""
    template_name = 'HIDROMET/hm_public_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = get_object_or_404(HydroStation, pk=kwargs['pk'])
        try:
            days = int(self.request.GET.get('days', '7'))
        except ValueError:
            days = 7
        show_all = (days == 0)

        qs = HydroReading.objects.filter(Station__id=station.id)
        if not show_all:
            start, _ = lima_day_bounds(_today_lima() - timedelta(days=days), _today_lima())
            qs = qs.filter(DateCreate__gte=start)
        readings = list(qs.order_by('DateCreate').values(*_SERIES_FIELDS))

        context.update(_chart_context(readings))
        context.update({
            'station': station,
            'days': days,
            'show_all': show_all,
            'total_readings': len(readings),
            'latest': HydroReading.objects.get_latest_by_station(station.id),
        })
        return context


# =================== DASHBOARD ===========================
class DashboardView(HidrometAccessMixin, CompanyMixin, TemplateView):
    template_name = 'HIDROMET/hm_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_name = self.get_company_name()

        stations = list(HydroStation.objects.list_by_company(company_name))
        latest_readings = list(HydroReading.objects.get_latest_per_station(company_name))
        latest_by_station = {r.Station.id: r for r in latest_readings}

        context['stations_geojson'] = _stations_geojson(stations, latest_by_station)
        context['latest_readings'] = latest_readings
        context['stations'] = stations
        context['active_count'] = sum(1 for s in stations if s['Status'] == 'Active')
        context['level_alerts'] = sum(
            1 for r in latest_readings if r.level_state in ('warning', 'critical')
        )
        context['page_section'] = 'Red Hidrometeorológica'
        context['page_view'] = 'Dashboard'
        return context


# =================== STATION CRUD ===========================
class StationListView(HidrometAccessMixin, CompanyMixin, ListView):
    template_name = 'HIDROMET/hm_station_list.html'
    context_object_name = 'stations'

    def get_queryset(self):
        return HydroStation.objects.list_by_company(self.get_company_name())


class StationAddView(HidrometAccessMixin, CompanyMixin, CreateView):
    template_name = 'HIDROMET/hm_station_add.html'
    model = HydroStation
    form_class = HydroStationForm
    success_url = reverse_lazy('hidromet:station_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['Owner'] = self.request.user.id
        return initial


class StationUpdateView(HidrometAccessMixin, CompanyStationMixin, UpdateView):
    template_name = 'HIDROMET/hm_station_update.html'
    model = HydroStation
    form_class = HydroStationForm

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def get_success_url(self):
        return reverse_lazy('hidromet:station_detail', args=[self.object.pk])

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get('recalc_history'):
            # Altura del flujo = tara − distancia medida, para todas las lecturas con distancia registrada
            HydroReading.objects.filter(Station=self.object, RawDistance__isnull=False).update(
                WaterLevel=Value(self.object.LevelTare, output_field=FloatField()) - F('RawDistance')
            )
        return response


class StationRemoveView(HidrometAccessMixin, CompanyStationMixin, DeleteView):
    template_name = 'HIDROMET/hm_station_remove.html'
    model = HydroStation
    success_url = reverse_lazy('hidromet:station_list')


class StationDetailView(HidrometAccessMixin, CompanyStationMixin, DetailView):
    template_name = 'HIDROMET/hm_station_detail.html'
    model = HydroStation
    context_object_name = 'station'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.object
        try:
            days = int(self.request.GET.get('days', 7))
        except ValueError:
            days = 7
        date_from = _today_lima() - timedelta(days=days)

        readings = list(
            HydroReading.objects.get_range_by_station(station.id, date_from, _today_lima())
            .order_by('DateCreate').values(*_SERIES_FIELDS)
        )
        context.update(_chart_context(readings))
        all_readings = HydroReading.objects.filter(Station=station)
        context['days'] = days
        context['latest'] = HydroReading.objects.get_latest_by_station(station.id)
        context['first_reading'] = all_readings.order_by('DateCreate').values_list('DateCreate', flat=True).first()
        context['readings_total'] = all_readings.count()
        context['readings'] = list(reversed(readings))
        return context


# =================== READINGS ===========================
class ReadingListView(HidrometAccessMixin, CompanyMixin, ListView):
    template_name = 'HIDROMET/hm_reading_list.html'
    context_object_name = 'readings'

    def get_queryset(self):
        qs = HydroReading.objects.filter(
            Station__Owner__CompanyId__CompanyName=self.get_company_name()
        ).select_related('Station').order_by('-DateCreate')
        station_id = self.request.GET.get('station')
        if station_id:
            qs = qs.filter(Station__id=station_id)
        return qs[:5000]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stations'] = HydroStation.objects.list_by_company(self.get_company_name())
        context['filter_station'] = self.request.GET.get('station', '')
        return context


class ReadingAddView(HidrometAccessMixin, CompanyMixin, CreateView):
    template_name = 'HIDROMET/hm_reading_add.html'
    model = HydroReading
    form_class = HydroReadingForm
    success_url = reverse_lazy('hidromet:dashboard')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def get_initial(self):
        initial = super().get_initial()
        station_id = self.request.GET.get('station')
        if station_id:
            initial['Station'] = station_id
        return initial

    def form_valid(self, form):
        # El formulario recibe hora Lima; en BD se guarda naive UTC (igual que el cliente MQTT)
        dt = form.cleaned_data['DateCreate']
        form.instance.DateCreate = (
            dt.replace(tzinfo=_LIMA_TZ).astimezone(dt_utc.utc).replace(tzinfo=None)
        )
        return super().form_valid(form)


# =================== REPORTS ===========================
class ReportView(HidrometAccessMixin, CompanyMixin, FormView):
    template_name = 'HIDROMET/hm_report.html'
    form_class = ReportFilterForm

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def get_initial(self):
        return {
            'date_from': _today_lima() - timedelta(days=30),
            'date_to': _today_lima(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('readings', [])
        return context

    def form_valid(self, form):
        station = form.cleaned_data.get('station')
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']

        if station:
            readings = HydroReading.objects.get_range_by_station(
                station.id, date_from, date_to
            ).order_by('DateCreate').values('Station__StationName', 'DateCreate', *READING_FIELDS)
        else:
            readings = HydroReading.objects.get_range_by_company(
                self.get_company_name(), date_from, date_to
            )

        if 'download' in self.request.POST:
            return self._csv_response(readings, date_from, date_to)

        readings = list(readings)
        return self.render_to_response(
            self.get_context_data(form=form, readings=readings, total=len(readings))
        )

    def _csv_response(self, readings, date_from, date_to):
        filename = f'hidromet_report_{date_from}_{date_to}.csv'
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write('﻿')
        writer = csv.writer(response)
        writer.writerow(['Estación', 'Fecha/Hora (Lima)', *[h for _, h in CSV_COLUMNS]])
        for r in readings:
            dt = _to_lima(r.get('DateCreate'))
            writer.writerow([
                r.get('Station__StationName', ''),
                dt.strftime('%Y-%m-%d %H:%M:%S') if dt else '',
                *[r.get(f) if r.get(f) is not None else '' for f, _ in CSV_COLUMNS],
            ])
        return response
