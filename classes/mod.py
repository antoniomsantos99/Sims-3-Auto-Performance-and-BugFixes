import requests

import io
from collections import defaultdict
from classes.archiveHandler import PlainHandler, ZipHandler, RarHandler, SevenZipHandler, ArchiveHandler, TarHandler

import os

headers = {'User-Agent': 'Mozilla/5.0'}

class Mod:
    def __init__(self,name,dic,ownedPacks=set()):
        self.name : str = name
        self.link : str = dic["Link"]
        self.fileName : str = dic["FileName"]
        self.linkEA : str = dic["LinkEA"]
        self.toOverride : bool = dic["toOverride"]
        self.filesPerEP = dic["filesPerEP"]
        self.ownedPacks : set = ownedPacks
        self.download = None

    def __repr__(self):
        return repr(f'''Name: {self.name} | Filename: {self.fileName} | Link: {self.link} | LinkEA: {self.linkEA} | toOverride: {self.toOverride} | filesPerEP: {self.filesPerEP}''')

    def createArchiveHandler(self,response, destination):
        match self.fileName.split(".")[-1]:
            case "zip":
                print(self.fileName.split(".")[-1])
                return ZipHandler(response.content,destination,self.fileName)
            case "rar":
                return RarHandler(response.content,destination,self.fileName)
            case "7z":
                return SevenZipHandler(response.content,destination,self.fileName)
            case "gz":
                return TarHandler(response.content,destination,self.fileName)
            case _:
                return PlainHandler(response.content,destination,self.fileName)

    def handleMod(self,destination,isEA,console,tries=1):
        if tries > 5:
            return -1

        try:
            # To prevent redownloading the same mod multiple times lets save it in the object
            if(self.download is None):
                link = self.linkEA if isEA else self.link

                console.emit(f"Start downloading {self.fileName} from {link}")
                req = requests.get(self.link,headers)

                if req.status_code != 200:
                    return -1

                self.download = req
                
            folder = "Overrides/" if self.toOverride else "Packages/" + "Sims-3-Auto-Performance-and-BugFixes/" + self.name + "/"
            with self.createArchiveHandler(self.download,destination+folder) as mod:
                if self.filesPerEP:
                    files = {self.filesPerEP[ownedPack] for ownedPack in self.ownedPacks if ownedPack in self.filesPerEP}
                    mod.extract_list(files)
                else:
                    mod.extract_all()
        except Exception as e:
            print(e)
            console.emit(f"Download failed (try {tries} : 5)")
            self.handleMod(destination,isEA,console,tries+1)
