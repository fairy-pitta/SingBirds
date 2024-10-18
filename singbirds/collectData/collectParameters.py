from django.contrib import admin
from django.db import transaction
from ..models import BirdDetail, AcousticParameters, Bird
import librosa
import requests
from io import BytesIO
import json
import numpy as np
import concurrent.futures

# 音響特徴量を抽出する関数（無音部分を除去）
# 音響特徴量を抽出する関数（無音部分を除去してトリム）
def extract_features(audio_data, sr, silence_threshold=0.01):
    # 無音部分の除去: librosa.effects.splitで無音区間を除去
    non_silent_intervals = librosa.effects.split(audio_data, top_db=30)  # Adjust top_db to control silence sensitivity

    # 有音区間を結合して新しい音声データを作成
    trimmed_audio = np.concatenate([audio_data[start:end] for start, end in non_silent_intervals])

    # MFCC特徴量の抽出
    mfccs = librosa.feature.mfcc(y=trimmed_audio, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs, axis=1).astype(np.float16).tolist()
    
    # Chroma特徴量
    chroma_stft = librosa.feature.chroma_stft(y=trimmed_audio, sr=sr)
    chroma_mean = np.mean(chroma_stft, axis=1).astype(np.float16).tolist()
    
    # スペクトル帯域幅
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=trimmed_audio, sr=sr)).item()
    
    # スペクトルコントラスト
    spectral_contrast = librosa.feature.spectral_contrast(y=trimmed_audio, sr=sr)
    spectral_contrast_mean = np.mean(spectral_contrast, axis=1).astype(np.float16).tolist()
    
    # スペクトルフラットネス
    spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=trimmed_audio)).item()
    
    # RMSエネルギー
    rms_energy = np.mean(librosa.feature.rms(y=trimmed_audio)).item()
    
    # ゼロ交差率
    zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y=trimmed_audio)).item()
    
    # スペクトル中心
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=trimmed_audio, sr=sr)).item()
    
    # スペクトルロールオフ
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=trimmed_audio, sr=sr)).item()
    
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

# BirdDetailごとに音声データを処理する関数
def process_bird_detail(bird_detail):
    try:
        # recording_urlから音声データをダウンロード
        response = requests.get(bird_detail.recording_url)
        response.raise_for_status()

        # librosaで音声データを読み込む
        audio_data, sr = librosa.load(BytesIO(response.content), sr=16000)  # 16kHz sampling

        # 音響特徴量の抽出（無音部分の除去）
        features = extract_features(audio_data, sr)

        # AcousticParametersインスタンスを作成
        acoustic_param = AcousticParameters(
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
        return acoustic_param, None  # 正常に処理できた場合

    except Exception as e:
        return None, f'Failed to process BirdDetail ID {bird_detail.birddetail_id}: {e}'  # エラー発生時

# 選択されたBirdDetailの録音から特徴量を抽出し、AcousticParametersにバルクで保存するアクション
@admin.action(description='Extract acoustic features for selected BirdDetails')
def sync_extract_acoustic_features(modeladmin, request, queryset):
    acoustic_parameters_to_create = []  # バルクインサート用のリスト
    errors = []  # エラーメッセージを格納するリスト
    batch_size = 100  # バッチサイズの設定

    # 並列処理で音響特徴量を抽出
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_bird_detail, bird_detail) for bird_detail in queryset]

        for future in concurrent.futures.as_completed(futures):
            result, error = future.result()
            if result:
                acoustic_parameters_to_create.append(result)
                print(f"Appended: {len(acoustic_parameters_to_create)} records")

                # バッチサイズに達したらデータベースに保存
                if len(acoustic_parameters_to_create) >= batch_size:
                    try:
                        AcousticParameters.objects.bulk_create(acoustic_parameters_to_create)
                        print(f'Successfully processed {len(acoustic_parameters_to_create)} records')
                        acoustic_parameters_to_create = []  # 保存後にリストをクリア
                    except Exception as e:
                        print(f'Failed to bulk insert: {e}')

            if error:
                errors.append(error)  # エラーメッセージを格納

    # 最後に残っているレコードを保存（バッチサイズに満たない分）
    if acoustic_parameters_to_create:
        try:
            AcousticParameters.objects.bulk_create(acoustic_parameters_to_create)
            print(f'Successfully processed {len(acoustic_parameters_to_create)} remaining records')
        except Exception as e:
            print(f'Failed to bulk insert: {e}')

    # エラーがあれば表示
    if errors:
        for error in errors:
            print(error)