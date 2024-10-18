import pandas as pd
import librosa
import requests
from io import BytesIO
import numpy as np
import csv

# 無音部分の除去を含む音響特徴量の抽出関数
def extract_features(audio_data, sr, silence_threshold=0.01):
    # 無音部分の除去: 短時間エネルギー（RMS）が閾値以下の部分を無視
    rms = librosa.feature.rms(y=audio_data)[0]
    non_silent_indices = np.where(rms > silence_threshold)[0]
    
    # 無音部分を除去した音声信号を作成
    if len(non_silent_indices) > 0:
        audio_data = audio_data[np.concatenate([np.arange(start, start + sr) for start in non_silent_indices])]
    
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

# CSVファイルのインポートと音響データ処理
def process_audio_features(input_csv_path, output_csv_path):
    # CSVファイルを読み込む
    data = pd.read_csv(input_csv_path)
    
    # 結果を保存するリスト
    results = []
    
    # 各レコードに対して処理
    for index, row in data.iterrows():
        birddetail_id = row['birddetail_id']
        recording_url = row['recording_url']

        try:
            # recording_urlから音声データをダウンロード
            response = requests.get(recording_url)
            response.raise_for_status()

            # librosaで音声データを読み込む
            audio_data, sr = librosa.load(BytesIO(response.content), sr=None)

            # 音響特徴量の抽出（無音部分を除去）
            features = extract_features(audio_data, sr)
            
            # 結果を保存する
            results.append({
                'birddetail_id': birddetail_id,
                'mfcc_features': features['mfcc_features'],
                'chroma_features': features['chroma_features'],
                'spectral_bandwidth': features['spectral_bandwidth'],
                'spectral_contrast': features['spectral_contrast'],
                'spectral_flatness': features['spectral_flatness'],
                'rms_energy': features['rms_energy'],
                'zero_crossing_rate': features['zero_crossing_rate'],
                'spectral_centroid': features['spectral_centroid'],
                'spectral_rolloff': features['spectral_rolloff']
            })
        
        except Exception as e:
            print(f"Failed to process {birddetail_id} due to {e}")
    
    # 結果を新しいCSVファイルに書き込む
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['birddetail_id', 'mfcc_features', 'chroma_features', 'spectral_bandwidth', 
                    'spectral_contrast', 'spectral_flatness', 'rms_energy', 
                    'zero_crossing_rate', 'spectral_centroid', 'spectral_rolloff']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # ヘッダーを書き込む
        writer.writeheader()

        # 行を書き込む
        for result in results:
            writer.writerow(result)

# 実行例
input_csv = 'test.csv'  # 入力CSVファイルのパス
output_csv = 'output.csv'  # 出力CSVファイルのパス
process_audio_features(input_csv, output_csv)