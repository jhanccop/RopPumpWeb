from datetime import datetime, timedelta, timezone

from rest_framework import serializers
from .models import TrapView, WeatherStation, WellAnalyzerDevice

class TrapViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrapView
        fields = [
            'id',
            'IdGateway',
            'DeviceName',
            'DeviceMacAddress',

            'A_TH',
            'SleepTime',
            'runningNN',
            'isContinue',
            'sensibility',
            'Resolution'
        ]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        dtNow = datetime.now(timezone.utc)
        timeNow = dtNow.time()

        print("UTC TIME: ",dtNow)

        timeStart = instance.TimeStart
        timeEnd = instance.TimeEnd
        
        status = False
        if timeNow >= timeStart and timeNow <= timeEnd:
            status = True
        representation["status"] = status
        return representation

class WeatherStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherStation
        fields = [
            'id',
            'IdGateway',
            'DeviceName',
            'DeviceMacAddress',

            'A_TH',
            'A_WP',
            'A_RS',
            'SleepTime',
        ]

class WellAnalyzerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellAnalyzerDevice
        fields = [
            'id',
            'DeviceName',
            'DeviceMacAddress',
            'SamplingRate',
            'RunNNdevice'
        ]