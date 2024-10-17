from ..models import Bird
from rest_framework import serializers

class BirdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bird
        fields = ['bird_id', 'speciesCode', 'sciName', 'comName'] 