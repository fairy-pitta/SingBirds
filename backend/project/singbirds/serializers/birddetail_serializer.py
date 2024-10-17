from rest_framework import serializers
from ..models import BirdDetail

class BirdDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdDetail
        fields = ['recording_url', 'spectrogram', 'bird_id', 'birddetail_id']