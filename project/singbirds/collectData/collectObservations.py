import requests
from django.utils import timezone
from datetime import timedelta
from ..models import Bird, Hotspot
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_recent_birds_for_hotspots():
    url_template = "https://api.ebird.org/v2/data/obs/{}/recent"
    
    api_token = os.getenv("ebirdToken")
    headers = {
        "X-eBirdApiToken": api_token
    }

    hotspots = Hotspot.objects.all()

    for hotspot in hotspots:
        url = url_template.format(hotspot.locId)
        params = {
            'back': 30 
        }

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            bird_data = response.json()

            for bird in bird_data:
                species_code = bird['speciesCode']
                com_name = bird.get('comName', 'Unknown')
                sci_name = bird.get('sciName', 'Unknown')

                bird_obj, created = Bird.objects.get_or_create(
                    speciesCode=species_code,
                    defaults={
                        'comName': com_name,
                        'sciName': sci_name,
                    }
                )

                bird_obj.hotspots.add(hotspot)
                print(f"Added {com_name} to hotspot {hotspot.locName}")
        else:
            print(f"Failed to fetch data for hotspot {hotspot.locName}: {response.status_code}")
