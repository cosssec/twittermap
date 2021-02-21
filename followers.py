'''
This module creates map with twitter users' friends locations.
'''
import json
import requests
import folium
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from flask import Flask, render_template, request
from ipyleaflet import Map


def friends(name, token):
    '''
    Works with .json file and returns information about user's friends.
    '''
    base_url = "https://api.twitter.com/"

    headers_find = {
        'Authorization': f'Bearer {token}'
    }

    params_find = {
        'screen_name': f'@{name}',
        'count': 10
    }

    search_url = f'{base_url}1.1/friends/list.json'

    response = requests.get(
        search_url, headers=headers_find, params=params_find)

    return response.json()["users"]


def create_base(base):
    '''
    Navigates through file.
    '''
    users_lst = []
    for user in base:
        users_lst.append([user["location"], user["name"]])

    return users_lst


def add_location(base):
    '''
    Turns location of every friend into coordinates.
    '''
    try:
        geolocator = Nominatim(user_agent="mandaryna")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        for line in base:
            if line[0] == '':
                continue
            location = geolocator.geocode(line[0])
            try:
                coords = (location.latitude, location.longitude)
            except:
                continue
            line.append(coords)
        return base

    except:
        GeocoderUnavailable
        pass


def create_map(base):
    '''
    Creates map with friends' locations. .
    '''
    izum = "49.20675315972298, 37.269659540014"

    map = folium.Map(location=[izum.split(', ')[
        0], izum.split(', ')[1]], zoom_start=10)

    locs = folium.FeatureGroup(name="Friends locations")
    for line in base:
        try:
            locs.add_child(folium.Marker(
                location=[list(line[-1])[0], list(line[-1])[1]],
                popup=line[1], icon=folium.Icon()))
        except:
            ValueError
            continue
        map.add_child(locs)

    map.add_child(folium.LayerControl())
    map.save('MapFriends.html')


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/followers_map", methods=["POST"])
def followers_map():
    name = request.form.get('nickname')
    token = request.form.get('needed_token')
    if not name:
        return render_template('failure.html')
    create_map(add_location(create_base(friends(name, token))))
    return render_template('MapFriends.html')


if __name__ == '__main__':
    app.run(debug=False)
