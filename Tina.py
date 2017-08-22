import discord
import json
import websockets
import ConvertMods
from time import gmtime, strftime
import api as osu
from discord.ext import commands
from datadog import statsd

with open("./config.json", "r") as file:
    config = json.load(file)

bot = commands.Bot(command_prefix='!')

bot.remove_command("help")

def __init__(self, bot):
    self.bot = bot

def isOwnerChecker(message):
    if message.author.id == config["owner_id"]:
        return True
    else:
        return False

def isOwner():
    return commands.check(lambda ctx: isOwnerChecker(ctx.message))

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

                osu_api = osu.bid(api["beatmap_id"])

                if osu_api == None:
                  print("Blame peppy got api error...")
                else:
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
                      "username": api["username"]
                  }

                  new_score = "New score +{performance}pp gain • #{personal_top} personal best\n".format(
                      **formatter)
                  new_score += "Mode {mode} • Global rank #{global_rank} • {country} Country rank #{country_rank} • PP {performance_new}\n".format(
                      **formatter)
                  new_score += "Combo {combo} / {max_combo} • Rank {rank} • Score {score} • Accuracy {accuracy}% • Mods {mods}\n".format(
                      **formatter)
                  new_score += "{artist} - {title} [{version}] {stars}★\n".format(**formatter)

                  if formatter["personal_top"] == 1:
                      e = discord.Embed(title="",
                                        url="https://ripple.moe/u/{}".format(
                                            api["user_id"]),
                                        colour=discord.Colour.gold(),
                                        description="{}".format(new_score))
                  elif formatter["personal_top"] == 2:
                      e = discord.Embed(title="",
                                        url="https://ripple.moe/u/{}".format(
                                            api["user_id"]),
                                        colour=discord.Colour.light_grey(),
                                        description="{}".format(new_score))
                  elif formatter["personal_top"] == 3:
                      e = discord.Embed(title="",
                                        url="https://ripple.moe/u/{}".format(
                                            api["user_id"]),
                                        colour=discord.Colour.dark_orange(),
                                        description="{}".format(new_score))
                  else:
                      e = discord.Embed(title="",
                                        url="https://ripple.moe/u/{}".format(
                                            api["user_id"]),
                                        colour=discord.Colour.darker_grey(),
                                        description="{}".format(new_score))

                  e.set_thumbnail(
                      url="https://b.ppy.sh/thumb/{sid}.jpg".format(**formatter))

                  e.set_author(name='{username}'.format(**formatter),
                               icon_url="https://a.ripple.moe/{userid}".format(**formatter))

                  e.set_footer(text="{}".format(strftime("%d.%m.%Y at %H:%M", gmtime())))

                  if 1 <= formatter["personal_top"] <= 50:
                      await bot.send_message(discord.Object(id='348621766702268416'), embed=e)

@bot.command()
@isOwner()
async def shutdown():
    await bot.say(":wave:")
    await bot.logout()
    await bot.close()

if __name__ == "__main__":
    try:
        bot.loop.create_task(Tina())
    except:
        print("Got error trying to reconnect...")
        bot.loop.create_task(Tina())
    bot.run(config["token"])