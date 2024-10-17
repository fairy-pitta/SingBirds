from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Hotspot
from ..serializers.birds_serializer import BirdSerializer
from django.db.models import Count
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def birds_by_hotspot(request, hotspot_id):
    # Hotspotを取得
    hotspot = get_object_or_404(Hotspot, hotspot_id=hotspot_id)
    
    # birdDetailの数をカウントし、カウントが0でないものだけを取得
    birds = hotspot.birds.annotate(detail_count=Count('birddetail')).filter(detail_count__gt=0)
    
    # シリアライズ
    serializer = BirdSerializer(birds, many=True)
    
    # JSONレスポンスを返す
    return Response({'hotspot': hotspot.locName, 'birds': serializer.data})