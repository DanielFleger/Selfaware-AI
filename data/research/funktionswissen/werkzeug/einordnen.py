import csv, re, collections, json, sys
SRC=r"C:\Users\danie\SHC-Modding\VillageStudio\lib\funktionen.csv"
rows=list(csv.reader(open(SRC,encoding="utf-8",errors="replace"),delimiter=";"))[1:]
KL={ # Klasse -> Bereich
 "AICState":"KI","AIVState":"KI","AIMessageQueue":"KI","TroopValueState":"KI",
 "UnitsState":"Einheiten","TribesState":"Truppen/Gruppen","EntityState":"Einheiten",
 "PathFindingState":"Wegfindung","DirectionAlgorithmState":"Wegfindung",
 "TileMapState":"Karte","LandscapeState":"Karte","MapPropertiesState":"Karte","WallAndPitchState":"Gebaeude",
 "BuildingsState":"Gebaeude","ResourceManager":"Wirtschaft","WildlifeState":"Umwelt",
 "GameStateStructures":"Spielablauf","GameSynchronyState":"Befehle/Takt","GameCore":"Spielablauf",
 "RNG":"Spielablauf","InGameEventUnionVersion":"Spielablauf","SkirmishLobbySetupStructure":"Spielablauf",
 "MissingResourceState":"Wirtschaft",
}
NEBEN_KL=set("SoundSystem SFXState BinkControlClass DecoderState".split())
DARST_KL=set("TextureRenderCore PencilRenderCore ViewportRenderState MinimapViewState BitMapState AlphaAndButtonSurface WindowAndDirectDraw FontSizeClass".split())
UI_KL=set("TextEditorState TextManager UserTextHandler MouseState MenuModalComposition MenuTextInputState Menu MenuHandlerState HoveredState ScrollingHandler MenuItem BottomLeftTextDisplayState ModifierKeyState MenuView WindowInformation InsertKeyState MenuModal DisplayElement".split())
def bereich(a,n,s):
    m=re.search(r"\(\s*([A-Za-z_][\w:]*)\s*\*\s*this", s); k=m.group(1) if m else None
    if k in KL: return KL[k],k
    if k in NEBEN_KL: return "Ton/Video",k
    if k in DARST_KL: return "Darstellung",k
    if k in UI_KL: return "Menue/Oberflaeche",k
    if k: return "System",k
    N=n
    if re.match(r"^(_|Unwind@|FID_conflict|x_|std::|operator|`|\?)",N) or "Lockit" in N: return "System",None
    if re.search(r"Menu|Modal|Button|Scrollbar|DisplayElement|Lobby|Tooltip|Mouse|Keyboard|Hotkey|Cursor|Constructor_|Destructor_|Text|Font|Dialog|Chat|Highscore|Ranking|Credits|Screen|Option",N): return "Menue/Oberflaeche",None
    if re.search(r"Render|Draw|Gfx|Sprite|Texture|Animation|Anim|Display|Camera|Viewport|Minimap|Palette|Bink|Video|Image",N): return "Darstellung",None
    if re.search(r"Sound|Speech|Music|Sfx|SFX|Voice|Audio",N): return "Ton/Video",None
    if re.search(r"AI|Aic|AIC|Lord.*Plan|Personality",N): return "KI",None
    if re.search(r"[Pp]ath|[Nn]avigat|Climb|Ladder|[Ww]alk|Move",N): return "Wegfindung",None
    if re.search(r"Tribe|Troop|Formation|Selection|Group|Rally",N): return "Truppen/Gruppen",None
    if re.search(r"Building|Keep|Gate|Tower|Wall|Moat|Pitch|Ditch|Farm|Workshop|Stockpile|Granary|Armory|Barracks|Market|Mill|Bakery|Brewery|Inn|Church|Hovel|Siege|Engine|Catapult|Trebuchet|Mangonel|Ballista|Place|Upgrade|Construct|Destroy|Demolish|Repair",N): return "Gebaeude",None
    if re.search(r"Unit|Arrow|Projectile|Damage|Attack|Fight|Kill|Death|Die|Archer|Spear|Pike|Knight|Assassin|Slave|Peasant|Worker|Engineer|Tunnel|Monk|Laddermen|Lord|Soldier|Fire|Burn|Heal",N): return "Einheiten",None
    if re.search(r"Tile|Map|Terrain|Landscape|Rock|Tree|Water|Height|Area|Region|Coord|XY|Grid",N): return "Karte",None
    if re.search(r"Resource|Goods|Gold|Food|Tax|Popular|Ration|Ale|Fear|Trade|Buy|Sell|Wood|Stone|Iron|Pitch|Weapon",N): return "Wirtschaft",None
    if re.search(r"Wolf|Bear|Deer|Rabbit|Camel|Lion|Animal|Bird|Wildlife|Crow|Seagull|Fish|Dog|Cow",N): return "Umwelt",None
    if re.search(r"Command|Sync|Tick|Turn|Protocol|Invoke|Queue|DPlay|Network|Multiplayer|Player",N): return "Befehle/Takt",None
    if re.search(r"Game|Mission|Skirmish|Scenario|Trigger|Event|Save|Load|Campaign|Crusade|Victory|Win|Lose|Difficulty|Setup|Init|Reset|Update|Process",N): return "Spielablauf",None
    if N.startswith("FUN_") or re.search(r"FUN_|Unk|unk",N): return "Unbenannt",None
    return "Sonstiges",None
SPIEL={"KI","Einheiten","Truppen/Gruppen","Wegfindung","Karte","Gebaeude","Wirtschaft","Umwelt","Spielablauf","Befehle/Takt"}
out=[]; c=collections.Counter(); unb=collections.Counter()
for a,n,s in rows:
    b,k=bereich(a,n,s); out.append({"adresse":a,"name":n,"signatur":s,"klasse":k,"bereich":b,"spiel":b in SPIEL})
    c[b]+=1
    if n.startswith("FUN_") or "FUN_" in n: unb[b]+=1
json.dump(out,open("phase1_einordnung.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
for b,v in c.most_common(): print(f"{b:20} {v:5}  (davon unbenannt {unb[b]})")
print("Spielrelevant:",sum(v for b,v in c.items() if b in SPIEL),"  Rest:",sum(v for b,v in c.items() if b not in SPIEL))
