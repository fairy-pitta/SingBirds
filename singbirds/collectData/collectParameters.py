from django.contrib import admin
from ..models import BirdDetail, AcousticParameters, Bird
import librosa
import requests
from io import BytesIO
import json
import numpy as np

# 音響特徴量を抽出する関数
def extract_features(audio_data, sr):
    # MFCC特徴量の抽出
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs, axis=1).tolist()
    
    # Chroma特徴量
    chroma_stft = librosa.feature.chroma_stft(y=audio_data, sr=sr)
    chroma_mean = np.mean(chroma_stft, axis=1).tolist()
    
    # スペクトル帯域幅
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sr))
    
    # スペクトルコントラスト
    spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
    spectral_contrast_mean = np.mean(spectral_contrast, axis=1).tolist()
    
    # スペクトルフラットネス
    spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=audio_data))
    
    # RMSエネルギー
    rms_energy = np.mean(librosa.feature.rms(y=audio_data))

    # ゼロ交差率
    zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y=audio_data))

    # スペクトル中心
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))

    # スペクトルロールオフ
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr))
    
    # 抽出した特徴量を辞書として返す
    return {
        "mfcc_features": mfccs_mean,
        "chroma_features": chroma_mean,
        "spectral_bandwidth": spectral_bandwidth,
        "spectral_contrast": spectral_contrast_mean,
        "spectral_flatness": spectral_flatness,
        "rms_energy": rms_energy,
        "zero_crossing_rate": zero_crossing_rate,
        "spectral_centroid": spectral_centroid,
        "spectral_rolloff": spectral_rolloff
    }

# 選択されたBirdDetailの録音から特徴量を抽出し、AcousticParametersに保存するアクション
@admin.action(description='Extract acoustic features for selected BirdDetails')
def extract_acoustic_features(modeladmin, request, queryset):
    for bird_detail in queryset:
        try:
            # recording_urlから音声データをダウンロード
            response = requests.get(bird_detail.recording_url)
            response.raise_for_status()
            
            # librosaで音声データを読み込む
            audio_data, sr = librosa.load(BytesIO(response.content), sr=None)
            
            # 音響特徴量の抽出
            features = extract_features(audio_data, sr)
            
            # AcousticParametersテーブルにデータを保存
            AcousticParameters.objects.create(
                bird_id=bird_detail.bird_id,
                birddetail_id=bird_detail,
                mfcc_features=json.dumps(features['mfcc_features']),
                chroma_features=json.dumps(features['chroma_features']),
                spectral_bandwidth=features['spectral_bandwidth'],
                spectral_contrast=json.dumps(features['spectral_contrast']),
                spectral_flatness=features['spectral_flatness'],
                rms_energy=features['rms_energy'],
                zero_crossing_rate=features['zero_crossing_rate'],
                spectral_centroid=features['spectral_centroid'],
                spectral_rolloff=features['spectral_rolloff']
            )
            modeladmin.message_user(request, f'Successfully processed BirdDetail ID {bird_detail.birddetail_id}')
            print(f'Successfully processed BirdDetail ID {bird_detail.birddetail_id}')

        except Exception as e:
            modeladmin.message_user(request, f'Failed to process BirdDetail ID {bird_detail.birddetail_id}: {e}', level='error')
            print(f'Failed to process BirdDetail ID {bird_detail.birddetail_id}: {e}')
