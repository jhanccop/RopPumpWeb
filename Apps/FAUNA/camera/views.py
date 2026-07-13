import json
import csv
from datetime import date, timedelta

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
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
from .models import CameraStation, CameraCapture, CaptureDetection
from .forms import CameraStationForm, CameraCaptureForm, CaptureReportFilterForm, DetectionFormSet


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


# =================== DASHBOARD ===========================
class DashboardView(FaunaAccessMixin, CompanyMixin, TemplateView):
    template_name = 'FAUNA/camera/cam_dashboard.html'
    login_url = reverse_lazy('user_app:user-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_name = self.get_company_name()

        stations = list(CameraStation.objects.list_by_company(company_name))
        latest_captures = list(CameraCapture.objects.get_latest_per_station(company_name))
        summary = list(CameraCapture.objects.species_summary(company_name))

        latest_by_station = {c.Station.id: c for c in latest_captures}

        features = []
        for st in stations:
            if st['Latitude'] and st['Longitude']:
                c = latest_by_station.get(st['id'])
                det_summary = ''
                total_count = None
                if c:
                    dets = list(c.detections.all())
                    det_summary = ', '.join(f'{d.Species}({d.Count})' for d in dets)
                    total_count = sum(d.Count for d in dets)
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
                        'detections': det_summary,
                        'count': total_count,
                        'temp': round(c.Temperature, 1) if c and c.Temperature is not None else None,
                        'hum': round(c.Humidity, 1) if c and c.Humidity is not None else None,
                        'battery': round(c.VoltageBattery, 2) if c and c.VoltageBattery is not None else None,
                        'date': c.DateCapture.strftime('%d/%m/%Y %H:%M') if c else None,
                        'img_url': c.Image.url if c and c.Image else None,
                        'capture_id': c.id if c else None,
                    },
                })
        context['stations_geojson'] = json.dumps({'type': 'FeatureCollection', 'features': features})
        context['latest_captures'] = latest_captures
        context['stations'] = stations
        context['species_summary'] = summary[:10]

        species_names = [s['Species'] for s in summary[:10]]
        species_counts = [s['captures'] for s in summary[:10]]
        species_individuals = [s['total_individuals'] for s in summary[:10]]
        context['chart_species'] = json.dumps(species_names)
        context['chart_captures'] = json.dumps(species_counts)
        context['chart_individuals'] = json.dumps(species_individuals)
        return context


# =================== STATION CRUD ===========================
class StationListView(FaunaAccessMixin, CompanyMixin, ListView):
    template_name = 'FAUNA/camera/cam_station_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'stations'

    def get_queryset(self):
        return CameraStation.objects.list_by_company(self.get_company_name())


class StationAddView(FaunaAccessMixin, CompanyMixin, CreateView):
    template_name = 'FAUNA/camera/cam_station_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraStation
    form_class = CameraStationForm
    success_url = reverse_lazy('camera_app:station_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class StationUpdateView(FaunaAccessMixin, CompanyMixin, UpdateView):
    template_name = 'FAUNA/camera/cam_station_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraStation
    form_class = CameraStationForm
    success_url = reverse_lazy('camera_app:station_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class StationRemoveView(FaunaAccessMixin, CompanyMixin, DeleteView):
    template_name = 'FAUNA/camera/cam_station_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraStation
    success_url = reverse_lazy('camera_app:station_list')


class StationDetailView(FaunaAccessMixin, CompanyMixin, DetailView):
    template_name = 'FAUNA/camera/cam_station_detail.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraStation
    context_object_name = 'station'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.object
        days = int(self.request.GET.get('days', 30))
        date_from = date.today() - timedelta(days=days)
        date_to = date.today()

        captures = list(
            CameraCapture.objects.filter(
                Station__id=station.id,
                DateCapture__date__gte=date_from,
                DateCapture__date__lte=date_to,
            )
            .annotate(total_count=Coalesce(Sum('detections__Count'), 0))
            .order_by('DateCapture')
            .values('DateCapture', 'Temperature', 'Humidity', 'VoltageBattery', 'total_count')
        )

        dates = [c['DateCapture'].strftime('%Y-%m-%d %H:%M') for c in captures]
        context['chart_dates'] = json.dumps(dates)
        context['chart_count'] = json.dumps([c['total_count'] for c in captures])
        context['chart_temperature'] = json.dumps([c['Temperature'] for c in captures])
        context['chart_humidity'] = json.dumps([c['Humidity'] for c in captures])
        context['chart_battery'] = json.dumps([c['VoltageBattery'] for c in captures])

        species_agg = list(
            CaptureDetection.objects.filter(Capture__Station=station)
            .values('Species')
            .annotate(captures=Sum('Count', default=0), individuals=Sum('Count'))
            .order_by('-individuals')
        )
        context['chart_sp_names'] = json.dumps([s['Species'] for s in species_agg])
        context['chart_sp_captures'] = json.dumps([s['captures'] for s in species_agg])
        context['chart_sp_individuals'] = json.dumps([s['individuals'] for s in species_agg])

        context['days'] = days
        context['latest'] = CameraCapture.objects.get_latest_by_station(station.id)
        context['recent_captures'] = CameraCapture.objects.get_by_station(station.id)[:10]
        return context


# =================== CAPTURES ===========================
class CaptureListView(FaunaAccessMixin, CompanyMixin, ListView):
    template_name = 'FAUNA/camera/cam_capture_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'captures'

    def get_queryset(self):
        company_name = self.get_company_name()
        qs = CameraCapture.objects.filter(
            Station__Owner__CompanyId__CompanyName=company_name
        ).select_related('Station').prefetch_related('detections')
        station_id = self.request.GET.get('station')
        if station_id:
            qs = qs.filter(Station__id=station_id)
        species = self.request.GET.get('species')
        if species:
            qs = qs.filter(detections__Species__icontains=species).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_name = self.get_company_name()
        context['stations'] = CameraStation.objects.list_by_company(company_name)
        context['filter_station'] = self.request.GET.get('station', '')
        context['filter_species'] = self.request.GET.get('species', '')
        return context


class CaptureAddView(FaunaAccessMixin, CompanyMixin, CreateView):
    template_name = 'FAUNA/camera/cam_capture_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraCapture
    form_class = CameraCaptureForm
    success_url = reverse_lazy('camera_app:capture_list')

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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['det_formset'] = DetectionFormSet(self.request.POST, prefix='det')
        else:
            ctx['det_formset'] = DetectionFormSet(prefix='det')
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        det_formset = ctx['det_formset']
        if det_formset.is_valid():
            self.object = form.save()
            det_formset.instance = self.object
            det_formset.save()
            return redirect(self.get_success_url())
        return self.form_invalid(form)


class CaptureDetailView(FaunaAccessMixin, CompanyMixin, DetailView):
    template_name = 'FAUNA/camera/cam_capture_detail.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraCapture
    context_object_name = 'capture'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('detections')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.object.Station
        all_ids = list(
            CameraCapture.objects.filter(Station=station)
            .order_by('-DateCapture')
            .values_list('id', flat=True)
        )
        current_idx = all_ids.index(self.object.id) if self.object.id in all_ids else None
        context['prev_capture'] = all_ids[current_idx + 1] if current_idx is not None and current_idx + 1 < len(all_ids) else None
        context['next_capture'] = all_ids[current_idx - 1] if current_idx is not None and current_idx > 0 else None
        return context


class CaptureUpdateView(FaunaAccessMixin, CompanyMixin, UpdateView):
    template_name = 'FAUNA/camera/cam_capture_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraCapture
    form_class = CameraCaptureForm
    success_url = reverse_lazy('camera_app:capture_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['det_formset'] = DetectionFormSet(self.request.POST, instance=self.object, prefix='det')
        else:
            ctx['det_formset'] = DetectionFormSet(instance=self.object, prefix='det')
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        det_formset = ctx['det_formset']
        if det_formset.is_valid():
            self.object = form.save()
            det_formset.instance = self.object
            det_formset.save()
            return redirect(self.get_success_url())
        return self.form_invalid(form)


class CaptureRemoveView(FaunaAccessMixin, CompanyMixin, DeleteView):
    template_name = 'FAUNA/camera/cam_capture_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = CameraCapture
    success_url = reverse_lazy('camera_app:capture_list')


# =================== REPORTS ===========================
class ReportView(FaunaAccessMixin, CompanyMixin, FormView):
    template_name = 'FAUNA/camera/cam_report.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = CaptureReportFilterForm

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
        context['captures'] = []
        return context

    def form_valid(self, form):
        company_name = self.get_company_name()
        station = form.cleaned_data.get('station')
        species = form.cleaned_data.get('species')
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']

        if station:
            qs = CameraCapture.objects.get_range_by_station(station.id, date_from, date_to)
            if species:
                qs = qs.filter(detections__Species__icontains=species).distinct()
            captures = list(qs.prefetch_related('detections').select_related('Station'))
        else:
            captures = list(CameraCapture.objects.get_range_by_company(
                company_name, date_from, date_to, species=species
            ))

        if 'download' in self.request.POST:
            return self._csv_response(captures, date_from, date_to)

        context = self.get_context_data(form=form)
        context['captures'] = captures
        context['total'] = len(captures)
        return self.render_to_response(context)

    def _csv_response(self, captures, date_from, date_to):
        filename = f'camera_report_{date_from}_{date_to}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow([
            'Station', 'Date/Time', 'Species', 'Count',
            'Temperature (°C)', 'Humidity (%)', 'Battery (V)',
        ])
        for c in captures:
            dets = list(c.detections.all())
            if dets:
                for d in dets:
                    writer.writerow([
                        c.Station.StationName, c.DateCapture,
                        d.Species, d.Count,
                        c.Temperature, c.Humidity, c.VoltageBattery,
                    ])
            else:
                writer.writerow([
                    c.Station.StationName, c.DateCapture,
                    '', '', c.Temperature, c.Humidity, c.VoltageBattery,
                ])
        return response
