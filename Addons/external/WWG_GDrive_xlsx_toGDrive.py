from __important.PluginInterface import PluginInterface

from pydrive2.auth import GoogleAuth
import os
from pydrive2.drive import GoogleDrive
import webbrowser

class WWG_GDrive_xlsx_toGDrive(PluginInterface):
    load = True
    types = {"keyfile":8, "target":4}
    type_types = {"keyfile":{"type":"drag_drop_file", "description":"please select the secret file"}, "target":{"type":"drag_drop_folder", "description":"please select default folder"}}

    callname = "wwgxlsx2gdrive"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True







    def main(self,secret_loc, target_loc, ):

        secret_loc = secret_loc.replace("/", "\\")
        curdir = os.getcwd()
        os.chdir('\\'.join(secret_loc.split('\\')[0:-1]))
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)

        #secret_loc = file, get the folder the file is in
        os.chdir('\\'.join(secret_loc.split('\\')[0:-1]))
        file = self.Popups.select_file("Select the xlsx file to upload", target_loc)
        if file == None:
            return
        file = file.replace("/", "\\")
        filename = file.split('\\')[-1]
        os.chdir(curdir)

        #file is D:/xlsxfiletouploadtogdrive.xlsx
        #upload to gdrive
        filename = filename.replace(".xlsx", "")
        filename =  self.Popups.data_entry("Enter the name of the file to upload", "Upload file", filename)
        filename = filename + ".xlsx"

        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file1 in file_list:
            if file1['title'] == filename:
                if self.Popups.yesno(f"File '{filename}' already exists", "File already exists, overwrite?"):
                    file1.Delete()
                else: 

                    return False
        file1 = drive.CreateFile({'title': filename})
        file1.SetContentFile(file)
        file1.Upload()
        #get link to file
        link = file1['alternateLink']
        self.Popups.alert("File uploaded, check console for link", "File uploaded")
        self.logger.success(f"File uploaded: {link}")
        if self.Popups.yesno("Open link in browser?", "Open link in browser?"):
            webbrowser.open(link)
        os.chdir(curdir)




            



