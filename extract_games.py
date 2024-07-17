import requests 
import folium
import json 

def generate_map(_data, i):
    _map = folium.Map(location=[0, 0], zoom_start=3)

    for loc, g_loc, country, dist in zip(_data["locs"], _data["guesses"], _data["countries"], _data["dists"]):

        lat, lon = loc 
        g_lat, g_lon = g_loc 

        folium.Marker(
            location=loc,
            tooltip=f"Exact Location, {country}",
            popup=f'lat={str(lat)}<br>lon={str(lon)}<br><a href="https://www.google.com/maps?layer=c&cbll={str(lat)},{str(lon)}" target="blank">STREET VIEW</a>',
            icon=folium.Icon(icon="cloud", color="green")
        ).add_to(_map)

        folium.Marker(
            location=g_loc,
            tooltip=f"Guessed_[{dist}]",
            popup=f'lat={str(g_lat)}<br>lon={str(g_lon)}<br><a href="https://www.google.com/maps?layer=c&cbll={str(g_lat)},{str(g_lon)}" target="blank">STREET VIEW</a>',
            icon=folium.Icon(icon="star", color="red")
        ).add_to(_map)

        folium.PolyLine([[lat, lon], [g_lat, g_lon]]).add_to(_map)

    _map.save(f"fol_{i}.html")
    return
    
def geoguessr():
    ''' Create a session object and set the _ncfa cookie '''
    session = requests.Session()
    session.cookies.set("_ncfa", NCFA_TOKEN, domain="www.geoguessr.com")

    ''' Get data from games played '''
    resp = session.get(GEOGUESSR_URL)

    if resp.status_code == 200:

        obj = json.loads(resp.text)

        for i, group in enumerate(obj["entries"]):

            _data = {
                "locs": [],
                "guesses": [],
                "countries": [],
                "dists": [],
            }

            group_obj = json.loads(group["payload"])

            if isinstance(group_obj, list):
                continue

            if group_obj.get("gameMode", None)==None:
                continue

            ''' Deal with data having the necessary info '''
            if group_obj["gameMode"]=="Standard":

                try:
                    token = group_obj["gameToken"]
                except:
                    continue

                game_resp = session.get(f"{GEOGUESSR_GAME_URL}/{token}")

                game_obj = json.loads(game_resp.text)

                ''' Store the exact location, guessed location, distance, and country code '''
                for _round in game_obj["rounds"]:
                    _data["locs"].append([_round["lat"],_round["lng"]])
                    _data["countries"].append([_round["streakLocationCode"]])

                for guess in game_obj["player"]["guesses"]:
                    _data["guesses"].append([guess["lat"], guess["lng"]])
                    _data["dists"].append(round(guess["distanceInMeters"]/1000, 3))

                ''' Generate an interactive map having the game info visualized '''
                generate_map(_data, i)
    else:
        print(f"Error: {resp.status_code}")
    return

def main():
    geoguessr()
    return

if __name__=="__main__":
    #GEONAMES_URL = "https://api.3geonames.org/?randomland=yes"

    GEOGUESSR_URL = f"https://www.geoguessr.com/api/v4/feed/private"  # Base URL for all endpoints
    GEOGUESSR_GAME_URL = f"https://www.geoguessr.com/api/v3/games"  # Base URL for all endpoints
    #GEOGUESSR_CHALLENGE_URL = f"https://www.geoguessr.com/api/v3/challenges"  # Base URL for all endpoints

    NCFA_TOKEN = ""

    main()
