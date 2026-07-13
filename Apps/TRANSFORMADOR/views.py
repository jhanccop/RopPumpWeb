import json
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from Apps.users.mixins import AppAccessMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from Apps.users.models import User
from .models import Alert, AlertRule, ElectricalReading, Substation, Transformer
from .forms import (
    AlertFilterForm,
    AlertRuleForm,
    ElectricalReadingForm,
    SubstationForm,
    TransformerForm,
)


# =================== MIXINS ===========================

class TransformadorAccessMixin(AppAccessMixin):
    required_app = 'transformadores'
    login_url = reverse_lazy('user_app:user-login')


class CompanyMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['CompanyName'] = self._company_name()
        return context

    def _company_name(self):
        return User.objects.get_company_name(
            self.request.user)[0]["CompanyId__CompanyName"]


# =================== DASHBOARD ===========================

class DashboardView(TransformadorAccessMixin, CompanyMixin, TemplateView):
    template_name = 'TRANSFORMADOR/tr_dashboard.html'
    login_url = reverse_lazy('user_app:user-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self._company_name()

        transformers = list(
            Transformer.objects.get_by_company(company)
            .prefetch_related('readings')
        )

        # Attach latest reading to each transformer
        for tr in transformers:
            prefetched = list(tr.readings.all())
            tr.latest_reading = prefetched[0] if prefetched else None

        total_transformers = len(transformers)
        operational_count = sum(1 for t in transformers if t.Status == 'operational')
        fault_count = sum(1 for t in transformers if t.Status == 'fault')
        maintenance_count = sum(1 for t in transformers if t.Status == 'maintenance')

        active_alerts = Alert.objects.get_active_by_company(company)
        critical_alerts_count = Alert.objects.get_critical(company).count()
        active_alerts_count = active_alerts.count()
        recent_alerts = active_alerts[:10]

        # Build GeoJSON FeatureCollection
        features = []
        for tr in transformers:
            if tr.Latitude is not None and tr.Longitude is not None:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [tr.Longitude, tr.Latitude],
                    },
                    'properties': {
                        'id': tr.id,
                        'code': tr.Code,
                        'name': tr.StationName,
                        'status': tr.Status,
                        'power': float(tr.NominalPower),
                        'address': tr.Address,
                        'reading': {
                            'date': tr.latest_reading.DateCreate.strftime('%d/%m/%Y %H:%M') if tr.latest_reading else None,
                            'hotspot': tr.latest_reading.HotSpotTemperature if tr.latest_reading else None,
                            'oil_temp': tr.latest_reading.OilTemperature if tr.latest_reading else None,
                            'pressure': tr.latest_reading.InternalPressure if tr.latest_reading else None,
                            'oil_level': tr.latest_reading.OilLevel if tr.latest_reading else None,
                            'vibration': tr.latest_reading.Vibration if tr.latest_reading else None,
                            'oil_humidity': tr.latest_reading.OilHumidity if tr.latest_reading else None,
                        } if tr.latest_reading else None,
                    },
                })
        stations_geojson = json.dumps({'type': 'FeatureCollection', 'features': features})

        context.update({
            'transformers': transformers,
            'total_transformers': total_transformers,
            'operational_count': operational_count,
            'fault_count': fault_count,
            'maintenance_count': maintenance_count,
            'active_alerts': active_alerts,
            'critical_alerts_count': critical_alerts_count,
            'active_alerts_count': active_alerts_count,
            'recent_alerts': recent_alerts,
            'stations_geojson': stations_geojson,
        })
        return context


# =================== TRANSFORMER CRUD ===========================

class TransformerListView(TransformadorAccessMixin, CompanyMixin, ListView):
    template_name = 'TRANSFORMADOR/tr_transformer_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'transformers'

    def get_queryset(self):
        company = self._company_name()
        return (
            Transformer.objects.get_by_company(company)
            .select_related('Substation')
            .order_by('StationName')
        )


class TransformerAddView(TransformadorAccessMixin, CompanyMixin, CreateView):
    template_name = 'TRANSFORMADOR/tr_transformer_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = TransformerForm
    success_url = reverse_lazy('transformer_app:transformer_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.Owner = self.request.user
        return super().form_valid(form)


class TransformerUpdateView(TransformadorAccessMixin, CompanyMixin, UpdateView):
    template_name = 'TRANSFORMADOR/tr_transformer_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Transformer
    form_class = TransformerForm
    success_url = reverse_lazy('transformer_app:transformer_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class TransformerDetailView(TransformadorAccessMixin, CompanyMixin, DetailView):
    template_name = 'TRANSFORMADOR/tr_transformer_detail.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Transformer
    context_object_name = 'transformer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transformer = self.object

        readings = list(
            ElectricalReading.objects.filter(Transformer=transformer)
            .order_by('-DateCreate')[:100]
        )
        alerts = transformer.alerts.filter(Status='active').order_by('-DateCreate')
        alert_rules = transformer.alert_rules.all()

        sample = list(reversed(readings[:50]))
        chart_dates         = json.dumps([r.DateCreate.strftime('%Y-%m-%d %H:%M') for r in sample])
        chart_oil_temp       = json.dumps([r.OilTemperature      for r in sample])
        chart_hotspot_temp   = json.dumps([r.HotSpotTemperature  for r in sample])
        chart_pressure       = json.dumps([r.InternalPressure     for r in sample])
        chart_oil_level      = json.dumps([r.OilLevel             for r in sample])
        chart_vibration      = json.dumps([r.Vibration            for r in sample])
        chart_oil_humidity   = json.dumps([r.OilHumidity          for r in sample])

        context.update({
            'readings': readings,
            'latest_reading': readings[0] if readings else None,
            'active_alerts': alerts,
            'alert_rules': alert_rules,
            'chart_dates': chart_dates,
            'chart_oil_temp': chart_oil_temp,
            'chart_hotspot_temp': chart_hotspot_temp,
            'chart_pressure': chart_pressure,
            'chart_oil_level': chart_oil_level,
            'chart_vibration': chart_vibration,
            'chart_oil_humidity': chart_oil_humidity,
        })
        return context


class TransformerDeleteView(TransformadorAccessMixin, CompanyMixin, DeleteView):
    template_name = 'TRANSFORMADOR/tr_transformer_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Transformer
    success_url = reverse_lazy('transformer_app:transformer_list')


# =================== SUBSTATION CRUD ===========================

class SubstationListView(TransformadorAccessMixin, CompanyMixin, ListView):
    template_name = 'TRANSFORMADOR/tr_sub_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'substations'

    def get_queryset(self):
        company = self._company_name()
        return Substation.objects.get_by_company(company)


class SubstationAddView(TransformadorAccessMixin, CompanyMixin, CreateView):
    template_name = 'TRANSFORMADOR/tr_sub_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Substation
    form_class = SubstationForm
    success_url = reverse_lazy('transformer_app:substation_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.Owner = self.request.user
        return super().form_valid(form)


class SubstationUpdateView(TransformadorAccessMixin, CompanyMixin, UpdateView):
    template_name = 'TRANSFORMADOR/tr_sub_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Substation
    form_class = SubstationForm
    success_url = reverse_lazy('transformer_app:substation_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class SubstationDeleteView(TransformadorAccessMixin, CompanyMixin, DeleteView):
    template_name = 'TRANSFORMADOR/tr_sub_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Substation
    success_url = reverse_lazy('transformer_app:substation_list')


# =================== READINGS ===========================

class ReadingListView(TransformadorAccessMixin, CompanyMixin, ListView):
    template_name = 'TRANSFORMADOR/tr_reading_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'readings'
    paginate_by = 50

    def get_queryset(self):
        company = self._company_name()
        qs = (
            ElectricalReading.objects
            .filter(Transformer__Owner__CompanyId__CompanyName=company)
            .select_related('Transformer')
            .order_by('-DateCreate')
        )
        transformer_pk = self.request.GET.get('transformer')
        if transformer_pk:
            qs = qs.filter(Transformer__pk=transformer_pk)
        date_from = self.request.GET.get('date_from')
        if date_from:
            qs = qs.filter(DateCreate__date__gte=date_from)
        date_to = self.request.GET.get('date_to')
        if date_to:
            qs = qs.filter(DateCreate__date__lte=date_to)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = self._company_name()
        ctx['transformer_choices'] = Transformer.objects.filter(
            Owner__CompanyId__CompanyName=company
        ).order_by('StationName')
        ctx['filter_transformer'] = self.request.GET.get('transformer', '')
        ctx['filter_date_from'] = self.request.GET.get('date_from', '')
        ctx['filter_date_to'] = self.request.GET.get('date_to', '')
        return ctx


class ReadingAddView(TransformadorAccessMixin, CompanyMixin, CreateView):
    template_name = 'TRANSFORMADOR/tr_reading_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = ElectricalReadingForm
    success_url = reverse_lazy('transformer_app:reading_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self._check_alerts(self.object)
        return response

    def _check_alerts(self, reading):
        transformer = reading.Transformer
        rules = AlertRule.objects.filter(Transformer=transformer, IsActive=True)
        for rule in rules:
            value = getattr(reading, rule.Variable, None)
            if value is None:
                continue
            condition = rule.Condition
            threshold = rule.Threshold
            triggered = False
            is_gt = False
            if condition == 'gt' and value > threshold:
                triggered = True
                is_gt = True
            elif condition == 'gte' and value >= threshold:
                triggered = True
                is_gt = True
            elif condition == 'lt' and value < threshold:
                triggered = True
                is_gt = False
            elif condition == 'lte' and value <= threshold:
                triggered = True
                is_gt = False
            if triggered:
                direction = '>' if is_gt else '<'
                Alert.objects.create(
                    Transformer=transformer,
                    Rule=rule,
                    Variable=rule.Variable,
                    Severity=rule.Severity,
                    DetectedValue=value,
                    ThresholdValue=threshold,
                    Message=f"{rule.Variable} = {value:.2f} {direction} {threshold}",
                )


# =================== ALERTS ===========================

class AlertListView(TransformadorAccessMixin, CompanyMixin, ListView):
    template_name = 'TRANSFORMADOR/tr_alert_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'alerts'
    paginate_by = 30

    def get_queryset(self):
        company = self._company_name()
        qs = (
            Alert.objects
            .filter(Transformer__Owner__CompanyId__CompanyName=company)
            .select_related('Transformer', 'AcknowledgedBy')
            .order_by('-DateCreate')
        )
        transformer_pk = self.request.GET.get('transformer')
        severity = self.request.GET.get('severity')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if transformer_pk:
            qs = qs.filter(Transformer__pk=transformer_pk)
        if severity:
            qs = qs.filter(Severity=severity)
        if status:
            qs = qs.filter(Status=status)
        if date_from:
            qs = qs.filter(DateCreate__date__gte=date_from)
        if date_to:
            qs = qs.filter(DateCreate__date__lte=date_to)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AlertFilterForm(
            self.request.GET or None, request=self.request
        )
        return context


class AlertAcknowledgeView(TransformadorAccessMixin, View):
    login_url = reverse_lazy('user_app:user-login')

    def post(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
            alert.Status = 'acknowledged'
            alert.AcknowledgedBy = request.user
            alert.DateAcknowledged = datetime.now()
            alert.save()
            return JsonResponse({'ok': True})
        except Alert.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Not found'}, status=404)


class AlertCloseView(TransformadorAccessMixin, View):
    login_url = reverse_lazy('user_app:user-login')

    def post(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
            alert.Status = 'closed'
            alert.DateClosed = datetime.now()
            alert.save()
            return JsonResponse({'ok': True})
        except Alert.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Not found'}, status=404)


# =================== ALERT RULES ===========================

class AlertRuleListView(TransformadorAccessMixin, CompanyMixin, ListView):
    template_name = 'TRANSFORMADOR/tr_rule_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'rules'

    def get_queryset(self):
        company = self._company_name()
        return AlertRule.objects.filter(
            Transformer__Owner__CompanyId__CompanyName=company
        ).select_related('Transformer')


class AlertRuleAddView(TransformadorAccessMixin, CompanyMixin, CreateView):
    template_name = 'TRANSFORMADOR/tr_rule_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = AlertRule
    form_class = AlertRuleForm
    success_url = reverse_lazy('transformer_app:rule_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class AlertRuleUpdateView(TransformadorAccessMixin, CompanyMixin, UpdateView):
    template_name = 'TRANSFORMADOR/tr_rule_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = AlertRule
    form_class = AlertRuleForm
    success_url = reverse_lazy('transformer_app:rule_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class AlertRuleDeleteView(TransformadorAccessMixin, CompanyMixin, DeleteView):
    template_name = 'TRANSFORMADOR/tr_rule_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = AlertRule
    success_url = reverse_lazy('transformer_app:rule_list')
