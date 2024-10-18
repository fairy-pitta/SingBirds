from django.contrib import admin
from ..models import Bird, BirdDetail
import requests

@admin.action(description="選択した鳥に対してXeno-Cantoの録音を取得")
def fetch_xeno_canto_recordings(modeladmin, request, queryset):
    base_url = "https://www.xeno-canto.org/api/2/recordings"
    
    for bird in queryset:
        query = bird.sciName
        
        params = {
            'query': f"{query} len:0-30 q:A"
        }

        response = requests.get(base_url, params=params)

        print(f"URL: {response.url}")

        if response.status_code == 200:
            data = response.json()

            count = 0  # カウンタを初期化

            for recording in data['recordings']:
                if count >= 10:  # 10件保存したら終了
                    break
                
                if recording['q'] == 'A':
                    recording_url = recording['file']
                    
                    # BirdDetail にデータを保存
                    bird_detail, created = BirdDetail.objects.get_or_create(
                        bird_id=bird,
                        recording_url=recording_url,
                    )
                    
                    if created:
                        modeladmin.message_user(request, f"Recording added for {bird.comName}: {recording_url}")
                    else:
                        modeladmin.message_user(request, f"Recording already exists for {bird.comName}")
                    
                    count += 1  # カウンタを増加
        else:
            modeladmin.message_user(request, f"Failed to fetch data for {bird.comName}: {response.status_code}", level='error')
