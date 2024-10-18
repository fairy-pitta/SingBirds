import os
import numpy as np
import plotly.express as px
import umap
from sklearn.preprocessing import StandardScaler
from django.conf import settings
from django.contrib import admin
from ..models import AcousticParameters
import ast

# 1. UMAP次元削減とスケーリングのカスタムアクション
@admin.action(description='Perform UMAP and create interactive plot')
def perform_umap_action(modeladmin, request, queryset):
    # 選択されたデータから音響パラメータを取得
    features = []
    bird_ids = []  # bird_id を格納するリスト
    bird_names = []  # 鳥の名前を格納するリスト（表示用）

    for record in queryset:
        try:
            # JSON形式から配列に変換し、空の場合はゼロ配列を設定
            # もし文字列ならリストに変換する
            mfcc = ast.literal_eval(record.mfcc_features) if record.mfcc_features else np.zeros(13)
            chroma = ast.literal_eval(record.chroma_features) if record.chroma_features else np.zeros(12)
            spectral_contrast = ast.literal_eval(record.spectral_contrast) if record.spectral_contrast else np.zeros(7)

            # それぞれの次元を確認しながら結合
            mfcc = np.array(mfcc) if len(mfcc) == 13 else np.zeros(13)
            chroma = np.array(chroma) if len(chroma) == 12 else np.zeros(12)
            spectral_contrast = np.array(spectral_contrast) if len(spectral_contrast) == 7 else np.zeros(7)

            if mfcc.shape == (13,) and chroma.shape == (12,) and spectral_contrast.shape == (7,):
                # 各パラメータを結合して特徴ベクトルを作成
                feature_vector = np.concatenate([
                    mfcc, chroma,
                    [record.spectral_bandwidth] if record.spectral_bandwidth is not None else [0],
                    [record.spectral_flatness] if record.spectral_flatness is not None else [0],
                    spectral_contrast,
                    [record.rms_energy] if record.rms_energy is not None else [0],
                    [record.zero_crossing_rate] if record.zero_crossing_rate is not None else [0],
                    [record.spectral_centroid] if record.spectral_centroid is not None else [0],
                    [record.spectral_rolloff] if record.spectral_rolloff is not None else [0]
                ])
                features.append(feature_vector)
                bird_ids.append(record.bird_id.bird_id)  # bird_idを保存
                bird_names.append(record.bird_id.comName)
                
            else:
                modeladmin.message_user(request, f"Error: Dimension mismatch for record {record.bird_id}")
                continue  # 次のレコードに進む

        except Exception as e:
            modeladmin.message_user(request, f"Error processing record {record.bird_id}: {e}")
            continue

    if len(features) == 0:
        modeladmin.message_user(request, "No valid features to process.")
        return

    # 2. データのスケーリング
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(np.array(features))

    # 3. UMAPで次元削減を実行
    reducer = umap.UMAP(n_components=2, random_state=42)
    reduced_data = reducer.fit_transform(features_scaled)

    # 4. インタラクティブなプロットを作成 (Plotly)
    fig = px.scatter(
        x=reduced_data[:, 0],
        y=reduced_data[:, 1],
        color=bird_ids,  # bird_idごとに色を分ける
        hover_name=bird_names,  # 鳥の名前をホバーで表示
        title="UMAP Result with Scaling",
        labels={"x": "UMAP 1", "y": "UMAP 2"}
    )

    fig.update_layout(
        dragmode="zoom",  # デフォルトでズームモードを有効に
        hovermode="closest",  # ホバーで最も近い点を表示
        plot_bgcolor="rgba(0,0,0,0)",  # 背景を透明に
        margin=dict(l=0, r=0, t=50, b=0),  # 余白を調整
        xaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        ),
    )

    # 5. インタラクティブプロットをHTMLとして保存
    media_path = os.path.join(settings.MEDIA_ROOT, 'umap_result_interactive_few4.html')
    fig.write_html(media_path)

    # 管理者に保存先を通知
    modeladmin.message_user(request, f'UMAPインタラクティブプロットを {media_path} に保存しました')
