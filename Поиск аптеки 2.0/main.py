import sys
import requests
from io import BytesIO
from PIL import Image
from math import radians, cos, sin, asin, sqrt
from map_scale import get_map_params_for_two_points

def geocode(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13",
        "geocode": address,
        "format": "json"
    }
    response = requests.get(geocoder_api_server, params=geocoder_params)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    coords = toponym["Point"]["pos"]
    longitude, latitude = map(float, coords.split())
    address_name = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
    return longitude, latitude, address_name

def search_pharmacy(lon, lat):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{lon},{lat}",
        "type": "biz",
        "results": 1
    }
    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()
    
    if not json_response["features"]:
        return None
    
    org = json_response["features"][0]
    org_coords = org["geometry"]["coordinates"]
    org_lon, org_lat = org_coords[0], org_coords[1]
    org_name = org["properties"]["CompanyMetaData"].get("name", "Название отсутствует")
    org_address = org["properties"]["CompanyMetaData"].get("address", "Адрес отсутствует")
    org_hours = org["properties"]["CompanyMetaData"].get("Hours", {})
    hours_text = org_hours.get("text", "Время работы не указано") if org_hours else "Время работы не указано"
    
    return {
        "coords": (org_lon, org_lat),
        "name": org_name,
        "address": org_address,
        "hours": hours_text
    }

def haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000
    return c * r

def show_map(start_coords, pharmacy_coords):
    apikey = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    
    map_params = get_map_params_for_two_points(start_coords, pharmacy_coords)
    map_params["apikey"] = apikey
    
    points = [
        f"{start_coords[0]},{start_coords[1]},pm2rdm",
        f"{pharmacy_coords[0]},{pharmacy_coords[1]},pm2gnm"
    ]
    map_params["pt"] = "~".join(points)
    
    map_api_server = "https://static-maps.yandex.ru/v1"
    response = requests.get(map_api_server, params=map_params)
    
    im = BytesIO(response.content)
    opened_image = Image.open(im)
    opened_image.show()

def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py 'адрес'")
        sys.exit(1)
    
    address = " ".join(sys.argv[1:])
    
    print("Поиск адреса...")
    start_lon, start_lat, start_address = geocode(address)
    print(f"Найденный адрес: {start_address}")
    print(f"Координаты: {start_lon}, {start_lat}")
    
    print("\nПоиск ближайшей аптеки...")
    pharmacy = search_pharmacy(start_lon, start_lat)
    
    if not pharmacy:
        print("Аптека не найдена")
        return
    
    distance = haversine_distance(start_lon, start_lat, 
                                  pharmacy["coords"][0], pharmacy["coords"][1])
    
    print("\n" + "="*50)
    print("СНИППЕТ:")
    print("="*50)
    print(f"Исходный адрес: {start_address}")
    print(f"Аптека: {pharmacy['name']}")
    print(f"Адрес аптеки: {pharmacy['address']}")
    print(f"Время работы: {pharmacy['hours']}")
    print(f"Расстояние: {distance:.0f} метров")
    print("="*50)
    
    show_map((start_lon, start_lat), pharmacy["coords"])

if __name__ == "__main__":
    main()