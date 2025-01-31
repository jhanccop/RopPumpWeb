from rest_framework import serializers
from .models import TrapViewData

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