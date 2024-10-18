from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
from ..models import Hotspot
from ..serializers.hotspots_serializer import HotspotSerializer


class HotspotListView(APIView):
    def get(self, request, *args, **kwargs):
        # 10種類以上の鳥がいて、かつその鳥が少なくとも1つ以上のBirdDetailを持っているホットスポットのみを取得
        hotspots = Hotspot.objects.annotate(
            valid_bird_count=Count('birds', filter=Q(birds__birddetail__isnull=False), distinct=True)
        ).filter(valid_bird_count__gte=10)

        # シリアライズしてレスポンスを返す
        serializer = HotspotSerializer(hotspots, many=True)
        return Response(serializer.data)