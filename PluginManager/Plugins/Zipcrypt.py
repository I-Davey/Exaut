from .__important.PluginInterface import PluginInterface
from os import walk, chdir, getcwd
from os.path import join, basename
import tempfile
from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES
import shutil
import ctypes
class Zipcrypt(PluginInterface):
    load = True
    types = {"source":3,"target":4,"databasename":6}
    type_types = {"source":["drag_drop_folder", "please select source folder"],"target":["drag_drop_folder", "please select destination folder"], "databasename":["text", "please enter password"]}
    callname = "zipcrypt"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True





    def main(self,source, destination, password, Popups) -> bool:
        curdir = getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            move_from_fullpath = source.split("/")[:-1]
            #combine move_from_fullpath into string seperated by "\\"
            move_from_fullpath = "/".join(move_from_fullpath) + "/"

            
            move_from = basename(source)
            move_to = destination
            compression_key =bytes(password, 'utf-8')
            chdir(move_from_fullpath)

            zf = AESZipFile(tmpdir + "/" + move_from +".rar", "w", compression=ZIP_LZMA,encryption=WZ_AES)
            zf.setpassword(compression_key)
            for dirname, subdirs, files in walk(move_from):
                for filename in files:
                    zf.write(join(dirname, filename))
            zf.close()
            try:
                shutil.copy(tmpdir + "/" + move_from +".rar", move_to)
                self.logger.success("Successfully copied file from: " + tmpdir + "/" + move_from +".rar" + " to " + move_to )
                
            except Exception as e:
                self.logger.error("Error copying file from: " + tmpdir + "/" + move_from +".rar" + " to " + move_to )
                self.logger.error("File is: " + tmpdir + "/" + move_from +".rar")
                self.logger.error(e)
                chdir(curdir)
                ctypes.windll.user32.MessageBoxW(0, "Error copying file, please make sure it is closed.", "Error", 0)
                return False
        chdir(curdir)
        return True


