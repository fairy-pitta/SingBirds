import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Bird, BirdDetail
from ..serializers.birddetail_serializer import BirdDetailSerializer

@api_view(['GET'])
def random_bird_detail(request, bird_id):
    bird = get_object_or_404(Bird, bird_id=bird_id)
    bird_details = BirdDetail.objects.filter(bird_id=bird)
    
    if bird_details.exists():
        bird_detail = random.choice(bird_details)
        serializer = BirdDetailSerializer(bird_detail)
        return Response({'bird': bird.comName, 'bird_detail': serializer.data})
    else:
        return Response({'message': 'No bird details found for this bird.'}, status=404)