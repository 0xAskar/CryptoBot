import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = 'AIzaSyBAg0H0lvt7rE19H-OkhIQXSPr0ld0jq2I'

 

def validate_city_state(city, state):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    complete_url = f"{base_url}address={city}%2C%20{state}&key={API_KEY}"
    response = requests.get(complete_url)
    data = response.json()
    print(complete_url)
    if data['status'] == 'OK':
        for result in data['results']:
            for component in result['address_components']:
                if 'locality' in component['types']:
                    print("oh my", component["long_name"], city, component["short_name"])
                    if component['long_name'] == city or component['short_name'] == city:
                        return True
    return False


file_path = r"/Users/askar/Downloads/LocationValidation.xlsx"
df = pd.read_excel(file_path, engine='openpyxl')
print("finishe reading excel")

valid_pairs = []

for index, row in df.iterrows():
    city_state = row['CityState']
    city, state = city_state.rsplit(",", 1)
    city = city.strip()
    state = state.strip()
    print("index", index, city, state)
    if validate_city_state(city, state):
        print("Valid pair!", city, state)
        valid_pairs.append((city, state))
print("Valid city/state pairs:")

for city, state in valid_pairs:

    print(f"{city}, {state}")