from django.db import models


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