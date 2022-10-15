#!/usr/bin/env python3

import json
from textwrap import indent
import requests
import os
import time


def config():
    key_word = "bia"
    language = "vi"
    lat = 21.012832699039034
    long = 105.82177484220092
    radius = 2000
    return key_word, language, lat, long, radius


def api_key():
    with open(os.path.join(os.path.dirname(__file__), "api_key.txt")) as f:
        key = f.read().strip()

    return key


def first_api_call(key_word, lat, long, radius, language, key):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}, {long}&radius={radius}&keyword={key_word}&key={key}&language={language}"
    payload = {}
    header = {}
    resp = requests.request("GET", url, headers=header, data=payload, timeout=20)
    resp = json.loads(resp.text)
    location_list = resp["results"]
    token = resp["next_page_token"]
    if "next_page_token" not in resp or len(resp["next_page_token"]) == 0:
        token = "No more result"
    else:
        token = resp["next_page_token"]

    return location_list, token


def next_api_call(token, key):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={token}&key={key}"
    payload = {}
    header = {}
    resp = requests.request("GET", url, headers=header, data=payload, timeout=20)
    resp = json.loads(resp.text)
    location_list = resp["results"]
    if "next_page_token" not in resp or len(resp["next_page_token"]) == 0:
        token = "No more result"
    else:
        token = resp["next_page_token"]

    return location_list, token


def get_address(location):
    lat = location["geometry"]["location"]["lat"]
    long = location["geometry"]["location"]["lng"]
    coord = [long, lat]
    name = location["name"]
    st_ward = location["vicinity"]

    if "plus_code" in location:
        compound_code = location["plus_code"]["compound_code"]
        remove_code = compound_code.find(" ")
        district_province = compound_code[remove_code:]
    else:
        district_province = ""

    address = f"{st_ward},{district_province}"

    return name, coord, address


def formatfeature(name, coord, address):
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": coord},
        "properties": {"address": address, "name": name}
    }
    return feature


def collectfeature(feature, features):
    features["features"].append(feature)
    return features


def writefile(data):
    file = json.dumps(data, indent=2)
    with open("pymi_beer.geojson", "w", encoding="utf-8") as f:
        f.write(file)
    return


def main():
    key_word, language, lat, long, radius = config()
    key = api_key()
    location_list, token = first_api_call(key_word, lat, long, radius, language, key)
    number_of_locations = 50
    features = {"type": "FeatureCollection", "features": []}

    while number_of_locations > len(location_list):
        if token == "No more result":
            break
        else:
            time.sleep(5)
            next_location_list, token = next_api_call(token, key)
            location_list.extend(next_location_list)

    for location in location_list[:50]:
        name, coord, address = get_address(location)
        feature = formatfeature(name, coord, address)
        collectfeature(feature, features)

    writefile(features)


if __name__ == "__main__":
    main()
