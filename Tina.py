import discord
import json
import Mysql
import websockets
import asyncio
import ConvertMods
import requests
import re
from time import gmtime, strftime
import api as osu
from discord.ext import commands
from datadog import statsd

with open("./config.json", "r") as file:
    config = json.load(file)

bot = commands.Bot(command_prefix='$')

def __init__(self, bot):
    self.bot = bot

def admin_only(orig_func):
    async def wrapper(*args, **kwargs):
        if args[0].author.server_permissions.administrator:
            await orig_func(*args, **kwargs)
        else:
            error = await bot.send_message(args[0].channel, "Sorry, you are not permitted to do that.")
            await asyncio.sleep(5)
            await bot.delete_message(error)
    return wrapper

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="with guns"))

async def Tina():
    await bot.wait_until_ready()
    while not bot.is_closed:
        async with websockets.connect('wss://getdownon.it/storas-relay') as websocket:
            while True:
                try:
                  get = await websocket.recv()
                except:
                  await bot.send_message(discord.Object(id='348621766702268416'), "Websockets died... bot is turning off should be back shortly...")
                  await bot.logout()
                  await bot.close()
                statsd.increment('Tina.new_score')
                api = json.loads(get)
                Connection, Cursor = Mysql.connect()
                meme = Mysql.execute(Connection, Cursor, "SELECT * FROM tracking WHERE user_id = %s", [api["user_id"]])
                #then you basically loop the results, check if
                #modes & 2**score["mode"]
                #score["new_score"]["performance"] >= minpp
                #score["personal_top"] <= topplays or topplays == 0
                embed = None
                for x in meme:
                    if x["modes"] & 2**api["mode"] \
                       and api["new_score"]["performance"] >= x["minpp"] \
                       and (api["personal_top"] <= x["topplays"] or x["topplays"] == 0):
                        if not embed:
                            embed = make_message(api)
                        await bot.send_message(discord.Object(id=x["channel_id"]), embed=embed)
def make_message(api):
    osu_api = osu.bid(api["beatmap_id"])

    if osu_api == None:
        print("Blame peppy got api error...")
        return

    formatter = {
        "performance_new": "{}".format(api["new_player"]["performance"]),
        "personal_top": api["personal_top"],
        "mode": ConvertMods.convertMode(api["mode"]),
        "global_rank": api["new_player"]["rank"],
        "country": api["country"],
        "country_rank": api["new_player"]["country_rank"],
        "performance": "{:.2f}".format(api["new_score"]["performance"]),
        "combo": api["new_score"]["max_combo"],
        "max_combo": osu_api[0]["max_combo"],
        "rank": api["new_score"]["rank"],
        "stars": "{:.2f}".format(float(osu_api[0]["difficultyrating"])),
        "score": "{:,d}".format(api["new_score"]["score"]),
        "accuracy": "{:.2f}".format(api["new_score"]["accuracy"]),
        "mods": ConvertMods.ModsRev(api["new_score"]["mods"]),
        "artist": osu_api[0]["artist"],
        "title": osu_api[0]["title"],
        "version": osu_api[0]["version"],
        "sid": osu_api[0]["beatmapset_id"],
        "userid": api["user_id"],
        "username": api["username"],
        "bid": api["beatmap_id"],
        "length": strftime("%M:%S", gmtime(int(osu_api[0]["total_length"]))),
        "bpm": osu_api[0]["bpm"]
    } # in bpm, length, stars: consider accounting for DT and HT

    if api["old_player"]:
        gain = api["new_player"]["performance"] - api["old_player"]["performance"]
        grankgain = api["new_player"]["rank"] - api["old_player"]["rank"]
        crankgain = api["new_player"]["country_rank"] - api["old_player"]["country_rank"]

        formatter["ppgain"] = "%+d"%gain
        formatter["grankgain"] = "%+d"%grankgain
        formatter["crankgain"] = "%+d"%crankgain
    else:
        formatter["ppgain"] = "+0"
        formatter["grankgain"] = "+0"
        formatter["crankgain"] = "+0"

    if api["new_score"]["performance"]:
        new_score = "__New score! **{performance}pp** • #{personal_top} personal best__\n"
    else:
        new_score = "__New score! **User has a better score on this map"
        if api["old_score"] and api["old_score"]["score"] > formatter["score"]:
            old_stuff = {
                "old_combo": api["old_score"]["max_combo"],
                "old_rank": api["old_score"]["rank"],
                "old_score": "{:,d}".format(api["old_score"]["score"]),
                "old_accuracy": "{:.2f}".format(api["old_score"]["accuracy"]),
                "old_mods": ConvertMods.ModsRev(api["old_score"]["mods"]),
                "max_combo": osu_api[0]["max_combo"]
            }
            new_score += ":**__\n**▸ Combo {old_combo} / {max_combo} • Rank {old_rank} • Score {old_score} • Accuracy {old_accuracy}% • Mods {old_mods}**\n".format(**old_stuff)
        else:
            new_score += "**__\n"
    new_score += "▸ Mode {mode} • Global #{global_rank} ({grankgain})• {country} #{country_rank} ({crankgain}) • PP {performance_new} ({ppgain})\n"
    new_score += "▸ Combo {combo} / {max_combo} • Rank {rank} • Score {score} • Accuracy {accuracy}% • Mods {mods}\n"
    new_score += "[{artist} - {title} [{version}]](https://osu.ppy.sh/b/{bid})\n▸ {length} • {bpm}BPM • **{stars}★**\n"

    new_score = new_score.format(**formatter)

    if formatter["personal_top"] == 1:
      e = discord.Embed(title="",
                        url="https://ripple.moe/u/{}".format(
                            api["user_id"]),
                        colour=0xf1c40f,
                        description="{}".format(new_score))
    elif formatter["personal_top"] == 2:
      e = discord.Embed(title="",
                        url="https://ripple.moe/u/{}".format(
                            api["user_id"]),
                        colour=0xcccccc,
                        description="{}".format(new_score))
    elif formatter["personal_top"] == 3:
      e = discord.Embed(title="",
                        url="https://ripple.moe/u/{}".format(
                            api["user_id"]),
                        colour=0xcd7f32,
                        description="{}".format(new_score))
    else:
      e = discord.Embed(title="",
                        url="https://ripple.moe/u/{}".format(
                            api["user_id"]),
                        colour=0x4F545C,
                        description="{}".format(new_score))

    e.set_thumbnail(
      url="https://b.ppy.sh/thumb/{sid}.jpg".format(**formatter))

    e.set_author(name='{username}'.format(**formatter),
               icon_url="https://a.ripple.moe/{userid}".format(**formatter))

    e.set_footer(text="{}".format(strftime("%d.%m.%Y at %H:%M", gmtime())))

    return e

@bot.event
async def on_message(message):
    if re.match(r'\$track (?:(?:\/m \w+|\/p \d+|\/pp \d+|\/c <#\d+>|\/u [A-Za-z0-9\[\]_\-]+) ?)+', message.content):
        await handle_track(message)
    else:
        await bot.process_commands(message)

def get_modes_list(modes):
    return [name for index, name in enumerate(["osu", "taiko", "ctb", "mania"]) if 2**index & modes]

@admin_only
async def handle_track(message):
    Connection, Cursor = Mysql.connect()
    server_id = message.channel.server.id
    r = re.findall(r'(?:\/m (\w+)|\/p (\d+)|\/pp (\d+)|\/c <#(\d+)>|\/u ([A-Za-z0-9\[\]_\-]+))', message.content)
    modes = []
    topplays = 0
    minpp = 0
    channel = None
    user = None

    for x in r:
        if x[0] and x[0] not in modes:
            modes.append(x[0])
        if x[1]:
            topplays = x[1]
        if x[2]:
            minpp = x[2]
        if x[3]:
            channel = x[3]
        if x[4]:
            user = x[4]

    if not (user and channel and modes):
        bot.say("You need at least /u /c and /m parameters.")

    try:
        u = requests.get("http://ripple.moe/api/get_user", params={"u": user}).json()
    except:
        print("Error")

    userid = u[0]["user_id"]

    modebit = 0
    modelist = ["osu", "taiko", "ctb", "mania"]
    for x in modes:
        if x in modelist:
            modebit += 2 ** modelist.index(x)
    if modebit == 0:
        await bot.say("Can't track user with no mods.")
    else:
        await bot.send_message(discord.Object(id=channel), "Starting to track {} for {}.".format(user, ",".join(get_modes_list(modebit))))
        Mysql.execute(Connection, Cursor,
                        "INSERT INTO tracking (user_id, server_id, channel_id, minpp, topplays, modes) VALUES (%s, %s, %s, %s, %s, %s)",
                        [userid, server_id, channel, minpp, topplays, modebit])

if __name__ == "__main__":
    try:
        bot.loop.create_task(Tina())
    except:
        print("Got error trying to reconnect...")
        bot.loop.create_task(Tina())
    bot.run(config["token"])
