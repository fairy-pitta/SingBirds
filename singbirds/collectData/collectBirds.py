from django.contrib import admin
from ..models import Country, Bird
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# 関数: 選択された国に基づいて鳥のデータを取得する
def fetch_and_save_birds_by_country(country_code):
    url = f"https://api.ebird.org/v2/data/obs/{country_code}/recent"
    
    api_token = os.getenv("ebirdToken")
    
    headers = {
        "X-eBirdApiToken": api_token
    }

    params = {
        "back": "30"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        species_list = response.json()
        for species in species_list:
            species_code = species['speciesCode']
            sci_name = species['sciName']
            com_name = species['comName']

            # 既に存在しない場合のみ新しい鳥を作成
            if not Bird.objects.filter(speciesCode=species_code).exists():
                Bird.objects.create(
                    speciesCode=species_code,
                    sciName=sci_name,
                    comName=com_name
                )
                print(f"Added: {com_name} ({sci_name})")
            else:
                print(f"Bird {com_name} already exists.")
    else:
        print(f"Failed to fetch data for {country_code}: {response.status_code}")
