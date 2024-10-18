import requests
from ..models import Bird, Hotspot
from dotenv import load_dotenv
import os
from django.contrib import admin

# 環境変数をロード
load_dotenv()

@admin.action(description="選択したホットスポットの情報を取得し鳥データを更新")
def fetch_birds_for_selected_hotspots(modeladmin, request, queryset):
    url_template = "https://api.ebird.org/v2/data/obs/{}/recent"
    
    # API トークンを環境変数から取得
    api_token = os.getenv("ebirdToken")
    headers = {
        "X-eBirdApiToken": api_token
    }

    # 選択されたホットスポットに対して処理を実行
    for hotspot in queryset:
        url = url_template.format(hotspot.locId)
        params = {
            'back': 30  # 過去30日分のデータを取得
        }

        # print(url, "this is url")
        response = requests.get(url, headers=headers, params=params)
        
        # # ステータスコードとレスポンスを出力
        # print(f"Status Code: {response.status_code}") 
        # print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            bird_data = response.json()

            # データが空の場合は処理をスキップ
            if not bird_data:
                print(f"No bird data found for hotspot {hotspot.locId} ({hotspot.locName})")
                continue  # データがない場合は次のホットスポットに進む

            for bird_data_entry in bird_data:
                species_code = bird_data_entry['speciesCode']
                com_name = bird_data_entry.get('comName', 'Unknown')
                sci_name = bird_data_entry.get('sciName', 'Unknown')

                # 鳥の speciesCode を基に Bird モデルを更新
                bird_obj, created = Bird.objects.get_or_create(
                    speciesCode=species_code,
                    defaults={
                        'comName': com_name,
                        'sciName': sci_name,
                    }
                )

                # ホットスポットと鳥の関係を更新
                bird_obj.hotspots.add(hotspot)
                # modeladmin.message_user(request, f"Added {com_name} to hotspot {hotspot.locName}")
                print(f"Added {com_name} to hotspot {hotspot.locName}")  # ターミナルに出力
        else:
            modeladmin.message_user(request, f"Failed to fetch data for hotspot {hotspot.locName}: {response.status_code}", level='error')
            print(f"Failed to fetch data for hotspot {hotspot.locName}: {response.status_code}")  # ターミナルに出力
