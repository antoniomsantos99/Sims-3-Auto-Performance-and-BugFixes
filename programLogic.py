from classes.mod import Mod
from collections import defaultdict
import os
import pathlib
import json

def smoothPatch(tps:int,fps:int,borderless:bool,path:str,update):
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
    },update)

    #Changing values if needed.
    if tps != 500 or fps != 0 or borderless:
        with open(f"{path}/Game/Bin/TS3Patch.txt","r") as f:
            content = f.readlines()

        update.emit(f"Setting TPS to {tps}")
        content[6] = f"TPS = {tps}\n"
        update.emit(f"Setting maxFPS to {fps}")
        content[9] = f"FPSLimit = {fps}\n"
        update.emit(f"Setting Borderless to {1 if borderless else 0}")
        content[12] = f"Borderless = {1 if borderless else 0}\n"

        with open(f"{path}/Game/Bin/TS3Patch.txt","w") as f:
            f.writelines(content)

def intelFix(update):
    import subprocess

    intelFix = defaultdict(lambda:None, {
        "Link": "https://chii.modthesims.info/getfile.php?file=2098866&v=1653948642",
        "FileName": "AlderLakePatch.zip",
    })

    intel = Mod("intelFix",intelFix)

    intel.downloadAndExtractMod(f"base/intelFix")

    update.emit("Starting intelFix")
    subprocess.run("base/intelFix/AlderLakePatch.exe")

def modifyGraphicRules(path:str,textureMemory:int,changeCPU:bool,update):

    with open(f"{path}/Game/Bin/GraphicsRules.sgr","r") as f:
            content = f.readlines()
    #Backing up GraphicsRules
    if not pathlib.Path("Backups/GraphicsRules.sgr").exists():
        update.emit("Backing up GraphicRules to Backups/")
        os.makedirs("Backups", exist_ok=True)
        with open("Backups/GraphicsRules.sgr","w") as f:
            f.writelines(content)
    
    update.emit("Modifying GraphicRules values")
    for index,line in enumerate([x for x in content]):
        if changeCPU and (line.startswith("seti cpuLevelMedium") or line.startswith("seti cpuLevelLow")):
            content[index] = line[:-2] + "3\n"
        elif "seti textureMemory" in line:
            content[index] = line[:27] + f"{textureMemory}\n"


    with open(f"{path}/Game/Bin/GraphicsRules.sgr","w") as f:
        f.writelines(content)

def disableFeatureItems(path:str,update):
    import shutil

    p = f"{path}/FeaturedItems"
    if not pathlib.Path("Backups/FeaturedItems").exists():
        update.emit("Backing up FeaturedItems to Backups/")
        shutil.move(p,"Backups/FeaturedItems")

    update.emit(f"Writing empty file to {path}")
    with open(p,"w") as f:
        pass

def flushDCBackup(path:str,update):
    update.emit("Flushing DCBackup")
    for file in os.listdir(f"{path}/DCBackup"):
        if file != "ccmerged.package":
            os.remove(f"{path}/DCBackup/"+file)

def updateProgress(progress,stepsDone,totalSteps):
    stepsDone+=1
    print(stepsDone)
    progress.emit(int((stepsDone/totalSteps)*100))
    return stepsDone

def pipeLine(ownedPacks,stepsToDo,modsToDownload,userPath,gamePath,originalVRAM,progress,update):
    maxFPS = int(stepsToDo["MaxFPS"])
    vRAM = int(stepsToDo["MoreGPU"])

    stepCount = stepsToDo["Smooth Patch"] + stepsToDo["IntelFix"] + (stepsToDo["MoreCPU"] or int(originalVRAM) != vRAM) + stepsToDo["FlushDCBackup"] + stepsToDo["Stopping Store Generated Jpgs"] + (len(modsToDownload))
    stepsDone = 0

    print(stepCount)

    if stepsToDo["Smooth Patch"]:
        smoothPatch(1000,maxFPS,stepsToDo["Borderless"],gamePath,update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)

    
    if stepsToDo["IntelFix"]:
        intelFix(update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)
    
    if stepsToDo["MoreCPU"] or int(originalVRAM) != vRAM:
        modifyGraphicRules(gamePath,vRAM,stepsToDo["MoreCPU"],update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)
    
    if stepsToDo["FlushDCBackup"]:
        flushDCBackup(userPath,update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)

    if stepsToDo["Stopping Store Generated Jpgs"]:
        disableFeatureItems(userPath,update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)


    with open("mods.json","r") as f:
        sectionedMods = json.load(f)
    modsFlattened = {}
    for section in sectionedMods.values():
        for name,mod in section.items():
            modsFlattened[name] = mod

    #update.emit(modsFlattened)
    
    for modName in modsToDownload:
        Mod(modName,defaultdict(lambda:None,modsFlattened[modName]),ownedPacks).downloadAndExtractMod("Downloads/",update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)
