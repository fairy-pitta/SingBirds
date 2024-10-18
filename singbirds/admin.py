from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Country, Hotspot, Bird, BirdDetail, AcousticParameters
from import_export import resources 
from import_export.admin import ImportExportModelAdmin
from .collectData.collectCountries import fetch_and_save_countries
from .collectData.collectHotspots import fetch_and_save_hotspots_by_country
from .collectData.collectBirds import fetch_and_save_birds_by_country
from .collectData.collectObservations import fetch_birds_for_selected_hotspots
from .collectData.collectRecordings import fetch_xeno_canto_recordings
from .collectData.createSpectrogram import generate_spectrograms_action
from .collectData.collectParameters import sync_extract_acoustic_features
from .collectData.getNMDS import perform_nmds_action
from .collectData.getUMAP import perform_umap_action


@admin.action(description='Fetch and save countries from eBird API')
def fetch_countries_action(modeladmin, request, queryset):
    try:
        fetch_and_save_countries()
        messages.success(request, "Countries fetched and saved successfully.")
    except Exception as e:
        messages.error(request, f"Error fetching countries: {e}")

@admin.action(description="選択した国に基づいてホットスポットを取得")
def fetch_hotspots_for_selected_countries(modeladmin, request, queryset):
    for country in queryset:
        # Country モデルの countryCode を渡す
        fetch_and_save_hotspots_by_country(country.countryCode)
        modeladmin.message_user(request, f"Fetched hotspots for {country.country_name} ({country.countryCode})")


@admin.action(description="選択した国の鳥データを取得")
def fetch_birds_for_selected_countries(modeladmin, request, queryset):
    for country in queryset:
        # 選択された国の countryCode を使用
        fetch_and_save_birds_by_country(country.countryCode)
        modeladmin.message_user(request, f"Fetched bird data for {country.country_name} ({country.countryCode})")

class AcousticParametersResource(resources.ModelResource):
    class Meta:
        model = AcousticParameters
        fields = ('bird_id', 'birddetail_id', 'mfcc_features', 'chroma_features',
                'spectral_bandwidth', 'spectral_contrast', 'spectral_flatness',
                'rms_energy', 'zero_crossing_rate', 'spectral_centroid', 'spectral_rolloff')

class BirdDetailResource(resources.ModelResource):
    class Meta:
        model = BirdDetail
        fields = ('birddetail_id', 'recording_url')


class BirdAdmin(admin.ModelAdmin):
    actions = [fetch_xeno_canto_recordings]

class HotspotAdmin(admin.ModelAdmin):
    actions = [fetch_birds_for_selected_hotspots]

class CountryAdmin(admin.ModelAdmin):
    list_display = ('countryCode', 'country_name')
    actions = [fetch_countries_action, fetch_hotspots_for_selected_countries, fetch_birds_for_selected_countries] 

class BirdDetailAdmin(ImportExportModelAdmin):
    list_display = ['bird_id', 'birddetail_id', 'recording_url', 'spectrogram_image']
    actions = [generate_spectrograms_action, sync_extract_acoustic_features]
    resource_class = BirdDetailResource 

    def spectrogram_image(self, obj):
        if obj.spectrogram:
            return format_html('<img src="{}" width="150" height="auto" />', obj.spectrogram.url)
        return "No Image"
    
    # フィールド名の表示をわかりやすくする
    spectrogram_image.short_description = "Spectrogram Image"


class AcousticParametersAdmin(admin.ModelAdmin):
    actions = [perform_nmds_action, perform_umap_action]


admin.site.register(Country, CountryAdmin)
admin.site.register(Hotspot, HotspotAdmin)
admin.site.register(Bird, BirdAdmin)
admin.site.register(BirdDetail, BirdDetailAdmin)
admin.site.register(AcousticParameters, AcousticParametersAdmin)
