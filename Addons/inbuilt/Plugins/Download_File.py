from .__important.PluginInterface import PluginInterface
import requests
import os


class Download_File(PluginInterface):
    load = True
    types = {"source":3,"target":4}
    type_types = {"source":{"type":"text", "description":"please enter the download url", "optional":True},
     "target":["drag_drop_folder", "Please select the Target Folder"],
     "__Name":"Download File"}

    callname = "file_download"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, source_url,target_folder) -> bool:
        self.logger.debug(f"source_url: {source_url}")
        self.logger.debug(f"target_folder: {target_folder}")

        filename = os.path.basename(source_url)
        self.logger.debug(f"filename: {filename}")

        r = requests.get(source_url, allow_redirects=True)
        open(os.path.join(target_folder, filename), 'wb').write(r.content)

        self.logger.success(f"file {filename} has been downloaded")
        return True
    
