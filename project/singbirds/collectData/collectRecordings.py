import requests
from ..models import Bird, BirdDetail

def fetch_xeno_canto_recordings():
    base_url = "https://www.xeno-canto.org/api/2/recordings"
    
    birds = Bird.objects.all()
    
    for bird in birds:
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
                    spectrogram_url = recording['sono'].get('full', '')
                    
                    # BirdDetail にデータを保存
                    bird_detail, created = BirdDetail.objects.get_or_create(
                        bird_id=bird,
                        recording_url=recording_url,
                        defaults={
                            'spectrogram': spectrogram_url,
                        }
                    )
                    
                    if created:
                        print(f"Recording added for {bird.comName}: {recording_url}")
                    else:
                        print(f"Recording already exists for {bird.comName}")
                    
                    count += 1  # カウンタを増加
        else:
            print(f"Failed to fetch data for {bird.comName}: {response.status_code}")
