import mods

def Mods(modsList):
    modsEnum = 0
    for i in modsList:
        if i == "NO":
            modsEnum = 0
            break
        elif i == "NF":
            modsEnum += 1
        elif i == "EZ":
            modsEnum += 2
        elif i == "HD":
            modsEnum += 8
        elif i == "HR":
            modsEnum += 16
        elif i == "DT":
            modsEnum += 64
        elif i == "HT":
            modsEnum += 256
        elif i == "NC":
            modsEnum += 512
        elif i == "FL":
            modsEnum += 1024
        else:
            modsEnum = 0
    return modsEnum

def ModsRev(__mods):
    r = ""
    if __mods == 0:
        return "None"
    if __mods & mods.NOFAIL > 0:
        r += "NF"
    if __mods & mods.EASY > 0:
        r += "EZ"
    if __mods & mods.HIDDEN > 0:
        r += "HD"
    if __mods & mods.HARDROCK > 0:
        r += "HR"
    if __mods & mods.DOUBLETIME > 0:
        r += "DT"
    if __mods & mods.HALFTIME > 0:
        r += "HT"
    if __mods & mods.FLASHLIGHT > 0:
        r += "FL"
    if __mods & mods.SPUNOUT > 0:
        r += "SO"
    return (r)

def convertMode(mode):
    if mode == 0:
        return "osu!"
    elif mode == 1:
        return "Taiko"
    elif mode == 2:
        return "CtB"
    else:
        return "Mania"
