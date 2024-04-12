import random

def read_choices(choices_list):
    return random.choice(choices_list)

def swnamegen(pickswname):
    pickname = str(pickswname)

    #Makes the variables the picks a random word from the lists
    randranks = read_choices(ranks)
    randplaces = read_choices(places)
    randnames = read_choices(names)

    #Creates the name based on your picks from the input
    #1 is rank and moon, 2 is rank and name, 3 is moon and name, 4 is rank, moon, name
    if pickname == "1":
        return randranks + "-" + randplaces
    elif pickname == "2":
        return randranks +"-"+ randnames
    elif pickname == "3":
        return randplaces + "-" + randnames
    elif pickname == "4":
        return randranks + "-" + randplaces + "-" + randnames
    else:
        return "Invalid input, try again"

ranks = [
    "Initiate",
    "Youngling",
    "Padawan",
    "Knight",
    "Master",
    "Grand-Master",
    "Acolyte",
    "Crusader",
    "Sith-Warrior",
    "Sith-Sorcerer",
    "Sith-Assassin",
    "Sith-Master",
    "Lord",
    "Dark-Lord",
    "Emperor",
    "Bounty-Hunter"
]

names = [
    "Millennium-Falcon",
    "Slave-I",
    "TIE-Fighter",
    "X-wing",
    "Star-Destroyer",
    "Executor",
    "Ghost",
    "Razor-Crest",
    "Slave-II",
    "Outrider",
    "Ebon-Hawk",
    "Nebulon-B-Frigate",
    "Devastator",
    "Twilight",
    "Mon-Calamari",
    "Interceptor-IV",
    "Devastator-II",
    "Redemption",
    "Serenity",
    "Invisible-Hand",
    "Sundered-Heart",
    "Finalizer",
    "Profundity",
    "Invisible-Hand-II",
    "Defiant",
    "Liberty",
    "Rogue-Shadow",
    "Hammerhead-Corvette",
    "Scimitar",
    "Thunderclap",
    "Redemption-II",
    "Reaper",
    "Havoc-Marauder",
    "Eclipse",
    "Thunderclap-II",
    "Malevolence",
    "Carrion-Spike",
    "Perseverance",
    "Raven's-Claw",
    "Vigilance",
    "Marauder",
    "Wild-Karrde",
    "Eclipse-II",
    "Resistance-Bomber",
    "Xi-class",
    "Delta-class",
    "Fulminatrix",
    "Thunderstrike"
]

places = [
    "Tatooine",
    "Coruscant",
    "Endor",
    "Hoth",
    "Naboo",
    "Mustafar",
    "Kamino",
    "Geonosis",
    "Yavin IV",
    "Dagobah",
    "Alderaan",
    "Jakku",
    "Starkiller Base",
    "Exegol",
    "Dathomir",
    "Kashyyyk",
    "Mygeeto",
    "Utapau",
    "Polis Massa",
    "Saleucami",
    "Umbara",
    "Mandalore",
    "Mon Cala",
    "Ryloth",
    "Malachor",
    "Lothal",
    "Kessel",
    "Bespin",
    "Sullust",
    "Corellia",
    "Dantooine",
    "Zeffo",
    "Iridonia",
    "Manaan",
    "Ord Mantell",
    "Onderon",
    "Dxun",
    "Taris",
    "Taral V",
    "Balmorra",
    "Serenno",
    "Ord Biniir",
    "Vulpter",
    "Haruun Kal",
    "Mirial",
    "Anaxes",
    "Raxus",
    "Rhen Var",
    "Toola",
    "Saleucami Minor",
    "Illum",
    "Cato Neimoidia",
    "Rishi",
    "Iego",
    "Felucia",
    "Utapau",
    "Socorro",
    "Pasaana",
    "Abafar",
    "Parnassos",
    "Atollon",
    "Shili",
    "Scarif"
]