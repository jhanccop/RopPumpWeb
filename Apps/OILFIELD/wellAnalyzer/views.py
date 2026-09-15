import json
from datetime import datetime, timedelta

from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from Apps.users.mixins import AppAccessMixin, AdminRequiredMixin
from .forms import WellAnalyzerStationForm
from .models import WellAnalyzerStation, AnalyzerReading


class WellMixin(AppAccessMixin):
    required_app = 'oilfield'


class WellAdminMixin(AdminRequiredMixin):
    pass


class WellAnalyzerListView(WellMixin, ListView):
    model               = WellAnalyzerStation
    template_name       = 'OILFIELD/wellAnalyzer/station_list.html'
    context_object_name = 'stations'

    def get_queryset(self):
        return WellAnalyzerStation.objects.select_related('Well', 'Well__Battery').order_by('Name')


class WellAnalyzerAddView(WellAdminMixin, CreateView):
    model         = WellAnalyzerStation
    form_class    = WellAnalyzerStationForm
    template_name = 'OILFIELD/wellAnalyzer/station_form.html'

    def get_success_url(self):
        return reverse_lazy('oilfield_wellanalyzer:detail', kwargs={'pk': self.object.pk})


class WellAnalyzerEditView(WellAdminMixin, UpdateView):
    model         = WellAnalyzerStation
    form_class    = WellAnalyzerStationForm
    template_name = 'OILFIELD/wellAnalyzer/station_form.html'

    def get_success_url(self):
        return reverse_lazy('oilfield_wellanalyzer:detail', kwargs={'pk': self.object.pk})


class WellAnalyzerDetailView(WellMixin, DetailView):
    model               = WellAnalyzerStation
    template_name       = 'OILFIELD/wellAnalyzer/station_detail.html'
    context_object_name = 'station'

    def get_context_data(self, **kwargs):
        ctx   = super().get_context_data(**kwargs)
        days  = int(self.request.GET.get('days', 1))
        since = datetime.utcnow() - timedelta(days=days)
        readings = (
            AnalyzerReading.objects
            .filter(Station=self.object, DateCreate__gte=since)
            .order_by('DateCreate')
        )
        readings_list = list(readings)
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

        ctx['chart_dates']  = json.dumps([r.DateCreate.strftime('%Y-%m-%dT%H:%M:%S') for r in readings_list])
        ctx['spm_data']     = json.dumps([_f(r.SPM)            for r in readings_list])
        ctx['fillage_data'] = json.dumps([_f(r.Fillage)         for r in readings_list])
        ctx['oil_data']     = json.dumps([_f(r.OilProduction)   for r in readings_list])
        ctx['water_data']   = json.dumps([_f(r.WaterProduction)  for r in readings_list])
        ctx['current_data'] = json.dumps([_f(r.MotorCurrent)    for r in readings_list])
        ctx['temp_data']    = json.dumps([_f(r.Temperature)     for r in readings_list])
        return ctx
