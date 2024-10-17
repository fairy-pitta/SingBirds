from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Country, Hotspot, Bird, BirdDetail
from .collectData.collectCountries import fetch_and_save_countries
from .collectData.collectHotspots import fetch_and_save_sg_hotspots
from .collectData.collectBirds import fetch_and_save_birds_in_singapore
from .collectData.collectObservations import fetch_recent_birds_for_hotspots
from .collectData.collectRecordings import fetch_xeno_canto_recordings
from .collectData.createSpectrogram import generate_spectrograms_action

@admin.action(description='Fetch and save countries from eBird API')
def fetch_countries_action(modeladmin, request, queryset):
    try:
        fetch_and_save_countries()
        messages.success(request, "Countries fetched and saved successfully.")
    except Exception as e:
        messages.error(request, f"Error fetching countries: {e}")

@admin.action(description="fetch the hotspots")
def fetch_hotspots_action(modelsadmin, request, quesryset):
    try:
        fetch_and_save_sg_hotspots()
        messages.success(request, "Hostpots fetched successfully")
    except Exception as e:
        messages.error(request, f"Error fetching hotspots: {e}")

@admin.action(description="fetch birds")
def fetch_birds_action(modelsadmin, request, quesryset):
    try:
        fetch_and_save_birds_in_singapore()
        messages.success(request, "Birds fetched successfully")
    except Exception as e:
        messages.error(request, f"Error fetching birds: {e}")

@admin.action(description="fetch birds observations")
def fetch_obs_action(modelsadmin, request, quesryset):
    try:
        fetch_recent_birds_for_hotspots()
        messages.success(request, "Obs fetched successfully")
    except Exception as e:
        messages.error(request, f"Error fetching obs: {e}")

@admin.action(description="Fetch bird recordings from Xeno-Canto")
def fetch_xeno_canto_action(modeladmin, request, queryset):
    try:
        # 鳥の音声をXeno-Cantoから取得する関数を実行
        fetch_xeno_canto_recordings()
        messages.success(request, "Bird recordings fetched successfully from Xeno-Canto")
    except Exception as e:
        messages.error(request, f"Error fetching bird recordings: {e}")


class BirdAdmin(admin.ModelAdmin):
    actions = [fetch_birds_action, fetch_obs_action, fetch_xeno_canto_action]

class HotspotAdmin(admin.ModelAdmin):
    actions = [fetch_hotspots_action]

class CountryAdmin(admin.ModelAdmin):
    list_display = ('countryCode', 'country_name')
    actions = [fetch_countries_action] 

class BirdDetailAdmin(admin.ModelAdmin):
    list_display = ['bird_id', 'recording_url', 'spectrogram_image']
    actions = [generate_spectrograms_action]

    def spectrogram_image(self, obj):
        if obj.spectrogram:
            return format_html('<img src="{}" width="150" height="auto" />', obj.spectrogram.url)
        return "No Image"
    
    # フィールド名の表示をわかりやすくする
    spectrogram_image.short_description = "Spectrogram Image"


admin.site.register(Country, CountryAdmin)
admin.site.register(Hotspot, HotspotAdmin)
admin.site.register(Bird, BirdAdmin)
admin.site.register(BirdDetail, BirdDetailAdmin)

