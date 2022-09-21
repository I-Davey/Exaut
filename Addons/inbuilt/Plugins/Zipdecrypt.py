from .__important.PluginInterface import PluginInterface
from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES
from os.path import exists as path_exists
from os import makedirs
class Zipdecrypt(PluginInterface):
    load = True
    types = {"source":3,"target":4,"databasename":6}
    type_types = {"source":["drag_drop", "please select source file"],"target":["drag_drop_folder", "please select destination folder"], "databasename":["text", "please enter password", None, True], "__Name":"Zip Decrypt"}
    callname = "zipdecrypt"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self,  source, destination, password, ) -> bool:
        source = source.replace("\\", "/")
        destination = destination.replace("\\", "/")
        move_from = source
        move_to = destination
        if not path_exists(move_to):
            self.logger.warning(f"destination folder: {move_to} does not exist")
            x = self.Popups.yesno(f"destination folder: {move_to} does not exist, create it?")
            if x == True:
                makedirs(move_to)
        if password:
            compression_key =bytes(password, 'utf-8')
        try:
            with AESZipFile(move_from) as zf:
                if password:
                    zf.setpassword(compression_key)
                zf.extractall(move_to) 
                self.logger.success(f"file: {move_from} decrypted successfully, loc: {move_to}")
        except Exception as e:
            self.logger.error("Error extracting file from: " + move_from + " to " + move_to)
            self.logger.error(e)
            self.Popups.alert("Error extracting file, please make sure it is closed.", "Error")
            return False