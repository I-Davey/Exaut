from .__important.PluginInterface import PluginInterface
from os import walk, chdir, getcwd
from os.path import join, basename
from tempfile import TemporaryDirectory
from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES
from shutil import copy
class Zipcrypt(PluginInterface):
    load = True
    types = {"source":3,"target":4,"databasename":6, "keyfile":8}
    type_types = {"source":["drag_drop_folder", "please select source folder"],"target":["drag_drop_folder", "please select destination folder"], "databasename":["text", "please enter password",None, True], "keyfile":["selection","Select file extension: zip or rar",  ["zip", "rar"]], "__Name":"Zipcrypt"}
    callname = "zipcrypt"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True





    def main(self,source, destination, password, extension, ) -> bool:
        curdir = getcwd()
        if not extension:
            extension = "rar"
        extension = f".{extension}"
        with TemporaryDirectory() as tmpdir:
            #replace all \\ in source, destination with /
            source = source.replace("\\", "/")
            destination = destination.replace("\\", "/")
            move_from_fullpath = source.split("/")[:-1]
            #combine move_from_fullpath into string seperated by "\\"
            move_from_fullpath = "/".join(move_from_fullpath) + "/"

            
            move_from = basename(source)
            move_to = destination
            if password:
                compression_key =bytes(password, 'utf-8')
            chdir(move_from_fullpath)

            zf = AESZipFile(tmpdir + "/" + move_from + extension, "w", compression=ZIP_LZMA,encryption=WZ_AES)
            if password:
                zf.setpassword(compression_key)
            for dirname, subdirs, files in walk(move_from):
                for filename in files:
                    zf.write(join(dirname, filename))
            zf.close()
            try:
                copy(tmpdir + "/" + move_from + extension, move_to)
                self.logger.success("Successfully copied file from: " + tmpdir + "/" + move_from + extension + " to " + move_to )
                
            except Exception as e:
                self.logger.error("Error copying file from: " + tmpdir + "/" + move_from + extension + " to " + move_to )
                self.logger.error("File is: " + tmpdir + "/" + move_from + extension)
                self.logger.error(e)
                chdir(curdir)
                self.Popups.alert("Error copying file, please make sure it is closed.", "Error: " + str(e))
                return False
        chdir(curdir)
        return True


