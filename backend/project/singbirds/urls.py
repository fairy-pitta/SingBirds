from django.urls import path
from .views.hotspot_views import HotspotListView 
from .views.bird_views import birds_by_hotspot
from .views.birddetail_views import random_bird_detail

urlpatterns = [
    path('hotspots/', HotspotListView.as_view(), name='hotspot-list'),
    path('hotspots/<int:hotspot_id>/birds/', birds_by_hotspot, name='birds-by-hotspot'),
    path('birds/<int:bird_id>/random-detail/', random_bird_detail, name='random-bird-detail'),
]