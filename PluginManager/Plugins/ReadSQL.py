from .__important.PluginInterface import PluginInterface
import os
import ctypes
import shutil
import win32api
class Run_Executable(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    callname = "example"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, folderpath,filename,type_,source,target,databasepath,databasename,keypath,keyfile,runsequence,treepath,buttonname) -> bool:
       self.logger.success(f"folderpath: {folderpath}, filename: {filename}, type: {type_}, source: {source}, target: {target}, databasepath: {databasepath}, databasename: {databasename}, keypath: {keypath}, keyfile: {keyfile}, runsequence: {runsequence}, treepath: {treepath}, buttonname: {buttonname}")