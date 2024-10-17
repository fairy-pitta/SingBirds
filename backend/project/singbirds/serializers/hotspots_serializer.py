from rest_framework import serializers
from ..models import Hotspot

class HotspotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotspot
        fields = ['hotspot_id', 'locId', 'locName', 'countrycode', "subnationalCode", 'lat', 'lng', 'numSpAllTime', 'latestObsDate'] 