from .__important.PluginInterface import PluginInterface
import ctypes
import shutil
import win32api
from sys import stdout, argv
from os import walk, chdir
from os.path import join, basename
from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES

class Zipdecrypt(PluginInterface):
    load = True
    types = {"source":3,"target":4,"databasename":6}
    type_types = {"source":["drag_drop", "please select source file"],"target":["drag_drop_folder", "please select destination folder"], "databasename":["text", "please enter password", None, True]}
    callname = "zipdecrypt"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self,  source, destination, password, Popups) -> bool:
        move_from = source
        move_to = destination
        if password:
            compression_key =bytes(password, 'utf-8')
        with AESZipFile(move_from) as zf:
            if password:
                zf.setpassword(compression_key)
            zf.extractall(move_to) 
