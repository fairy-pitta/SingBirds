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

        # デバッグ: APIリクエストの詳細を表示
        print(f"Requesting recordings for bird: {bird.comName} (Scientific name: {query})")
        print(f"API URL: {base_url} with params: {params}")

        response = requests.get(base_url, params=params)

        # デバッグ: レスポンスのURLとステータスコードを表示
        print(f"API Response URL: {response.url}")
        print(f"API Response Status Code: {response.status_code}")
        
        # APIレスポンスが成功した場合
        if response.status_code == 200:
            data = response.json()

            # デバッグ: 取得したデータの構造を確認
            print(f"API Response Data: {data}")

            count = 0  # カウンタを初期化

            # レスポンスデータ内の録音データを確認
            for recording in data.get('recordings', []):
                if count >= 10:  # 10件保存したら終了
                    print(f"10 recordings already saved for bird: {bird.comName}")
                    break
                
                # デバッグ: 各録音の情報を表示
                print(f"Recording Info: {recording}")

                # 録音の品質が "A" であるかを確認
                if recording.get('q') == 'A':
                    recording_url = recording.get('file')

                    if not recording_url:
                        print(f"Recording URL is missing for bird: {bird.comName}")
                        continue
                    
                    # デバッグ: 録音のURLを表示
                    print(f"Recording URL: {recording_url}")

                    # BirdDetail にデータを保存
                    bird_detail, created = BirdDetail.objects.get_or_create(
                        bird_id=bird,
                        recording_url=recording_url,
                    )
                    
                    if created:
                        message = f"Recording added for {bird.comName}: {recording_url}"
                        print(message)
                        modeladmin.message_user(request, message)
                    else:
                        message = f"Recording already exists for {bird.comName}"
                        print(message)
                        modeladmin.message_user(request, message)

                    count += 1  # カウンタを増加
                else:
                    print(f"Recording skipped for {bird.comName} due to quality: {recording.get('q')}")
        else:
            # APIリクエストが失敗した場合のエラーログ
            error_message = f"Failed to fetch data for {bird.comName}: {response.status_code}"
            print(error_message)
            modeladmin.message_user(request, error_message, level='error')

        # デバッグ: 処理が終了した鳥の情報を表示
        print(f"Finished processing bird: {bird.comName}\n")