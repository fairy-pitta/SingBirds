import requests
from ..models import Bird
from dotenv import load_dotenv
import os

load_dotenv()


def fetch_and_save_birds_in_singapore():
    url = "https://api.ebird.org/v2/data/obs/SG/recent"

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
        print(f"Failed to fetch data: {response.status_code}")
