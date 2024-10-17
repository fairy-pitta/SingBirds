import requests
from ..models import Hotspot, Country
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_and_save_sg_hotspots():
    url = "https://api.ebird.org/v2/ref/hotspot/SG"

    # APIトークンを.envから取得
    api_token = os.getenv("ebirdToken")

    headers = {
        "X-eBirdApiToken": api_token
    }

    params = {
        "fmt": "json",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        hotspots = response.json()

        sg_country, created = Country.objects.get_or_create(
            countryCode="SG",
            defaults={"country_name": "Singapore"}
        )

        for hotspot_data in hotspots:
            loc_id = hotspot_data['locId']
            loc_name = hotspot_data['locName']
            subnational_code = hotspot_data.get('subnationalCode', '') 
            lat = hotspot_data.get('lat', None)
            lng = hotspot_data.get('lng', None)
            latest_obs_date = hotspot_data.get('latestObsDate', None)
            num_sp_all_time = hotspot_data.get('numSpeciesAllTime', 0)

            if not Hotspot.objects.filter(locId=loc_id).exists():
                Hotspot.objects.create(
                    locId=loc_id,
                    locName=loc_name,
                    countrycode=sg_country,
                    subnationalCode=subnational_code,
                    lat=lat,
                    lng=lng,
                    latestObsDate=latest_obs_date,
                    numSpAllTime=num_sp_all_time
                )
                print(f"Added: {loc_name}")
            else:
                print(f"Hotspot {loc_name} already exists.")
    else:
        print(f"Failed to fetch data: {response.status_code}")
