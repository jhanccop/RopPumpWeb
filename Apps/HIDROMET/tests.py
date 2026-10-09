import json
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from Apps.company.models import Company
from Apps.users.models import User, Application
from .models import HydroStation, HydroReading


class HidrometViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        company = Company.objects.create(CompanyName='HydroCo', LocationState='Cusco', LocationCounty='Urubamba')
        other = Company.objects.create(CompanyName='OtherCo', LocationState='Lima', LocationCounty='Lima')

        cls.user = User.objects.create_user('hm_admin', 'hm@test.com', 'pass1234',
                                            CompanyId=company, Role='admin')
        cls.user.Applications.add(Application.objects.get(Code='hidromet'))
        cls.no_access = User.objects.create_user('no_hm', 'no@test.com', 'pass1234', CompanyId=company)
        cls.outsider = User.objects.create_user('out', 'out@test.com', 'pass1234', CompanyId=other)

        cls.station = HydroStation.objects.create(
            Owner=cls.user, StationName='Rio Vilcanota', WaterBodyName='Vilcanota',
            Latitude=-13.3, Longitude=-72.1, LevelWarning=1.5, LevelCritical=2.0,
            MacAddress='AA:BB:CC:DD:EE:FF', HasWaterPH=True, HasWaterTemp=True,
            HasWind=True, HasPrecipitation=True, HasSolarRadiation=True,
        )
        cls.foreign_station = HydroStation.objects.create(Owner=cls.outsider, StationName='Ajena')
        now = datetime.utcnow()
        for i, level in enumerate((1.2, 1.7, 2.3)):
            HydroReading.objects.create(
                Station=cls.station, DateCreate=now - timedelta(hours=3 - i), LocalTimestamp=now,
                Temperature=18.5, Humidity=70, WindDirection=200, WindSpeed=3.2,
                Precipitation=0.4, SolarRadiation=500, WaterLevel=level, WaterPH=7.4,
                WaterTemperature=12.1, VoltageBattery=3.9,
            )

    def setUp(self):
        self.client.force_login(self.user)

    def test_application_registered(self):
        app = Application.objects.get(Code='hidromet')
        self.assertEqual(app.DashboardUrl, '/hidromet/')

    def test_level_state(self):
        self.assertEqual(self.station.level_state(1.0), 'normal')
        self.assertEqual(self.station.level_state(1.6), 'warning')
        self.assertEqual(self.station.level_state(2.0), 'critical')
        self.assertIsNone(self.station.level_state(None))

    def test_private_pages_render(self):
        pk = self.station.pk
        for name, args in (
            ('dashboard', []), ('station_list', []), ('station_add', []),
            ('station_update', [pk]), ('station_remove', [pk]), ('station_detail', [pk]),
            ('reading_list', []), ('reading_add', []), ('report', []),
        ):
            with self.subTest(name=name):
                resp = self.client.get(reverse(f'hidromet:{name}', args=args))
                self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('hidromet:dashboard'))
        self.assertEqual(resp.context['level_alerts'], 1)
        self.assertContains(resp, 'Rio Vilcanota')

    def _chart_json(self, resp):
        html = resp.content.decode()
        start = html.index('<script id="hm-data" type="application/json">') + len('<script id="hm-data" type="application/json">')
        return json.loads(html[start:html.index('</script>', start)])

    def test_chart_json_is_valid(self):
        data = self._chart_json(self.client.get(reverse('hidromet:station_detail', args=[self.station.pk])))
        self.assertEqual(data['level'], [1.2, 1.7, 2.3])
        self.assertEqual(data['critical'], 2.0)

        self.station.LevelWarning = self.station.LevelCritical = None
        self.station.save()
        self.client.logout()
        data = self._chart_json(self.client.get(reverse('hidromet:public_detail', args=[self.station.pk])))
        self.assertIsNone(data['warning'])
        self.assertEqual(len(data['dates']), 3)

    def test_river_animation(self):
        resp = self.client.get(reverse('hidromet:station_detail', args=[self.station.pk]))
        self.assertContains(resp, 'id="hm-river"')
        self.assertContains(resp, 'data-level="2.300000"')
        self.assertContains(resp, 'data-critical="2.000000"')

        self.assertContains(resp, 'data-has-wind="1"')
        self.assertContains(resp, 'data-ws="3.200000"')

        # Sin sensor de nivel la escena se muestra igual, con el resto de sensores
        self.station.HasWaterLevel = False
        self.station.HasWind = False
        self.station.save()
        resp = self.client.get(reverse('hidromet:station_detail', args=[self.station.pk]))
        self.assertContains(resp, 'id="hm-river"')
        self.assertContains(resp, 'data-has-level="0"')
        self.assertContains(resp, 'data-has-wind="0"')

    def test_detail_table_only_enabled_sensors(self):
        url = reverse('hidromet:station_detail', args=[self.station.pk])

        def table(resp):
            html = resp.content.decode()
            html = html[html.index('id="readings-table"'):]
            return html[:html.index('</table>')]

        t = table(self.client.get(url))
        self.assertIn('Prec mm', t)
        self.assertEqual(t.count('<th '), 12)

        self.station.HasWind = self.station.HasPrecipitation = self.station.HasWaterPH = False
        self.station.save()
        t = table(self.client.get(url))
        for label in ('Viento m/s', 'Prec mm', '>pH<'):
            self.assertNotIn(label, t)
        head, body = t.split('<tbody>')
        self.assertEqual(head.count('<th '), 8)
        first_row = body[:body.index('</tr>')]
        self.assertEqual(first_row.count('<td '), 8)

    def test_tare_flow_height(self):
        self.station.LevelTare = 3.0
        self.station.save()
        r = HydroReading.objects.create(Station=self.station, DateCreate=datetime.utcnow(), RawDistance=1.25)
        self.assertAlmostEqual(r.WaterLevel, 1.75)
        self.assertEqual(self.station.flow_height(None), None)

        resp = self.client.get(reverse('hidromet:station_detail', args=[self.station.pk]))
        self.assertContains(resp, 'data-tare="3.000000"')
        self.assertContains(resp, 'data-raw="1.250000"')
        self.assertContains(resp, '3.000 m')
        self.assertNotContains(resp, 'no tiene <strong>tara de altura</strong>')

    def test_missing_tare_warning(self):
        resp = self.client.get(reverse('hidromet:station_detail', args=[self.station.pk]))
        self.assertContains(resp, 'no tiene <strong>tara de altura</strong>')

    def _update_station(self, **extra):
        data = {
            'Owner': self.user.pk, 'StationName': self.station.StationName, 'WaterBodyType': 'Rio',
            'TimeSleep': '15m', 'Status': 'Active', 'HasWaterLevel': 'on',
            'LevelWarning': '1.5', 'LevelCritical': '2.0',
        }
        data.update(extra)
        return self.client.post(reverse('hidromet:station_update', args=[self.station.pk]), data)

    def test_tare_recalc_history(self):
        HydroReading.objects.filter(Station=self.station).update(RawDistance=1.0, WaterLevel=None)

        # Sin marcar "recalcular", el histórico no cambia
        self.assertEqual(self._update_station(LevelTare='2.5').status_code, 302)
        self.assertFalse(HydroReading.objects.filter(Station=self.station, WaterLevel__isnull=False).exists())

        resp = self._update_station(LevelTare='2.5', recalc_history='on')
        self.assertRedirects(resp, reverse('hidromet:station_detail', args=[self.station.pk]),
                             fetch_redirect_response=False)
        levels = set(HydroReading.objects.filter(Station=self.station).values_list('WaterLevel', flat=True))
        self.assertEqual(levels, {1.5})

    def test_tare_validation(self):
        self.assertEqual(self._update_station(LevelTare='-1').status_code, 200)
        self.assertEqual(self._update_station(recalc_history='on').status_code, 200)  # sin tara

    def test_public_pages_render_anonymous(self):
        self.client.logout()
        resp = self.client.get(reverse('hidromet:public'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Rio Vilcanota')
        for days in ('7', '0', 'abc'):
            resp = self.client.get(reverse('hidromet:public_detail', args=[self.station.pk]), {'days': days})
            self.assertEqual(resp.status_code, 200)

    def test_access_control(self):
        self.client.force_login(self.no_access)
        resp = self.client.get(reverse('hidromet:dashboard'))
        self.assertRedirects(resp, reverse('user_app:no_access'), fetch_redirect_response=False)

        # Una estación de otra compañía no es accesible
        self.client.force_login(self.user)
        resp = self.client.get(reverse('hidromet:station_detail', args=[self.foreign_station.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_create_station_and_reading(self):
        resp = self.client.post(reverse('hidromet:station_add'), {
            'Owner': self.user.pk, 'StationName': 'Quebrada Honda', 'WaterBodyType': 'Quebrada',
            'TimeSleep': '15m', 'Status': 'Active', 'HasWaterLevel': 'on',
            'LevelWarning': '1', 'LevelCritical': '2',
        })
        self.assertEqual(resp.status_code, 302)
        st = HydroStation.objects.get(StationName='Quebrada Honda')

        resp = self.client.post(reverse('hidromet:reading_add'), {
            'Station': st.pk, 'DateCreate': '2026-10-02T10:00', 'RawDistance': '0.85', 'WaterPH': '7.1',
        })
        self.assertEqual(resp.status_code, 302)
        r = HydroReading.objects.get(Station=st)
        self.assertEqual(r.DateCreate, datetime(2026, 10, 2, 15, 0))  # Lima → UTC
        self.assertIsNone(r.WaterLevel)  # estación sin tara: no se puede calcular la altura

    def test_invalid_thresholds_and_ph(self):
        resp = self.client.post(reverse('hidromet:station_add'), {
            'Owner': self.user.pk, 'StationName': 'X', 'WaterBodyType': 'Rio',
            'TimeSleep': '15m', 'Status': 'Active', 'LevelWarning': '3', 'LevelCritical': '2',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(HydroStation.objects.filter(StationName='X').exists())

        resp = self.client.post(reverse('hidromet:reading_add'), {
            'Station': self.station.pk, 'DateCreate': '2026-10-02T10:00', 'WaterPH': '15',
        })
        self.assertEqual(resp.status_code, 200)

    def test_report_and_csv(self):
        today = datetime.utcnow().date()
        data = {'date_from': (today - timedelta(days=2)).isoformat(), 'date_to': today.isoformat()}
        resp = self.client.post(reverse('hidromet:report'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['total'], 3)

        resp = self.client.post(reverse('hidromet:report'), dict(data, download='1'))
        self.assertEqual(resp['Content-Type'], 'text/csv; charset=utf-8')
        body = resp.content.decode('utf-8-sig')
        self.assertIn('Distancia medida (m),Altura del flujo (m)', body)
        self.assertIn('Rio Vilcanota', body)

    def test_admin_panel_integration(self):
        resp = self.client.get(reverse('user_app:admin_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['hm_stations_count'], 1)
        self.assertEqual(resp.context['hm_level_alerts'], 1)
        self.assertContains(resp, reverse('hidromet:dashboard'))

    def test_django_admin(self):
        su = User.objects.create_superuser('root', 'root@test.com', 'pass1234')
        self.client.force_login(su)
        for url in ('admin:hidromet_hydrostation_changelist', 'admin:hidromet_hydroreading_changelist',
                    'admin:hidromet_hydrostation_add'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(reverse(url)).status_code, 200)
