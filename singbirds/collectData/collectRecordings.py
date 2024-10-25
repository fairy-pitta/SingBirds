from django.contrib import admin
from ..models import Bird, BirdDetail
import requests
import time
import logging

# ロガーの設定
logger = logging.getLogger("app")

@admin.action(description="選択した鳥に対してXeno-Cantoの録音を取得")
def fetch_xeno_canto_recordings(modeladmin, request, queryset):
    base_url = "https://www.xeno-canto.org/api/2/recordings"
    
    for bird in queryset:
        query = bird.sciName
        params = {
            'query': f"{query} len:0-30 q:A"
        }

        # # ログ: APIリクエストの詳細を表示
        # logger.info(f"Requesting recordings for bird: {bird.comName} (Scientific name: {query})")
        # logger.info(f"API URL: {base_url} with params: {params}")

        response = requests.get(base_url, params=params)

        # レスポンスのURLとステータスコードをログに記録
        logger.info(f"API Response URL: {response.url}")
        logger.info(f"API Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"API Response Data for {bird.comName}: {data}")

            count = 0  # 保存件数のカウンタ

            for recording in data.get('recordings', []):
                if count >= 10:  # 10件保存したら終了
                    logger.info(f"10 recordings already saved for bird: {bird.comName}")
                    break

                if recording.get('q') == 'A':
                    recording_url = recording.get('file')

                    if not recording_url:
                        logger.warning(f"Recording URL is missing for bird: {bird.comName}")
                        continue

                    # BirdDetail にデータを保存
                    bird_detail, created = BirdDetail.objects.get_or_create(
                        bird_id=bird,
                        recording_url=recording_url,
                    )

                    if created:
                        message = f"Recording added for {bird.comName}: {recording_url}"
                        logger.info(message)
                        modeladmin.message_user(request, message)
                    else:
                        message = f"Recording already exists for {bird.comName}"
                        logger.info(message)
                        modeladmin.message_user(request, message)

                    count += 1
                else:
                    logger.info(f"Recording skipped for {bird.comName} due to quality: {recording.get('q')}")
        else:
            error_message = f"Failed to fetch data for {bird.comName}: {response.status_code}"
            logger.error(error_message)
            modeladmin.message_user(request, error_message, level='error')

        # 5秒間の休憩
        time.sleep(5)

        # 処理が終了した鳥の情報を表示
        logger.info(f"Finished processing bird: {bird.comName}\n")