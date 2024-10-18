import requests
from ..models import Hotspot, Country
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_and_save_hotspots_by_country(country_code):
    url = f"https://api.ebird.org/v2/ref/hotspot/{country_code}"

    # APIトークンを.envから取得
    api_token = os.getenv("ebirdToken")

    headers = {
        "X-eBirdApiToken": api_token
    }

    print(api_token)

    params = {
        "fmt": "json",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        hotspots = response.json()

        # Country テーブルから国情報を取得または作成
        country, created = Country.objects.get_or_create(
            countryCode=country_code,
            defaults={"country_name": country_code}  # 必要であれば別途カスタムで国名を設定可能
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
                    countrycode=country,
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
        print(f"Failed to fetch data for {country_code}: {response.status_code}")