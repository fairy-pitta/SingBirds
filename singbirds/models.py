from django.db import models
from django.db.models import JSONField 


class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    countryCode = models.CharField(max_length=5, unique=True)
    country_name = models.CharField(max_length=100)

    def __str__(self):
        return self.country_name


class Hotspot(models.Model):
    hotspot_id = models.AutoField(primary_key=True)
    locId = models.CharField(max_length=20, unique=True)
    locName = models.CharField(max_length=255)
    countrycode = models.ForeignKey(Country, on_delete=models.CASCADE)
    subnationalCode = models.CharField(max_length=10, null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    latestObsDate = models.DateField(null=True, blank=True)
    numSpAllTime = models.IntegerField()

    def __str__(self):
        return self.locName


class Bird(models.Model):
    bird_id = models.AutoField(primary_key=True)
    speciesCode = models.CharField(max_length=50, unique=True)
    sciName = models.CharField(max_length=255)
    comName = models.CharField(max_length=255)
    hotspots = models.ManyToManyField(Hotspot, related_name="birds")

    def __str__(self):
        return self.comName


class BirdDetail(models.Model):
    birddetail_id = models.AutoField(primary_key=True)
    recording_url = models.URLField(max_length=500)
    bird_id = models.ForeignKey(Bird, on_delete=models.CASCADE)
    spectrogram = models.ImageField(upload_to='spectrograms/', blank=True, null=True) 

    def __str__(self):
        return f"Recording for {self.bird_id.comName} {self.birddetail_id}"


class AcousticParameters(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    bird_id = models.ForeignKey('Bird', on_delete=models.CASCADE)
    birddetail_id = models.OneToOneField(BirdDetail, on_delete=models.CASCADE)
    
    # 音響特徴量
    mfcc_features = JSONField()  # MFCC特徴量 (リストとして保存)
    chroma_features = JSONField()  # Chroma特徴量 (リストとして保存)
    spectral_bandwidth = models.FloatField()  # スペクトル帯域幅
    spectral_contrast = JSONField()  # スペクトルコントラスト (リストとして保存)
    spectral_flatness = models.FloatField()  # スペクトルフラットネス
    rms_energy = models.FloatField()  # RMSエネルギー
    zero_crossing_rate = models.FloatField()  # ゼロ交差率
    spectral_centroid = models.FloatField()  # スペクトル中心
    spectral_rolloff = models.FloatField()  # スペクトルロールオフ
    created_at = models.DateTimeField(auto_now_add=True)  # レコード作成日時

    def __str__(self):
        return f"Acoustic Parameters for Bird ID: {self.bird_id}"