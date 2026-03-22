from classes.mod import Mod
from collections import defaultdict
import os
import pathlib
import json

def ultimateAsiLoader(gamePath,console):

    asiLoader = defaultdict(lambda:None, {
        "Link": "https://github.com/ThirteenAG/Ultimate-ASI-Loader/releases/download/Win32-latest/wininet-Win32.zip",
        "FileName": "wininet-Win32.zip",
    })

    loader = Mod("Ultimate Asi Loader",asiLoader)

    loader.handleTool(f"{gamePath}/Game/Bin",{"wininet.dll"},console)

#WIP
def dxvk(gamePath,console):

    dxvk = defaultdict(lambda:None, {
        "Link": "https://github.com/doitsujin/dxvk/releases/download/v2.7.1/dxvk-2.7.1.tar.gz",
        "FileName": "dxvk-2.7.1.tar.gz",
    })

    loader = Mod("Ultimate Asi Loader",asiLoader)

    loader.handleTool(f"{gamePath}/Game/Bin",{"d3d9.dll"},console)

def Sims3SettingsSetter(gamePath,console):
    
    s3ss = defaultdict(lambda:None, {
        "Link": "https://github.com/sims3fiend/Sims3SettingsSetter/releases/download/1.4.1/Sims3SettingsSetter.asi",
        "FileName": "Sims3SettingsSetter.asi",
    })

    settingSetter = Mod("Sims 3 Settings Setter",s3ss)

    settingSetter.handleTool(f"{gamePath}/Game/Bin/",{},console)

def monoPatcher(gamePath,userPath,console):
    mp = defaultdict(lambda:None,{
        "Link": "https://github.com/LazyDuchess/MonoPatcher/releases/download/0.3.0/MonoPatcher.zip",
        "FileName": "MonoPatcher.zip",
        })

    monopatcher = Mod("MonoPatcher", mp)

    monopatcher.handleTool(f"{userPath}/Mods/",{"ld_MonoPatcher.package"},console)

    monopatcher.handleTool(f"{gamePath}/Game/",{"MonoPatcher.asi"},console)
    

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
    progress.emit(int((stepsDone/totalSteps)*100))
    return stepsDone

def pipeLine(modsJson,gameVersion,ownedPacks,stepsToDo,modsToDownload,userPath,gamePath,originalVRAM,progress,update):
    vRAM = int(stepsToDo["MoreGPU"])

    stepCount = stepsToDo["UltimateAsiLoader"]+ stepsToDo["Sims3SettingsSetter"] + stepsToDo["MonoPatcher"] + stepsToDo["IntelFix"] + (stepsToDo["MoreCPU"] or int(originalVRAM) != vRAM) + stepsToDo["FlushDCBackup"] + stepsToDo["Stopping Store Generated Jpgs"] + (len(modsToDownload))
    stepsDone = 0

    isEA = not gameVersion.startswith("1.67") 

    if stepsToDo["UltimateAsiLoader"]:
        ultimateAsiLoader(gamePath,update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)

    if stepsToDo["Sims3SettingsSetter"]:
        Sims3SettingsSetter(gamePath,update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)

    if stepsToDo["MonoPatcher"]:
        monoPatcher(gamePath,userPath,update)
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


    modsFlattened = {}
    for section in modsJson.values():
        for name,mod in section.items():
            modsFlattened[name] = mod

    #update.emit(modsFlattened)
    
    for modName in modsToDownload:
        Mod(modName,defaultdict(lambda:None,modsFlattened[modName]),ownedPacks).handleMod(destination=f"{userPath}/Mods/",isEA=isEA,console=update)
        stepsDone = updateProgress(progress,stepsDone,stepCount)
