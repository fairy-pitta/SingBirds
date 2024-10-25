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

        logger.info(f"Requesting recordings for bird: {bird.comName} (Scientific name: {query})")

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()  # リクエスト失敗時に例外を発生させる
        except requests.RequestException as e:
            error_message = f"Failed to fetch data for {bird.comName}: {e}"
            logger.error(error_message)
            modeladmin.message_user(request, error_message, level='error')
            continue

        data = response.json()
        count = 0  # 保存件数のカウンタ

        # 録音データを個別に処理してメモリ使用量を最小限に抑える
        for recording in data.get('recordings', []):
            if count >= 10:
                logger.info(f"10 recordings saved for bird: {bird.comName}")
                break

            if recording.get('q') == 'A':
                recording_url = recording.get('file')

                if not recording_url:
                    logger.warning(f"Recording URL is missing for bird: {bird.comName}")
                    continue

                bird_detail, created = BirdDetail.objects.get_or_create(
                    bird_id=bird,
                    recording_url=recording_url,
                )

                message = f"Recording {'added' if created else 'already exists'} for {bird.comName}: {recording_url}"
                logger.info(message)
                modeladmin.message_user(request, message)

                count += 1
            else:
                logger.info(f"Skipped recording for {bird.comName} due to quality: {recording.get('q')}")

        # メモリ負荷を軽減するためにデータ削除
        del data, response

        # 各鳥ごとに休憩を挟む
        time.sleep(5)

        # 鳥の処理が終了したことをログに記録
        logger.info(f"Finished processing bird: {bird.comName}\n")