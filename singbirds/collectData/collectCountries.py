import requests
import os
from ..models import Country
from dotenv import load_dotenv


load_dotenv()


def fetch_and_save_countries():
    url = "https://api.ebird.org/v2/ref/region/list"
    api_token = os.getenv("ebirdToken")

    headers = {
        "X-eBirdApiToken": api_token
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        countries = response.json()

        for country_data in countries:
            country_code = country_data['code']
            country_name = country_data['name']

            if not Country.objects.filter(countryCode=country_code).exists():
                Country.objects.create(
                    countryCode=country_code,
                    country_name=country_name
                )
                print(f"Added: {country_name}")
            else:
                print(f"Country {country_name} already exists.")
    else:
        print(f"Failed to fetch data: {response.status_code}")