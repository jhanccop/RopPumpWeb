from rest_framework import serializers
from .models import TrapViewData, WeatherStationData

class TrapViewDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrapViewData
        fields = [
            'IdDevice',

            'Humidity',
            'Temperature',
            'VoltageBattery',

            'Objective',
            'nDetected',
            'img64',
            'img_bool',
            'Status'
        ]

class WeatherStationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherStationData
        fields = [
            'IdDevice',

            'Humidity',
            'Temperature',
            'VoltageBattery',

            'WindVelocity',
            'WindDirection',
            'RainCounter',
            'Radiation',
            'Status'
        ]