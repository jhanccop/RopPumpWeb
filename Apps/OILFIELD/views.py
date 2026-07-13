import json
from datetime import date, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from Apps.users.mixins import AppAccessMixin
from django.db.models import Avg, Count, Max, Min, Q, Sum
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
from .models import (
    AlertRule,
    Battery,
    Manifold,
    OperationalAlert,
    PumpingUnit,
    Tank,
    TankReading,
    Well,
    WellDailyProduction,
    WellEvent,
)
from .forms import (
    AlertFilterForm,
    AlertRuleForm,
    BatteryForm,
    ManifoldForm,
    ProductionFilterForm,
    PumpingUnitForm,
    TankForm,
    TankReadingForm,
    WellDailyProductionForm,
    WellEventForm,
    WellForm,
)


# =================== MIXINS ===========================

class OilfieldAccessMixin(AppAccessMixin):
    required_app = 'oilfield'
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

class DashboardView(OilfieldAccessMixin, CompanyMixin, TemplateView):
    template_name = 'OILFIELD/of_dashboard.html'
    login_url = reverse_lazy('user_app:user-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self._company_name()

        batteries = Battery.objects.get_by_company(company)

        wells = list(
            Well.objects.get_by_company(company)
            .select_related('Battery', 'PumpingUnit')
            .prefetch_related('pumping_readings')
        )

        for well in wells:
            readings = list(well.pumping_readings.all())
            well.latest_reading = readings[0] if readings else None

        total_wells = len(wells)
        producing_count = sum(1 for w in wells if w.Status == 'producing')
        stopped_statuses = ('stopped', 'fault_mech', 'maintenance')
        stopped_count = sum(1 for w in wells if w.Status in stopped_statuses)
        problem_count = sum(
            1 for w in wells if w.Status not in ('producing', 'inactive')
        )

        today = date.today()
        total_oil_today = (
            WellDailyProduction.objects
            .get_by_company(company)
            .filter(OperativeDate=today)
            .aggregate(total=Sum('OilProduction'))['total'] or 0
        )
        total_water_today = (
            WellDailyProduction.objects
            .get_by_company(company)
            .filter(OperativeDate=today)
            .aggregate(total=Sum('WaterProduction'))['total'] or 0
        )

        active_alerts = OperationalAlert.objects.get_active_by_company(company)
        critical_alerts_count = OperationalAlert.objects.get_critical(company).count()
        recent_alerts = active_alerts.select_related('Well', 'Tank')[:10]

        tanks = list(
            Tank.objects.get_by_company(company)
            .prefetch_related('readings')
            .select_related('Battery')
        )
        for tank in tanks:
            readings = list(tank.readings.all())
            tank.latest_reading = readings[0] if readings else None

        # Build GeoJSON FeatureCollection for wells
        features = []
        for well in wells:
            if well.Latitude is not None and well.Longitude is not None:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [well.Longitude, well.Latitude],
                    },
                    'properties': {
                        'id':               well.id,
                        'code':             well.Code,
                        'name':             well.Name,
                        'status':           well.Status,
                        'battery':          str(well.Battery) if well.Battery else '',
                        'production_target': well.ProductionTarget,
                        'lift_type':        well.LiftType,
                    },
                })
        wells_geojson = json.dumps({'type': 'FeatureCollection', 'features': features})

        problem_statuses = ('overloaded', 'pump_off', 'gas_lock', 'fluid_pound')
        overloaded_wells = [w for w in wells if w.Status in problem_statuses]

        context.update({
            'batteries':             batteries,
            'wells':                 wells,
            'total_wells':           total_wells,
            'producing_count':       producing_count,
            'stopped_count':         stopped_count,
            'problem_count':         problem_count,
            'total_oil_today':       total_oil_today,
            'total_water_today':     total_water_today,
            'active_alerts':         active_alerts,
            'critical_alerts_count': critical_alerts_count,
            'recent_alerts':         recent_alerts,
            'tanks':                 tanks,
            'wells_geojson':         wells_geojson,
            'overloaded_wells':      overloaded_wells,
        })
        return context


# =================== BATTERY CRUD ===========================

class BatteryListView(OilfieldAccessMixin, CompanyMixin, ListView):
    template_name = 'OILFIELD/of_battery_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'batteries'

    def get_queryset(self):
        company = self._company_name()
        return Battery.objects.get_by_company(company)


class BatteryAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_battery_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = BatteryForm
    success_url = reverse_lazy('oilfield_app:battery_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.Owner = self.request.user
        return super().form_valid(form)


class BatteryUpdateView(OilfieldAccessMixin, CompanyMixin, UpdateView):
    template_name = 'OILFIELD/of_battery_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Battery
    form_class = BatteryForm
    success_url = reverse_lazy('oilfield_app:battery_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class BatteryDeleteView(OilfieldAccessMixin, CompanyMixin, DeleteView):
    template_name = 'OILFIELD/of_battery_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Battery
    success_url = reverse_lazy('oilfield_app:battery_list')


# =================== WELL CRUD ===========================

class WellListView(OilfieldAccessMixin, CompanyMixin, ListView):
    template_name = 'OILFIELD/of_well_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'wells'

    def get_queryset(self):
        company = self._company_name()
        qs = (
            Well.objects.get_by_company(company)
            .select_related('Battery', 'Manifold', 'Tank', 'PumpingUnit')
            .prefetch_related('pumping_readings')
        )
        battery_pk = self.request.GET.get('battery')
        status = self.request.GET.get('status')
        if battery_pk:
            qs = qs.filter(Battery__pk=battery_pk)
        if status:
            qs = qs.filter(Status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for well in context['wells']:
            readings = list(well.pumping_readings.all())
            well.latest_reading = readings[0] if readings else None
        return context


class WellAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_well_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = WellForm
    success_url = reverse_lazy('oilfield_app:well_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.Owner = self.request.user
        return super().form_valid(form)


class WellUpdateView(OilfieldAccessMixin, CompanyMixin, UpdateView):
    template_name = 'OILFIELD/of_well_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Well
    form_class = WellForm
    success_url = reverse_lazy('oilfield_app:well_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class WellDeleteView(OilfieldAccessMixin, CompanyMixin, DeleteView):
    template_name = 'OILFIELD/of_well_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Well
    success_url = reverse_lazy('oilfield_app:well_list')


class WellDetailView(OilfieldAccessMixin, CompanyMixin, DetailView):
    template_name = 'OILFIELD/of_well_detail.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Well
    context_object_name = 'well'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        well = self.object

        pumping_readings = list(
            well.pumping_readings.order_by('-DateCreate')[:100]
        )
        daily_productions = list(
            well.daily_productions.order_by('-OperativeDate')[:30]
        )
        events = well.events.order_by('-EventDate')[:20]
        active_alerts = well.alerts.filter(Status='active')

        sample_readings = list(reversed(pumping_readings[:30]))
        chart_dates   = json.dumps([r.DateCreate.strftime('%Y-%m-%d %H:%M') for r in sample_readings])
        chart_spm     = json.dumps([r.SPM          for r in sample_readings])
        chart_fillage = json.dumps([r.Fillage       for r in sample_readings])
        chart_oil     = json.dumps([r.OilProduction  for r in sample_readings])
        chart_current = json.dumps([r.MotorCurrent   for r in sample_readings])

        sample_prod = list(reversed(daily_productions))
        chart_prod_dates = json.dumps([str(p.OperativeDate) for p in sample_prod])
        chart_oil_prod   = json.dumps([p.OilProduction       for p in sample_prod])
        chart_water_prod = json.dumps([p.WaterProduction      for p in sample_prod])

        context.update({
            'pumping_readings':  pumping_readings,
            'daily_productions': daily_productions,
            'events':            events,
            'active_alerts':     active_alerts,
            'chart_dates':       chart_dates,
            'chart_spm':         chart_spm,
            'chart_fillage':     chart_fillage,
            'chart_oil':         chart_oil,
            'chart_current':     chart_current,
            'chart_prod_dates':  chart_prod_dates,
            'chart_oil_prod':    chart_oil_prod,
            'chart_water_prod':  chart_water_prod,
        })
        return context


# =================== TANK CRUD ===========================

class TankListView(OilfieldAccessMixin, CompanyMixin, ListView):
    template_name = 'OILFIELD/of_tank_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'tanks'

    def get_queryset(self):
        company = self._company_name()
        return (
            Tank.objects.get_by_company(company)
            .select_related('Battery')
        )


class TankAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_tank_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = TankForm
    success_url = reverse_lazy('oilfield_app:tank_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.Owner = self.request.user
        return super().form_valid(form)


class TankUpdateView(OilfieldAccessMixin, CompanyMixin, UpdateView):
    template_name = 'OILFIELD/of_tank_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Tank
    form_class = TankForm
    success_url = reverse_lazy('oilfield_app:tank_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class TankDeleteView(OilfieldAccessMixin, CompanyMixin, DeleteView):
    template_name = 'OILFIELD/of_tank_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Tank
    success_url = reverse_lazy('oilfield_app:tank_list')


class TankDetailView(OilfieldAccessMixin, CompanyMixin, DetailView):
    template_name = 'OILFIELD/of_tank_detail.html'
    login_url = reverse_lazy('user_app:user-login')
    model = Tank
    context_object_name = 'tank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tank = self.object

        readings = list(
            TankReading.objects.filter(Tank=tank).order_by('-ReadingDate')[:100]
        )
        latest_reading = readings[0] if readings else None
        active_alerts = tank.alerts.filter(Status='active')

        sample = list(reversed(readings[:50]))
        chart_dates = json.dumps([r.ReadingDate.strftime('%Y-%m-%d %H:%M') for r in sample])
        chart_level = json.dumps([r.Level        for r in sample])
        chart_temp  = json.dumps([r.Temperature   for r in sample])

        context.update({
            'readings':       readings,
            'latest_reading': latest_reading,
            'active_alerts':  active_alerts,
            'chart_dates':    chart_dates,
            'chart_level':    chart_level,
            'chart_temp':     chart_temp,
        })
        return context


# =================== PUMPING UNIT CRUD ===========================

class PumpingUnitListView(OilfieldAccessMixin, CompanyMixin, ListView):
    template_name = 'OILFIELD/of_pumping_unit_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'pumping_units'

    def get_queryset(self):
        return PumpingUnit.objects.all()


class PumpingUnitAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_pumping_unit_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = PumpingUnitForm
    success_url = reverse_lazy('oilfield_app:pumping_unit_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class PumpingUnitUpdateView(OilfieldAccessMixin, CompanyMixin, UpdateView):
    template_name = 'OILFIELD/of_pumping_unit_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = PumpingUnit
    form_class = PumpingUnitForm
    success_url = reverse_lazy('oilfield_app:pumping_unit_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class PumpingUnitDeleteView(OilfieldAccessMixin, CompanyMixin, DeleteView):
    template_name = 'OILFIELD/of_pumping_unit_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = PumpingUnit
    success_url = reverse_lazy('oilfield_app:pumping_unit_list')


# =================== PRODUCTION ===========================

class ProductionListView(OilfieldAccessMixin, CompanyMixin, ListView):
    template_name = 'OILFIELD/of_production_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'productions'
    paginate_by = 50

    def get_queryset(self):
        company = self._company_name()
        qs = (
            WellDailyProduction.objects
            .get_by_company(company)
            .select_related('Well', 'Well__Battery')
            .order_by('-OperativeDate', '-DateCreate')
        )
        well_pk    = self.request.GET.get('well')
        battery_pk = self.request.GET.get('battery')
        date_from  = self.request.GET.get('date_from')
        date_to    = self.request.GET.get('date_to')
        if well_pk:
            qs = qs.filter(Well__pk=well_pk)
        if battery_pk:
            qs = qs.filter(Well__Battery__pk=battery_pk)
        if date_from:
            qs = qs.filter(OperativeDate__gte=date_from)
        if date_to:
            qs = qs.filter(OperativeDate__lte=date_to)
        self._filtered_qs = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self._filtered_qs
        totals = qs.aggregate(
            total_oil=Sum('OilProduction'),
            total_water=Sum('WaterProduction'),
        )
        context['filter_form'] = ProductionFilterForm(
            self.request.GET or None, request=self.request
        )
        context['total_oil']   = totals['total_oil']   or 0
        context['total_water'] = totals['total_water'] or 0
        return context


class ProductionAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_production_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = WellDailyProductionForm
    success_url = reverse_lazy('oilfield_app:production_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.EnteredBy = self.request.user
        response = super().form_valid(form)
        self._check_alerts(self.object)
        return response

    def _check_alerts(self, production):
        well = production.Well

        def _already_active(well, alert_type):
            """Return True if an active/acknowledged alert of this type exists for the well."""
            return OperationalAlert.objects.filter(
                Well=well,
                AlertType=alert_type,
                Status__in=('active', 'acknowledged'),
            ).exists()

        # Low production alert: oil < 50% of target
        if (
            production.OilProduction is not None
            and well.ProductionTarget
            and production.OilProduction < well.ProductionTarget * 0.5
            and not _already_active(well, 'low_production')
        ):
            OperationalAlert.objects.create(
                Well=well,
                Owner=well.Owner,
                AlertType='low_production',
                Severity='high',
                Variable='OilProduction',
                DetectedValue=production.OilProduction,
                ThresholdValue=well.ProductionTarget * 0.5,
                Message=(
                    f"Baja produccion en {well.Code}: "
                    f"{production.OilProduction:.2f} bbl < "
                    f"{well.ProductionTarget * 0.5:.2f} bbl (50% del objetivo)"
                ),
            )

        # High water cut alert: water cut > 80%
        water_cut = production.WaterCut
        if (
            water_cut is not None
            and water_cut > 80
            and not _already_active(well, 'high_water_cut')
        ):
            OperationalAlert.objects.create(
                Well=well,
                Owner=well.Owner,
                AlertType='high_water_cut',
                Severity='medium',
                Variable='WaterCut',
                DetectedValue=water_cut,
                ThresholdValue=80,
                Message=(
                    f"Exceso de agua en {well.Code}: "
                    f"corte de agua = {water_cut:.1f}%"
                ),
            )

        # Operational condition alerts — only for abnormal conditions
        condition = production.OperationalCondition
        condition_alert_map = {
            'pump_off':    ('pump_off',           'high'),
            'gas_lock':    ('gas_lock',            'high'),
            'low_fillage': ('low_fillage',         'medium'),
            'stopped':     ('well_stopped',        'high'),
            'other':       ('abnormal_production', 'medium'),
        }
        if condition in condition_alert_map:
            alert_type, severity = condition_alert_map[condition]
            if not _already_active(well, alert_type):
                OperationalAlert.objects.create(
                    Well=well,
                    Owner=well.Owner,
                    AlertType=alert_type,
                    Severity=severity,
                    Variable='OperationalCondition',
                    Message=(
                        f"Condicion operacional anormal en {well.Code}: "
                        f"{production.get_OperationalCondition_display()}"
                    ),
                )


# =================== TANK READING ===========================

class TankReadingAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_tank_reading_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = TankReadingForm
    success_url = reverse_lazy('oilfield_app:tank_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.EnteredBy = self.request.user
        response = super().form_valid(form)
        self._check_alerts(self.object)
        return response

    def _check_alerts(self, reading):
        tank = reading.Tank
        level_pct = reading.LevelPercent

        if level_pct is None:
            return

        def _already_active(tank, alert_type):
            return OperationalAlert.objects.filter(
                Tank=tank,
                AlertType=alert_type,
                Status__in=('active', 'acknowledged'),
            ).exists()

        if (
            tank.HighLevelAlert is not None
            and level_pct > tank.HighLevelAlert
            and not _already_active(tank, 'tank_overflow')
        ):
            OperationalAlert.objects.create(
                Tank=tank,
                Owner=tank.Owner,
                AlertType='tank_overflow',
                Severity='critical',
                Variable='LevelPercent',
                DetectedValue=level_pct,
                ThresholdValue=tank.HighLevelAlert,
                Message=(
                    f"Sobrellenado en tanque {tank.Code}: "
                    f"nivel = {level_pct:.1f}% > {tank.HighLevelAlert}%"
                ),
            )
        elif (
            tank.LowLevelAlert is not None
            and level_pct < tank.LowLevelAlert
            and not _already_active(tank, 'low_tank_level')
        ):
            OperationalAlert.objects.create(
                Tank=tank,
                Owner=tank.Owner,
                AlertType='low_tank_level',
                Severity='high',
                Variable='LevelPercent',
                DetectedValue=level_pct,
                ThresholdValue=tank.LowLevelAlert,
                Message=(
                    f"Bajo nivel en tanque {tank.Code}: "
                    f"nivel = {level_pct:.1f}% < {tank.LowLevelAlert}%"
                ),
            )


# =================== WELL EVENT ===========================

class WellEventAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_event_add.html'
    login_url = reverse_lazy('user_app:user-login')
    form_class = WellEventForm

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.EnteredBy = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('oilfield_app:well_detail', kwargs={'pk': self.object.Well_id})


# =================== ALERTS ===========================

class AlertListView(OilfieldAccessMixin, CompanyMixin, ListView):
    template_name = 'OILFIELD/of_alert_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'alerts'
    paginate_by = 30

    def get_queryset(self):
        company = self._company_name()
        qs = (
            OperationalAlert.objects
            .filter(
                Q(Well__Owner__CompanyId__CompanyName=company)
                | Q(Tank__Owner__CompanyId__CompanyName=company)
            )
            .distinct()
            .select_related('Well', 'Tank', 'AcknowledgedBy')
            .order_by('-DateCreate')
        )
        well_pk    = self.request.GET.get('well')
        battery_pk = self.request.GET.get('battery')
        severity   = self.request.GET.get('severity')
        status     = self.request.GET.get('status')
        date_from  = self.request.GET.get('date_from')
        date_to    = self.request.GET.get('date_to')
        if well_pk:
            qs = qs.filter(Well__pk=well_pk)
        if battery_pk:
            qs = qs.filter(Well__Battery__pk=battery_pk)
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


class AlertAcknowledgeView(OilfieldAccessMixin, View):
    login_url = reverse_lazy('user_app:user-login')

    def post(self, request, pk):
        try:
            alert = OperationalAlert.objects.get(pk=pk)
            alert.Status = 'acknowledged'
            alert.AcknowledgedBy = request.user
            alert.DateAcknowledged = datetime.now()
            alert.save()
            return JsonResponse({'ok': True})
        except OperationalAlert.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Not found'}, status=404)


class AlertCloseView(OilfieldAccessMixin, View):
    login_url = reverse_lazy('user_app:user-login')

    def post(self, request, pk):
        try:
            alert = OperationalAlert.objects.get(pk=pk)
            alert.Status = 'closed'
            alert.DateClosed = datetime.now()
            alert.save()
            return JsonResponse({'ok': True})
        except OperationalAlert.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Not found'}, status=404)


# =================== ALERT RULES ===========================

class AlertRuleListView(OilfieldAccessMixin, CompanyMixin, ListView):
    template_name = 'OILFIELD/of_rule_list.html'
    login_url = reverse_lazy('user_app:user-login')
    context_object_name = 'rules'

    def get_queryset(self):
        company = self._company_name()
        return (
            AlertRule.objects
            .filter(
                Q(Well__Owner__CompanyId__CompanyName=company)
                | Q(Tank__Owner__CompanyId__CompanyName=company)
            )
            .distinct()
            .select_related('Well', 'Tank')
        )


class AlertRuleAddView(OilfieldAccessMixin, CompanyMixin, CreateView):
    template_name = 'OILFIELD/of_rule_add.html'
    login_url = reverse_lazy('user_app:user-login')
    model = AlertRule
    form_class = AlertRuleForm
    success_url = reverse_lazy('oilfield_app:rule_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context

    def form_valid(self, form):
        form.instance.Owner = self.request.user
        return super().form_valid(form)


class AlertRuleUpdateView(OilfieldAccessMixin, CompanyMixin, UpdateView):
    template_name = 'OILFIELD/of_rule_update.html'
    login_url = reverse_lazy('user_app:user-login')
    model = AlertRule
    form_class = AlertRuleForm
    success_url = reverse_lazy('oilfield_app:rule_list')

    def get_form_kwargs(self, **kwargs):
        context = super().get_form_kwargs(**kwargs)
        context['request'] = self.request
        return context


class AlertRuleDeleteView(OilfieldAccessMixin, CompanyMixin, DeleteView):
    template_name = 'OILFIELD/of_rule_remove.html'
    login_url = reverse_lazy('user_app:user-login')
    model = AlertRule
    success_url = reverse_lazy('oilfield_app:rule_list')


# =================== REPORT ===========================

class ReportView(OilfieldAccessMixin, CompanyMixin, TemplateView):
    template_name = 'OILFIELD/of_report.html'
    login_url = reverse_lazy('user_app:user-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self._company_name()

        filter_form = ProductionFilterForm(
            self.request.GET or None, request=self.request
        )

        summary = []
        if filter_form.is_valid():
            qs = WellDailyProduction.objects.get_by_company(company)

            well_val    = filter_form.cleaned_data.get('well')
            battery_val = filter_form.cleaned_data.get('battery')
            date_from   = filter_form.cleaned_data.get('date_from')
            date_to     = filter_form.cleaned_data.get('date_to')

            if well_val:
                qs = qs.filter(Well=well_val)
            if battery_val:
                qs = qs.filter(Well__Battery=battery_val)
            if date_from:
                qs = qs.filter(OperativeDate__gte=date_from)
            if date_to:
                qs = qs.filter(OperativeDate__lte=date_to)

            # Aggregate by well
            well_summary = (
                qs
                .values('Well__Code', 'Well__Name', 'Well__Battery__Name')
                .annotate(
                    total_oil=Sum('OilProduction'),
                    total_water=Sum('WaterProduction'),
                    total_gas=Sum('GasProduction'),
                    avg_oil=Avg('OilProduction'),
                    days_count=Count('id'),
                    date_min=Min('OperativeDate'),
                    date_max=Max('OperativeDate'),
                )
                .order_by('Well__Battery__Name', 'Well__Code')
            )
            summary = list(well_summary)

        context['filter_form'] = filter_form
        context['summary']     = summary
        return context


# =================== DYNAMOMETER / WELL ANALYZER ===========================

class WellMonitorView(OilfieldAccessMixin, CompanyMixin, TemplateView):
    """Overview list of all OILFIELD wells with their latest analyzer data."""
    template_name = 'OILFIELD/of_well_monitor.html'
    login_url = reverse_lazy('user_app:user-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from Apps.data.models import RodPumpData, TankData
        from datetime import timedelta

        company = self._company_name()
        wells = (
            Well.objects.get_by_company(company)
            .select_related('Battery', 'AnalyzerDevice')
            .prefetch_related('pumping_readings')
        )

        wells_data = []
        for well in wells:
            entry = {'well': well, 'last_analyzer': None, 'last_reading': None}
            # Latest IoT pumping reading
            pr = list(well.pumping_readings.all())
            entry['last_reading'] = pr[0] if pr else None
            # Latest dynamometer data via linked analyzer device
            if well.AnalyzerDevice_id:
                entry['last_analyzer'] = (
                    RodPumpData.objects
                    .filter(IdDevice_id=well.AnalyzerDevice_id)
                    .order_by('-DateCreate')
                    .first()
                )
            wells_data.append(entry)

        # Latest tank data for company tanks
        tanks = (
            Tank.objects.get_by_company(company)
            .select_related('Battery')
            .prefetch_related('readings')
        )
        tanks_data = []
        for tank in tanks:
            readings = list(tank.readings.all())
            tanks_data.append({'tank': tank, 'last_reading': readings[0] if readings else None})

        context['wells_data'] = wells_data
        context['tanks_data'] = tanks_data
        return context


class DynamometerView(OilfieldAccessMixin, CompanyMixin, TemplateView):
    """Dynamometer card and historical trends for a single well."""
    template_name = 'OILFIELD/of_dynamometer.html'
    login_url = reverse_lazy('user_app:user-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from Apps.data.models import RodPumpData
        from datetime import timedelta

        well = Well.objects.select_related('AnalyzerDevice', 'Battery').get(pk=self.kwargs['pk'])
        context['well'] = well

        interval = self.request.GET.get('dateKword', '')
        if not interval:
            today = date.today()
            interval = f"{today - timedelta(days=1)} to {today}"
        context['interval'] = interval

        analyzer_data = []
        if well.AnalyzerDevice_id:
            try:
                dates = interval.split(' to ')
                from datetime import datetime
                d0 = datetime.strptime(dates[0].strip(), '%Y-%m-%d')
                d1 = datetime.strptime(dates[-1].strip(), '%Y-%m-%d') + timedelta(days=1)
                analyzer_data = list(
                    RodPumpData.objects
                    .filter(
                        IdDevice_id=well.AnalyzerDevice_id,
                        DateCreate__range=(d0, d1),
                    )
                    .order_by('-DateCreate')
                )
            except Exception:
                analyzer_data = list(
                    RodPumpData.objects
                    .filter(IdDevice_id=well.AnalyzerDevice_id)
                    .order_by('-DateCreate')[:50]
                )

        context['analyzer_data'] = analyzer_data
        context['latest'] = analyzer_data[0] if analyzer_data else None
        return context
