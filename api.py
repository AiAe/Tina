import requests
import json

with open("./config.json", "r") as file:
    config = json.load(file)

def bid(id):
    par = {
        "b": id,
        "k": config["osu_api"]
    }
    try:
        request = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=par)
        return json.loads(request.text)
    except:
        print("Not connected to bancho trying fallback.")
        return