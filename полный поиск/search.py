import sys
from io import BytesIO
import requests
from PIL import Image
import map_scale
import config

toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": config.GEOCODER_API_KEY,
    "geocode": toponym_to_find,
    "format": "json"
}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    sys.exit(1)

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
toponym_coordinates = toponym["Point"]["pos"]
toponym_longitude, toponym_lattitude = toponym_coordinates.split(" ")

spn_longitude, spn_latitude = map_scale.calculate_scale_params(toponym)

map_params = {
    "ll": f"{toponym_longitude},{toponym_lattitude}",
    "spn": f"{spn_longitude},{spn_latitude}",
    "pt": f"{toponym_longitude},{toponym_lattitude},pm2rdm",
    "apikey": config.STATIC_MAPS_API_KEY,
    "size": "650,450"
}

map_api_server = "https://static-maps.yandex.ru/v1"
response = requests.get(map_api_server, params=map_params)

im = BytesIO(response.content)
opened_image = Image.open(im)
opened_image.show()