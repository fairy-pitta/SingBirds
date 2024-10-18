import os
import ast
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from django.conf import settings
from django.contrib import admin
from ..models import AcousticParameters
from sklearn.metrics.pairwise import cosine_distances
import matplotlib.cm as cm 
import plotly.express as px

@admin.action(description='PerformNMDS') 
def perform_nmds_action(modeladmin, request, queryset):
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
                bird_ids.append(record.bird_id)  # bird_idを保存
                bird_names.append(record.bird_id.comName)  # 鳥の名前を保存
            else:
                modeladmin.message_user(request, f"Error: Dimension mismatch for record {record.bird_id}")
                continue  # 次のレコードに進む

        except Exception as e:
            modeladmin.message_user(request, f"Error processing record {record.bird_id}: {e}")
            continue

    if len(features) == 0:
        modeladmin.message_user(request, "No valid features to process.")
        return

    features = np.array(features)

    # 2. コサイン距離行列を計算
    cosine_dist_matrix = cosine_distances(features)

    # 3. NMDSの次元削減を実行（コサイン距離行列を使用）
    nmds = MDS(n_components=2, metric=False, dissimilarity='precomputed', random_state=42)
    reduced_data = nmds.fit_transform(cosine_dist_matrix)

    # 4. インタラクティブなプロットを作成 (Plotly)
    fig = px.scatter(
        x=reduced_data[:, 0], 
        y=reduced_data[:, 1],
        color=bird_ids,  # bird_idごとに色を分ける
        hover_name=bird_names,  # 鳥の名前をホバーで表示
        title="NMDS Result (Cosine Similarity)",
        labels={"x": "Component 1", "y": "Component 2"}
    )

    # 5. インタラクティブプロットをHTMLとして保存
    media_path = os.path.join(settings.MEDIA_ROOT, 'nmds_cosine_result_part.html')
    fig.write_html(media_path)

    # 管理者に保存先を通知
    modeladmin.message_user(request, f'NMDSインタラクティブプロットを {media_path} に保存しました')
    #    # 選択されたデータから音響パラメータを取得
    # features = []
    # bird_ids = []  # bird_id を格納するリスト
    # for record in queryset:
    #     try:
    #         # JSON形式から配列に変換し、空の場合はゼロ配列を設定
    #         mfcc = ast.literal_eval(record.mfcc_features) if record.mfcc_features else np.zeros(13)
    #         chroma = ast.literal_eval(record.chroma_features) if record.chroma_features else np.zeros(12)
    #         spectral_contrast = ast.literal_eval(record.spectral_contrast) if record.spectral_contrast else np.zeros(7)

    #         # それぞれの次元を確認しながら結合
    #         mfcc = np.array(mfcc) if len(mfcc) == 13 else np.zeros(13)
    #         chroma = np.array(chroma) if len(chroma) == 12 else np.zeros(12)
    #         spectral_contrast = np.array(spectral_contrast) if len(spectral_contrast) == 7 else np.zeros(7)

    #         if mfcc.shape == (13,) and chroma.shape == (12,) and spectral_contrast.shape == (7,):
    #             # 各パラメータを結合して特徴ベクトルを作成
    #             feature_vector = np.concatenate([
    #                 mfcc, chroma,
    #                 [record.spectral_bandwidth] if record.spectral_bandwidth is not None else [0],
    #                 [record.spectral_flatness] if record.spectral_flatness is not None else [0],
    #                 spectral_contrast,
    #                 [record.rms_energy] if record.rms_energy is not None else [0],
    #                 [record.zero_crossing_rate] if record.zero_crossing_rate is not None else [0],
    #                 [record.spectral_centroid] if record.spectral_centroid is not None else [0],
    #                 [record.spectral_rolloff] if record.spectral_rolloff is not None else [0]
    #             ])
    #             features.append(feature_vector)
    #             bird_ids.append(record.bird_id)  # bird_idを保存
    #         else:
    #             modeladmin.message_user(request, f"Error: Dimension mismatch for record {record.bird.species_name}")
    #             continue  # 次のレコードに進む

    #     except Exception as e:
    #         modeladmin.message_user(request, f"Error processing record {record.id}: {e}")
    #         continue

    # if len(features) == 0:
    #     modeladmin.message_user(request, "No valid features to process.")
    #     return

    # features = np.array(features)

    # # 2. コサイン距離行列を計算
    # cosine_dist_matrix = cosine_distances(features)

    # # 3. NMDSの次元削減を実行（コサイン距離行列を使用）
    # nmds = MDS(n_components=2, metric=False, dissimilarity='precomputed', random_state=42)
    # reduced_data = nmds.fit_transform(cosine_dist_matrix)

    # # 4. 異なるbird_idごとに異なる色を割り当てる
    # unique_bird_ids = list(set(bird_ids))  # 重複を排除したbird_idのリスト
    # colors = cm.rainbow(np.linspace(0, 1, len(unique_bird_ids)))  # カラーマップで異なる色を生成

    # # bird_idに対応する色を割り振る
    # bird_colors = {bird_id: color for bird_id, color in zip(unique_bird_ids, colors)}

    # # 5. 結果をプロットしてメディアディレクトリに保存
    # media_path = os.path.join(settings.MEDIA_ROOT, 'nmds_cosine_result.png')
    # plt.figure()

    # # プロット
    # for i, (x, y) in enumerate(reduced_data):
    #     plt.scatter(x, y, color=bird_colors[bird_ids[i]], label=bird_ids[i] if bird_ids[i] not in plt.gca().get_legend_handles_labels()[1] else "")  # 同じbird_idのラベルは一度だけ表示

    # plt.title('NMDS Result (Cosine Similarity)')
    # plt.xlabel('Component 1')
    # plt.ylabel('Component 2')
    # # plt.legend(loc='best', title="Bird ID")  # 凡例を表示

    # plt.savefig(media_path)
    # plt.close()

    # # 管理者に保存先を通知
    # modeladmin.message_user(request, f'NMDSプロットを {media_path} に保存しました')