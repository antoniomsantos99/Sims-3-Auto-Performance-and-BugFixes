import io
import os
import requests
import zipfile
import rarfile
import py7zr
from abc import ABC, abstractmethod
import tempfile
import shutil
import subprocess


class ArchiveHandler(ABC):
    def __init__(self, response_content, destination, filename=None):
        self.stream = response_content
        self.filename = filename
        self.destination = destination
        self.archive = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def get_file_names(self):
        pass

    def extract_all(self):
        self.archive.extractall(self.destination)

    def extract_list(self,fileList):
        for file in fileList:
            for file_in_archive in self.get_file_names():
                if file in file_in_archive:
                    self.archive.extract(file_in_archive,self.destination)
                    break

    def close(self):
        if self.archive:
            self.archive.close()


# CLass to handle plain files

class PlainHandler(ArchiveHandler):
    def open(self):
        pass

    def get_file_names(self):
        return [filename]
    
    def extract_all(self):
        os.makedirs(self.destination, exist_ok=True)
        with open(self.destination+self.filename,"wb+") as f:
            f.write(self.stream)


# Class to handle zip files

class ZipHandler(ArchiveHandler):
    def open(self):
        self.archive : ZipFile = zipfile.ZipFile(io.BytesIO(self.stream), 'r')
    
    def get_info_list(self):
        return self.archive.infolist()

    def get_file_names(self):
        return [file.filename for file in self.get_info_list()]

# Class to handle 7z files

class SevenZipHandler(ArchiveHandler):
    def open(self):
        self.archive : SevenZipFile = py7zr.SevenZipFile(io.BytesIO(self.stream), 'r')

    def get_file_names(self):
        return self.archive.getnames()

# Class to handle rar files (Why are we still using this proprietary format...)

class RarHandler(ArchiveHandler):
    def __init__(self,*args,**kwargs):
        ArchiveHandler.__init__(self, *args)
        self.tool = r'UnRAR.exe' if os.name == "nt" else r'unrar'

    def open(self):
        self._temp_dir = tempfile.mkdtemp()
        self._temp_path = os.path.join(self._temp_dir, "data.rar")
        
        with open(self._temp_path, "wb") as f:
            f.write(io.BytesIO(self.stream).getvalue())
            f.flush()
            os.fsync(f.fileno())

        self.archive = rarfile.RarFile(self._temp_path, mode='r')

    def get_file_names(self):
        return self.archive.namelist()

    def extract_all(self):
        destination = self.destination
        os.makedirs(destination, exist_ok=True)

        cmd = [f"./{self.tool}", "x", "-o+", "-y", self._temp_path, destination]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Unrar failed: {e.stderr}")


    def extract_list(self, file_list):
        destination = self.destination
        os.makedirs(destination, exist_ok=True)
        
        archive_filenames = self.get_file_names()
        
        for target_file in file_list:
            for file_in_archive in archive_filenames:
                if target_file in file_in_archive:
                    cmd = [
                        f"./{self.tool}", "x", "-o+", "-y", 
                        self._temp_path, 
                        file_in_archive, 
                        destination
                    ]
                    
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to extract {file_in_archive}: {e.stderr}")
                    
                    break 

    def close(self):
        if self.archive:
            self.archive.close()
        if hasattr(self, '_temp_dir') and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)