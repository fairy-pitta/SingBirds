from django.contrib import admin
from django.contrib import messages
from ..models import BirdDetail
import requests
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')  # 非GUIバックエンドを使用
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile

# カスタムアクションとしてスペクトログラム生成を実装
@admin.action(description="Generate spectrograms for selected birds")
def generate_spectrograms_action(modeladmin, request, queryset):
    # 選択された BirdDetail オブジェクトに対してのみ実行
    for bird_detail in queryset:
        recording_url = bird_detail.recording_url  # 音声ファイルのURLを取得

        if recording_url and not bird_detail.spectrogram:
            try:
                # 音声ファイルをダウンロード
                audio_response = requests.get(recording_url)
                if audio_response.status_code == 200:
                    audio_data = BytesIO(audio_response.content)  # 音声データをメモリに保存

                    # librosaで音声データを読み込み
                    y, sr = librosa.load(audio_data, sr=None)

                    # スペクトログラムを生成
                    plt.figure(figsize=(10, 4))
                    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
                    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log', cmap="viridis")
                    plt.colorbar(format='%+2.0f dB')
                    plt.tight_layout()

                    # スペクトログラムをメモリ内に保存
                    image_buffer = BytesIO()
                    plt.savefig(image_buffer, format='png')
                    plt.close()
                    image_buffer.seek(0)

                    # BirdDetail の ImageField に画像を保存
                    image_file = ContentFile(image_buffer.read(), name=f"spectrogram_{bird_detail.birddetail_id}.png")
                    bird_detail.spectrogram.save(image_file.name, image_file, save=True)

                    print(f"Spectrogram generated and saved for BirdDetail ID: {bird_detail.birddetail_id}")
                else:
                    messages.error(request, f"Failed to download audio for BirdDetail ID: {bird_detail.birddetail_id}")
            except Exception as e:
                messages.error(request, f"Error processing BirdDetail ID: {bird_detail.birddetail_id}: {e}")
        elif bird_detail.spectrogram:
            messages.warning(request, f"Spectrogram already exists for BirdDetail ID: {bird_detail.birddetail_id}")
        else:
            messages.error(request, f"No recording URL found for BirdDetail ID: {bird_detail.birddetail_id}")

    messages.success(request, "Spectrograms generated for selected birds")