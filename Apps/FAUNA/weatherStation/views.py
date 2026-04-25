import json
import csv
from datetime import date, timedelta

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
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
from .models import WeatherStation, WeatherReading
from .forms import WeatherStationForm, WeatherReadingForm, ReportFilterForm


# =================== MIXIN ===========================
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


# =================== DASHBOARD ===========================
class DashboardView(LoginRequiredMixin, CompanyMixin, TemplateView):
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
                        'date': r.DateCreate.strftime('%d/%m/%Y %H:%M') if r else None,
                    },
                })
        context['stations_geojson'] = json.dumps({'type': 'FeatureCollection', 'features': features})
        context['latest_readings'] = latest_readings
        context['stations'] = stations
        context['page_section'] = 'Weather Stations'
        context['page_view'] = 'Dashboard'
        return context


# =================== STATION CRUD ===========================
class StationListView(LoginRequiredMixin, CompanyMixin, ListView):
    template_name = 'FAUNA/weatherStation/ws_station_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'stations'

    def get_queryset(self):
        return WeatherStation.objects.list_by_company(self.get_company_name())


class StationAddView(LoginRequiredMixin, CompanyMixin, CreateView):
    template_name = 'FAUNA/weatherStation/ws_station_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    form_class = WeatherStationForm
    success_url = reverse_lazy('weather_app:station_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class StationUpdateView(LoginRequiredMixin, CompanyMixin, UpdateView):
    template_name = 'FAUNA/weatherStation/ws_station_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    form_class = WeatherStationForm
    success_url = reverse_lazy('weather_app:station_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class StationRemoveView(LoginRequiredMixin, CompanyMixin, DeleteView):
    template_name = 'FAUNA/weatherStation/ws_station_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    success_url = reverse_lazy('weather_app:station_list')


class StationDetailView(LoginRequiredMixin, CompanyMixin, DetailView):
    template_name = 'FAUNA/weatherStation/ws_station_detail.html'
    login_url = reverse_lazy('user_app:user-login')
    model = WeatherStation
    context_object_name = 'station'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.object
        days = int(self.request.GET.get('days', 7))
        date_from = date.today() - timedelta(days=days)
        date_to = date.today()

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
            r['DateCreate'].strftime('%Y-%m-%d %H:%M') if r['DateCreate'] else ''
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
class ReadingListView(LoginRequiredMixin, CompanyMixin, ListView):
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


class ReadingAddView(LoginRequiredMixin, CompanyMixin, CreateView):
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
class ReportView(LoginRequiredMixin, CompanyMixin, FormView):
    template_name = 'FAUNA/weatherStation/ws_report.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = ReportFilterForm

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def get_initial(self):
        return {
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
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
