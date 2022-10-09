#!/usr/bin/env python3

import json
import requests
import os
import time


def config(key_word="bia", language="vi"):
    lat, long = 21.012832699039034, 105.82177484220092
    radius = 2000
    ses = requests.Session()
    timeout_time = 15
    return key_word, lat, long, radius, ses, timeout_time, language


def api_key():
    with open(os.path.join(os.path.dirname(__file__), "api_key.txt")) as f:
        key = f.read().strip()

    print(key)
    return key


def first_api_call(key_word, lat, long, radius, ses, timeout_time, language):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={key_word}&location={lat}, {long}&radius={radius}&key={key_word}&language={language}"
    payload = {}
    header = {}
    resp = ses.request("GET", url, headers=header, data=payload, timeout=timeout_time)
    resp = json.loads(resp.text)
    location_list = resp["results"]

    if "next_page_token" not in resp or len(resp["next_page_token"]) == 0:
        next_page_token = "No more result"
    else:
        next_page_token = resp["next_page_token"]

    return location_list, next_page_token


def next_api_call(ses, timeout_time, next_token, key_word):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_token}&key={key_word}"
    payload = {}
    header = {}
    resp = ses.request("GET", url, headers=header, data=payload, timeout=timeout_time)
    resp = json.loads(resp.text)
    location_list = resp["results"]

    if "next_page_token" not in resp or len(resp["next_page_token"]) == 0:
        next_page_token = "No more result"
    else:
        next_page_token = resp["next_page_token"]

    return location_list, next_page_token


def get_address(location):
    lat = location["geometry"]["location"]["lat"]
    long = location["geometry"]["location"]["lng"]
    coord = [lat, long]
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


def formatfeature(coordinates, name, address):
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": coordinates},
        "properties": {"address": address, "name": name},
    }
    return feature


def collectfeature(feature, features):
    features["features"].append(feature)
    return features


def writefile(data):
    with open("pymi_beer.geojson", "w", encoding="utf-8") as f:
        f.write(str(data))
    return


def main():
    ses, timeout_time, lat, long, radius, keyword, language = config()
    key = api_key()
    location_list, next_page_token = first_api_call(
        ses,
        timeout_time,
        lat,
        long,
        radius,
        keyword,
        language,
    )

    number_of_locations = 50

    features = {"type": "FeatureCollection", "features": []}

    while number_of_locations > len(location_list):
        if next_page_token == "No more result":
            break
        else:
            time.sleep(2)
            next_location_list, next_page_token = next_api_call(
                ses, timeout_time, next_page_token, key
            )
            location_list.extend(next_location_list)

    for location in location_list[:50]:
        coordinates, name, address = get_address(location)
        feature = formatfeature(coordinates, name, address)
        collectfeature(feature, features)

    writefile(features)


if __name__ == "__main__":
    main()
