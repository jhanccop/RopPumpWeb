import csv
from datetime import datetime, timedelta

from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, ListView, TemplateView, UpdateView, View,
)

from Apps.users.mixins import AppAccessMixin, AdminRequiredMixin
from .forms import SecurityDeviceForm, SensorForm
from .models import SENSOR_KEYS, EventLog, SecurityDevice, Sensor


# ── Mixins de acceso ─────────────────────────────────────────────────────────
# Operadores y admins con app 'seguridad' habilitada
class SecUserMixin(AppAccessMixin):
    """Acceso a monitoreo: cualquier usuario con la app seguridad habilitada."""
    required_app = 'seguridad'


# Configuración de dispositivos: solo admins
class SecAdminMixin(AdminRequiredMixin):
    """Acceso a configuración: solo administradores."""
    pass


# ── Dashboard ─────────────────────────────────────────────────────────────────
class DashboardView(SecUserMixin, TemplateView):
    template_name = 'SEGURIDAD/seg_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        device_id = self.request.GET.get('device')
        devices   = SecurityDevice.objects.all()
        device    = None

        if device_id:
            device = get_object_or_404(SecurityDevice, pk=device_id)
        elif devices.exists():
            device = devices.first()

        ctx['devices'] = devices
        ctx['device']  = device
        if device:
            ctx['sensors']       = device.sensors.all()
            ctx['recent_events'] = device.events.select_related('User')[:25]
        return ctx


# ── Lista de dispositivos ─────────────────────────────────────────────────────
class DeviceListView(SecAdminMixin, ListView):
    model               = SecurityDevice
    template_name       = 'SEGURIDAD/seg_device_list.html'
    context_object_name = 'devices'
    ordering            = ['Name']


# ── Añadir dispositivo ────────────────────────────────────────────────────────
class DeviceAddView(SecAdminMixin, CreateView):
    model         = SecurityDevice
    form_class    = SecurityDeviceForm
    template_name = 'SEGURIDAD/seg_device_add.html'

    def form_valid(self, form):
        device = form.save()
        # Crear sensores predeterminados
        for idx, (key, name) in enumerate(SENSOR_KEYS):
            Sensor.objects.get_or_create(
                Device=device, SensorKey=key,
                defaults={'Name': name, 'SensorIndex': idx,
                          'Enabled': False, 'Category': 'critico'},
            )
        return redirect('seguridad:device_edit', pk=device.pk)

    def get_success_url(self):
        return reverse_lazy('seguridad:device_list')


# ── Editar dispositivo + configurar sensores ──────────────────────────────────
class DeviceEditView(SecAdminMixin, UpdateView):
    model         = SecurityDevice
    form_class    = SecurityDeviceForm
    template_name = 'SEGURIDAD/seg_device_edit.html'

    def get_context_data(self, **kwargs):
        ctx     = super().get_context_data(**kwargs)
        device  = self.object
        sensors = device.sensors.order_by('SensorIndex')

        SensorFormSet = modelformset_factory(
            Sensor, form=SensorForm, extra=0,
        )
        if self.request.method == 'POST':
            ctx['sensor_formset'] = SensorFormSet(
                self.request.POST,
                queryset=sensors,
                prefix='sensors',
            )
        else:
            ctx['sensor_formset'] = SensorFormSet(
                queryset=sensors,
                prefix='sensors',
            )
        ctx['sensors_zip'] = list(zip(sensors, ctx['sensor_formset']))
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form        = self.get_form()
        device      = self.object
        sensors     = device.sensors.order_by('SensorIndex')

        SensorFormSet = modelformset_factory(Sensor, form=SensorForm, extra=0)
        sensor_formset = SensorFormSet(request.POST, queryset=sensors, prefix='sensors')

        if form.is_valid() and sensor_formset.is_valid():
            form.save()
            sensor_formset.save()
            return redirect('seguridad:device_edit', pk=device.pk)

        ctx = self.get_context_data(form=form)
        ctx['sensor_formset'] = sensor_formset
        ctx['sensors_zip']    = list(zip(sensors, sensor_formset))
        return self.render_to_response(ctx)

    def get_success_url(self):
        return reverse_lazy('seguridad:device_edit', kwargs={'pk': self.object.pk})


# ── Log de eventos ────────────────────────────────────────────────────────────
class EventLogView(SecUserMixin, TemplateView):
    template_name = 'SEGURIDAD/seg_event_log.html'

    def get_context_data(self, **kwargs):
        ctx      = super().get_context_data(**kwargs)
        devices  = SecurityDevice.objects.all()
        dev_id   = self.request.GET.get('device')
        days     = int(self.request.GET.get('days', 1))
        category = self.request.GET.get('category', '')
        estado   = self.request.GET.get('estado', '')

        device = None
        events = EventLog.objects.select_related('Device', 'User')

        if dev_id:
            device = get_object_or_404(SecurityDevice, pk=dev_id)
            events = events.filter(Device=device)
        if days:
            since  = datetime.now() - timedelta(days=days)
            events = events.filter(ServerTimestamp__gte=since)
        if category:
            events = events.filter(Category=category)
        if estado:
            events = events.filter(Estado=estado)

        ctx['devices']  = devices
        ctx['device']   = device
        ctx['events']   = events[:500]
        ctx['days']     = days
        ctx['category'] = category
        ctx['estado']   = estado
        return ctx


# ── Exportar CSV de eventos ───────────────────────────────────────────────────
class EventLogCSVView(SecUserMixin, View):
    def get(self, request):
        dev_id = request.GET.get('device')
        days   = int(request.GET.get('days', 1))

        events = EventLog.objects.select_related('Device', 'User')
        if dev_id:
            events = events.filter(Device__pk=dev_id)
        if days:
            since  = datetime.now() - timedelta(days=days)
            events = events.filter(ServerTimestamp__gte=since)

        filename = f'seguridad_log_{datetime.now():%Y%m%d}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['Fecha/Hora Servidor', 'Fecha/Hora Dispositivo',
                         'Dispositivo', 'Origen', 'Sensor', 'Estado', 'Categoría', 'Usuario'])
        for e in events:
            writer.writerow([
                e.ServerTimestamp.strftime('%Y-%m-%d %H:%M:%S'),
                e.DeviceTimestamp.strftime('%Y-%m-%d %H:%M:%S') if e.DeviceTimestamp else '—',
                e.Device.Name,
                e.get_Origin_display(),
                e.SensorName or f'Sensor {e.SensorIndex}',
                e.get_Estado_display(),
                e.get_Category_display(),
                str(e.User) if e.User else '—',
            ])
        return response


# ── API: último estado del dispositivo (para polling AJAX del dashboard) ──────
class DeviceStatusAPI(SecUserMixin, View):
    def get(self, request, pk):
        device  = get_object_or_404(SecurityDevice, pk=pk)
        sensors = list(device.sensors.values(
            'SensorKey', 'Name', 'Enabled', 'Category', 'CurrentState',
        ))
        return JsonResponse({
            'buzzer':      device.BuzzerState,
            'bypass':      device.BypassState,
            'temperature': device.Temperature,
            'humidity':    device.Humidity,
            'has_rtc':     device.HasRTC,
            'sd_status':   device.SDStatus,
            'wifi_ok':     device.WifiOK,
            'mqtt_ok':     device.MqttOK,
            'last_seen':   device.LastSeen.strftime('%d/%m/%Y %H:%M:%S') if device.LastSeen else None,
            'sensors':     sensors,
        })
