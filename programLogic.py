from classes.mod import Mod
from collections import defaultdict
import os
import pathlib
import json

def smoothPatch(tps:int,fps:int,borderless:bool,path:str):
    #Create Mod Object for smoothPatch
    smoothPatch = defaultdict(lambda:None, {
    "Link": "https://chii.modthesims.info/getfile.php?file=2124160&v=1706733391",
    "LinkEA": "https://chii.modthesims.info/getfile.php?file=2125462&v=1706733367",
    "FileName": "SmoothPatch.zip",
    })
    sP = Mod("Smooth Patch",smoothPatch)

    #Downloading and Extracting required files
    sP.downloadAndExtractModWithFileMap({
        "ddraw.dll":f"{path}/Game/Bin",
        "TS3Patch.asi":f"{path}/Game/Bin",
        "TS3Patch.txt":f"{path}/Game/Bin"
    })

    #Changing values if needed.
    if tps != 500 or fps != 0 or borderless:
        with open(f"{path}/Game/Bin/TS3Patch.txt","r") as f:
            content = f.readlines()

        print(f"Setting TPS to {tps}")
        content[6] = f"TPS = {tps}\n"
        print(f"Setting maxFPS to {fps}")
        content[9] = f"FPSLimit = {fps}\n"
        print(f"Setting Borderless to {1 if borderless else 0}")
        content[12] = f"Borderless = {1 if borderless else 0}\n"

        with open(f"{path}/Game/Bin/TS3Patch.txt","w") as f:
            f.writelines(content)

def intelFix():
    import subprocess

    intelFix = defaultdict(lambda:None, {
        "Link": "https://chii.modthesims.info/getfile.php?file=2098866&v=1653948642",
        "FileName": "AlderLakePatch.zip",
    })

    intel = Mod("intelFix",intelFix)

    intel.downloadAndExtractMod(f"base/intelFix")

    print("Starting intelFix")
    subprocess.run("base/intelFix/AlderLakePatch.exe")

def modifyGraphicRules(path:str,textureMemory:int,changeCPU:bool):

    with open(f"{path}/Game/Bin/GraphicsRules.sgr","r") as f:
            content = f.readlines()
    #Backing up GraphicsRules
    if not pathlib.Path("Backups/GraphicsRules.sgr").exists():
        print("Backing up GraphicRules to Backups/")
        os.makedirs("Backups", exist_ok=True)
        with open("Backups/GraphicsRules.sgr","w") as f:
            f.writelines(content)
    
    print("Modifying GraphicRules values")
    for index,line in enumerate([x for x in content]):
        if changeCPU and (line.startswith("seti cpuLevelMedium") or line.startswith("seti cpuLevelLow")):
            content[index] = line[:-2] + "3\n"
        elif "seti textureMemory" in line:
            content[index] = line[:27] + f"{textureMemory}\n"


    with open(f"{path}/Game/Bin/GraphicsRules.sgr","w") as f:
        f.writelines(content)

def disableFeatureItems(path:str):
    import shutil

    p = f"{path}/FeaturedItems"
    if not pathlib.Path("Backups/FeaturedItems").exists():
        print("Backing up FeaturedItems to Backups/")
        shutil.move(p,"Backups/FeaturedItems")

    print(f"Writing empty file to {path}")
    with open(p,"w") as f:
        pass

def flushDCBackup(path:str):
    print("Flushing DCBackup")
    for file in os.listdir(f"{path}/DCBackup"):
        if file != "ccmerged.package":
            os.remove(f"{path}/DCBackup/"+file)

def pipeLine(ownedPacks,stepsToDo,modsToDownload,userPath,gamePath,originalVRAM,progress,update):
    print(stepsToDo,modsToDownload,userPath,gamePath,originalVRAM)
    maxFPS = int(stepsToDo["MaxFPS"])
    vRAM = int(stepsToDo["MoreGPU"])

    if stepsToDo["Smooth Patch"]:
        smoothPatch(1000,maxFPS,stepsToDo["Borderless"],gamePath)
    
    if stepsToDo["IntelFix"]:
        intelFix()
    
    if stepsToDo["MoreCPU"] or int(originalVRAM) != vRAM:
        modifyGraphicRules(gamePath,vRAM,stepsToDo["MoreCPU"])
    
    if stepsToDo["FlushDCBackup"]:
        flushDCBackup(userPath)

    if stepsToDo["Stopping Store Generated Jpgs"]:
        disableFeatureItems(userPath)


    with open("mods.json","r") as f:
        sectionedMods = json.load(f)
    modsFlattened = {}
    for section in sectionedMods.values():
        for name,mod in section.items():
            modsFlattened[name] = mod

    #print(modsFlattened)
    progress.emit(50)
    for modName in modsToDownload:
        Mod(modName,defaultdict(lambda:None,modsFlattened[modName]),ownedPacks).downloadAndExtractMod("Downloads/")
