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

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from Apps.users.mixins import AppAccessMixin
from django.views.generic import (
    TemplateView,
    View,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    FormView,
)

from Apps.users.models import User
from .models import WeatherStation, WeatherReading
from .forms import WeatherStationForm, WeatherReadingForm, ReportFilterForm


# =================== MIXINS ===========================
class FaunaAccessMixin(AppAccessMixin):
    required_app = 'fauna'
    login_url = reverse_lazy('user_app:user-login')


class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        company_name = User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]
        context = super().get_context_data(**kwargs)
        context['CompanyName'] = company_name
        return context

    def get_company_name(self):
        return User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]


# =================== PUBLIC VIEWS ===========================
class PublicWeatherView(TemplateView):
    """Vista pública de estaciones meteorológicas — sin autenticación."""
    template_name = 'FAUNA/weatherStation/ws_public.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stations = list(
            WeatherStation.objects.filter(Status='Active')
            .values('id', 'StationName', 'Description', 'Latitude', 'Longitude',
                    'Altitude', 'Status', 'HasTempHumidity', 'HasSolarRadiation',
                    'HasPrecipitation', 'HasWind')
        )

        from django.db.models import Max
        latest_ids = (
            WeatherReading.objects
            .filter(Station__Status='Active')
            .values('Station')
            .annotate(last_id=Max('id'))
            .values('last_id')
        )
        latest_readings = (
            WeatherReading.objects
            .filter(id__in=latest_ids)
            .select_related('Station')
            .order_by('Station__StationName')
        )
        latest_by_station = {r.Station.id: r for r in latest_readings}

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
                        'temp': round(r.Temperature, 1) if r and r.Temperature is not None else None,
                        'hum': round(r.Humidity, 1) if r and r.Humidity is not None else None,
                        'rain': round(r.Precipitation, 1) if r and r.Precipitation is not None else None,
                        'rad': round(r.SolarRadiation, 0) if r and r.SolarRadiation is not None else None,
                        'wind': round(r.WindSpeed, 1) if r and r.WindSpeed is not None else None,
                        'date': _to_lima(r.DateCreate).strftime('%d/%m/%Y %H:%M') if r else None,
                    },
                })

        context['stations_geojson'] = json.dumps({'type': 'FeatureCollection', 'features': features})
        context['latest_readings'] = list(latest_readings)
        context['stations'] = stations
        context['total_stations'] = WeatherStation.objects.count()
        context['active_stations'] = WeatherStation.objects.filter(Status='Active').count()
        context['stations_with_reading'] = len(latest_by_station)
        return context


class PublicWeatherDetailView(TemplateView):
    """Vista pública de historial de una estación — sin autenticación."""
    template_name = 'FAUNA/weatherStation/ws_public_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.shortcuts import get_object_or_404
        station = get_object_or_404(WeatherStation, pk=kwargs['pk'])
        days_param = self.request.GET.get('days', '7')
        show_all = (days_param == '0')
        days = 0 if show_all else int(days_param)

        if show_all:
            readings = list(
                WeatherReading.objects.filter(Station__id=station.id)
                .order_by('DateCreate')
                .values('DateCreate', 'Temperature', 'Humidity',
                        'SolarRadiation', 'Precipitation', 'WindSpeed', 'VoltageBattery')
            )
        else:
            date_from = _today_lima() - timedelta(days=days)
            date_to = _today_lima()
            readings = list(WeatherReading.objects.get_range_by_station(
                station.id, date_from, date_to
            ).order_by('DateCreate')
             .values('DateCreate', 'Temperature', 'Humidity',
                     'SolarRadiation', 'Precipitation', 'WindSpeed', 'VoltageBattery'))

        # ISO para Plotly (type:'date'), formato legible para la tabla
        chart_dates   = [_to_lima(r['DateCreate']).strftime('%Y-%m-%d %H:%M:%S') for r in readings]
        display_dates = [_to_lima(r['DateCreate']).strftime('%d/%m/%Y %H:%M') for r in readings]
        context.update({
            'station': station,
            'days': days,
            'show_all': show_all,
            'total_readings': len(readings),
            'latest': WeatherReading.objects.get_latest_by_station(station.id),
            'chart_dates': json.dumps(chart_dates),
            'display_dates': json.dumps(display_dates),
            'chart_temperature': json.dumps([r['Temperature'] for r in readings]),
            'chart_humidity': json.dumps([r['Humidity'] for r in readings]),
            'chart_radiation': json.dumps([r['SolarRadiation'] for r in readings]),
            'chart_precipitation': json.dumps([r['Precipitation'] for r in readings]),
            'chart_wind': json.dumps([r['WindSpeed'] for r in readings]),
            'chart_battery': json.dumps([r['VoltageBattery'] for r in readings]),
        })
        return context


# =================== DASHBOARD ===========================
class DashboardView(FaunaAccessMixin, CompanyMixin, TemplateView):
    template_name = 'FAUNA/weatherStation/ws_dashboard.html'
    login_url = reverse_lazy('user_app:user-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_name = self.get_company_name()

        stations = list(WeatherStation.objects.list_by_company(company_name))
        latest_readings = WeatherReading.objects.get_latest_per_station(company_name)

        # Index latest readings by station id for O(1) lookup
        latest_by_station = {r.Station.id: r for r in latest_readings}

        # Build enriched GeoJSON — properties include last measurement for popups
        features = []
        for st in stations:
            if st['Latitude'] and st['Longitude']:
                r = latest_by_station.get(st['id'])
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [st['Longitude'], st['Latitude']],
                    },
                    'properties': {
                        'id': st['id'],
                        'name': st['StationName'],
                        'status': st['Status'],
                        'temp': round(r.Temperature, 1) if r and r.Temperature is not None else None,
                        'hum': round(r.Humidity, 1) if r and r.Humidity is not None else None,
                        'rain': round(r.Precipitation, 1) if r and r.Precipitation is not None else None,
                        'rad': round(r.SolarRadiation, 0) if r and r.SolarRadiation is not None else None,
                        'wind': round(r.WindSpeed, 1) if r and r.WindSpeed is not None else None,
                        'date': _to_lima(r.DateCreate).strftime('%d/%m/%Y %H:%M') if r else None,
                    },
                })
        context['stations_geojson'] = json.dumps({'type': 'FeatureCollection', 'features': features})
        context['latest_readings'] = latest_readings
        context['stations'] = stations
        context['page_section'] = 'Weather Stations'
        context['page_view'] = 'Dashboard'
        return context


# =================== STATION CRUD ===========================
class StationListView(FaunaAccessMixin, CompanyMixin, ListView):
    template_name = 'FAUNA/weatherStation/ws_station_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'stations'

    def get_queryset(self):
        return WeatherStation.objects.list_by_company(self.get_company_name())


class StationAddView(FaunaAccessMixin, CompanyMixin, CreateView):
    template_name = 'FAUNA/weatherStation/ws_station_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    form_class = WeatherStationForm
    success_url = reverse_lazy('weather_app:station_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class StationUpdateView(FaunaAccessMixin, CompanyMixin, UpdateView):
    template_name = 'FAUNA/weatherStation/ws_station_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    form_class = WeatherStationForm
    success_url = reverse_lazy('weather_app:station_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class StationRemoveView(FaunaAccessMixin, CompanyMixin, DeleteView):
    template_name = 'FAUNA/weatherStation/ws_station_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    success_url = reverse_lazy('weather_app:station_list')


class StationDetailView(FaunaAccessMixin, CompanyMixin, DetailView):
    template_name = 'FAUNA/weatherStation/ws_station_detail.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    context_object_name = 'station'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.object
        days = int(self.request.GET.get('days', 7))
        date_from = _today_lima() - timedelta(days=days)
        date_to = _today_lima()

        readings = list(WeatherReading.objects.get_range_by_station(
            station.id, date_from, date_to
        ).values(
            'DateCreate',
            'Temperature', 'Humidity',
            'SolarRadiation', 'Precipitation',
            'WindSpeed', 'WindDirection',
            'VoltageBattery',
        ))

        dates = [
            _to_lima(r['DateCreate']).strftime('%d/%m/%Y %H:%M') if r['DateCreate'] else ''
            for r in readings
        ]
        context['chart_dates'] = json.dumps(dates)
        context['chart_temperature'] = json.dumps([r['Temperature'] for r in readings])
        context['chart_humidity'] = json.dumps([r['Humidity'] for r in readings])
        context['chart_radiation'] = json.dumps([r['SolarRadiation'] for r in readings])
        context['chart_precipitation'] = json.dumps([r['Precipitation'] for r in readings])
        context['chart_wind_speed'] = json.dumps([r['WindSpeed'] for r in readings])
        context['chart_wind_direction'] = json.dumps([r['WindDirection'] for r in readings])
        context['chart_battery'] = json.dumps([r['VoltageBattery'] for r in readings])
        context['days'] = days
        context['latest'] = WeatherReading.objects.get_latest_by_station(station.id)
        context['readings'] = readings
        return context


# =================== READINGS ===========================
class ReadingListView(FaunaAccessMixin, CompanyMixin, ListView):
    template_name = 'FAUNA/weatherStation/ws_reading_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'readings'

    def get_queryset(self):
        company_name = self.get_company_name()
        qs = WeatherReading.objects.filter(
            Station__Owner__CompanyId__CompanyName=company_name
        ).select_related('Station').order_by('-DateCreate')
        station_id = self.request.GET.get('station')
        if station_id:
            qs = qs.filter(Station__id=station_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stations'] = WeatherStation.objects.list_by_company(self.get_company_name())
        context['filter_station'] = self.request.GET.get('station', '')
        return context


class ReadingAddView(FaunaAccessMixin, CompanyMixin, CreateView):
    template_name = 'FAUNA/weatherStation/ws_reading_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherReading
    form_class = WeatherReadingForm
    success_url = reverse_lazy('weather_app:dashboard')

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


# =================== REPORTS ===========================
class ReportView(FaunaAccessMixin, CompanyMixin, FormView):
    template_name = 'FAUNA/weatherStation/ws_report.html'
    login_url = reverse_lazy('user_app:user-login')
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
        context['readings'] = []
        return context

    def form_valid(self, form):
        company_name = self.get_company_name()
        station = form.cleaned_data.get('station')
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']

        if station:
            readings = WeatherReading.objects.get_range_by_station(
                station.id, date_from, date_to
            ).values(
                'Station__StationName', 'DateCreate',
                'Temperature', 'Humidity', 'SolarRadiation',
                'Precipitation', 'WindSpeed', 'WindDirection',
            )
        else:
            readings = WeatherReading.objects.get_range_by_company(
                company_name, date_from, date_to
            )

        if 'download' in self.request.POST:
            return self._csv_response(readings, date_from, date_to)

        context = self.get_context_data(form=form)
        context['readings'] = list(readings)
        context['total'] = len(context['readings'])
        return self.render_to_response(context)

    def _csv_response(self, readings, date_from, date_to):
        filename = f'weather_report_{date_from}_{date_to}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow([
            'Station', 'Date/Time',
            'Temperature (°C)', 'Humidity (%)',
            'Solar Radiation (W/m²)', 'Precipitation (mm)',
            'Wind Speed (m/s)', 'Wind Direction (°)',
        ])
        for r in readings:
            writer.writerow([
                r.get('Station__StationName', ''),
                r.get('DateCreate', ''),
                r.get('Temperature', ''),
                r.get('Humidity', ''),
                r.get('SolarRadiation', ''),
                r.get('Precipitation', ''),
                r.get('WindSpeed', ''),
                r.get('WindDirection', ''),
            ])
        return response
