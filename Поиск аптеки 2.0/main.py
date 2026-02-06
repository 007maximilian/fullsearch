import sys
from io import BytesIO
import requests
from PIL import Image
import math
import scale_calculator
import config

def geocode(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": config.GEOCODER_API_KEY,
        "geocode": address,
        "format": "json"
    }
    
    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        return None
    
    json_response = response.json()
    try:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coordinates = toponym["Point"]["pos"]
        longitude, latitude = map(float, toponym_coordinates.split())
        address_name = toponym["name"]
        return (longitude, latitude), address_name
    except:
        return None

def search_pharmacy(lon, lat):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    search_params = {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{lon},{lat}",
        "type": "biz",
        "results": "1"
    }
    
    response = requests.get(search_api_server, params=search_params)
    if not response:
        return None
    
    json_response = response.json()
    try:
        organization = json_response["features"][0]
        org_lon, org_lat = organization["geometry"]["coordinates"]
        properties = organization["properties"]
        name = properties.get("name", "Аптека")
        address = properties.get("description", "")
        hours = properties.get("CompanyMetaData", {}).get("Hours", {}).get("text", "Время работы неизвестно")
        return (org_lon, org_lat), name, address, hours
    except:
        return None

def calculate_distance(point1, point2):
    lon1, lat1 = point1
    lon2, lat2 = point2
    
    degree_to_meters = 111000
    dx = (lon2 - lon1) * degree_to_meters * math.cos(math.radians((lat1 + lat2) / 2))
    dy = (lat2 - lat1) * degree_to_meters
    
    distance = math.sqrt(dx * dx + dy * dy)
    return round(distance, 1)

def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py <адрес>")
        sys.exit(1)
    
    address = " ".join(sys.argv[1:])
    
    print(f"Поиск адреса: {address}")
    address_result = geocode(address)
    
    if not address_result:
        print("Не удалось найти указанный адрес")
        sys.exit(1)
    
    address_coords, address_name = address_result
    address_lon, address_lat = address_coords
    
    print(f"Найден адрес: {address_name}")
    print(f"Координаты: {address_lon}, {address_lat}")
    print("\nПоиск ближайшей аптеки...")
    
    pharmacy_result = search_pharmacy(address_lon, address_lat)
    
    if not pharmacy_result:
        print("Не удалось найти аптеки поблизости")
        sys.exit(1)
    
    pharmacy_coords, pharmacy_name, pharmacy_address, pharmacy_hours = pharmacy_result
    pharmacy_lon, pharmacy_lat = pharmacy_coords
    
    distance = calculate_distance(address_coords, pharmacy_coords)
    
    print("\n" + "="*50)
    print("НАЙДЕННАЯ АПТЕКА:")
    print("="*50)
    print(f"Название: {pharmacy_name}")
    print(f"Адрес: {pharmacy_address}")
    print(f"Режим работы: {pharmacy_hours}")
    print(f"Расстояние от '{address_name}': {distance} метров")
    print("="*50)
    
    center_lon_str, center_lat_str = scale_calculator.calculate_center_for_two_points(
        address_coords, pharmacy_coords
    )
    
    spn_lon_str, spn_lat_str = scale_calculator.calculate_spn_for_two_points(
        address_coords, pharmacy_coords
    )
    
    map_params = {
        "ll": f"{center_lon_str},{center_lat_str}",
        "spn": f"{spn_lon_str},{spn_lat_str}",
        "pt": f"{address_lon},{address_lat},pm2rdm~{pharmacy_lon},{pharmacy_lat},pm2gnm",
        "apikey": config.STATIC_MAPS_API_KEY,
        "size": "650,450"
    }
    
    map_api_server = "https://static-maps.yandex.ru/v1"
    response = requests.get(map_api_server, params=map_params)
    
    if response.status_code == 200:
        im = BytesIO(response.content)
        opened_image = Image.open(im)
        opened_image.show()
    else:
        print(f"Ошибка при получении карты: {response.status_code}")

if __name__ == "__main__":
    main()