from __important.PluginInterface import PluginInterface

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pandas import DataFrame
import threading
import os
from time import perf_counter


class WWG_GDrive_xlsx_Local_Downloader(PluginInterface):
    load = True
    types = {"target":4,"keyfile":8}
    type_types = {"target":{"type":"drag_drop_folder", "description":"Please select the save location"},"keyfile":{"type":"drag_drop_file", "description":"please select the secret file"}}

    callname = "wwgdrivelocalsdwnld"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        self.titles = []
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}





    def main(self,save_loc, secret_loc):
        curdir = os.getcwd()
        os.chdir(save_loc)
        start_time = perf_counter()
        filename = "\\WWG_GDrive.xlsx"
        save_loc = save_loc.replace("/", "\\")
        secret_loc = secret_loc.replace("/", "\\")
        self.save_loc = save_loc
        #secret_loc = file, get the folder the file is in
        curdir = os.getcwd()
        os.chdir('\\'.join(secret_loc.split('\\')[0:-1]))

        
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
    

        folders = {"root": 'root'}
        self.folders_kvswapped = {v: k for k, v in folders.items()}
        #Parse('SHARED FOLDERS').cfg
        self.logger.debug(folders)




        self.drive = GoogleDrive(gauth)



        self.d_ext_desc = {'csv':'CSV file',
                    'db':'Thumbnail',
                    'doc':'Microsoft Word Document',
                    'docx':'Microsoft Word Document',
                    'GIF':'GIF Image file',
                    'html':'HTML file',
                    'ico':'Icon Image file',
                    'jpg':'JPG Image file',
                    'JPEG':'JPEG Image file',
                    'json':'JSON file',
                    'lnk':'Shortcut file',
                    'msg':'Microsoft Outlook Message file',
                    'pdf':'PDF file',
                    'pkl':'Pickle (python) file',
                    'png':'PNG Image file',
                    'ppt':'Microsoft Powerpoint file',
                    'pptx':'Microsoft Powerpoint file',
                    'pst':'Microsoft Outlook Data file',
                    'py':'Python file',
                    'pyc':'Python file (compiled)',
                    'rtf':'Rich Text Format',
                    'svg':'SVG Image file',
                    'txt':'Text document',
                    'url':'Hyperlink',
                    'vsd':'Microsoft Visio file',
                    'xls':'Microsoft Excel file',
                    'xlsb':'Microsoft Excel file',
                    'xlsm':'Microsoft Excel (Macro-enabled) file',
                    'xlsx':'Microsoft Excel file',
                    'yml':'Requirements file (python)',
                    'zip':'ZIP file'}


        self.data =[['File', 'File Type', 'Folder Location', 'Link', 'Path', 'URL', 'Modified', 'Modified By', 'Created', 'Main Folder']]

        count = 0
        max = 100
        #set df headers 
        threads = []
        for folder, folder_id in folders.items():
            try:

                t = threading #self.getFolderData(folder_id, folder, 0, folder_id)
                t = threading.Thread(target=self.getFolderData, args=(folder_id, folder, 0, folder_id))
                t.start()
                threads.append(t)
            except:
                pass
        
        for t in threads:
            t.join()

        df = DataFrame(self.data)
        df.to_excel(save_loc + filename)
        os.chdir(curdir)
        self.logger.success(f"Finished, file saved to {save_loc + filename} in {round(perf_counter() - start_time, 2)} seconds")
        


    def ext_desc(self, ext):
        try:
            desc = self.d_ext_desc[ext]
        except KeyError:
            desc = 'file'
        else:
            pass
        return desc


    def getFolderData(self, folder_id, full_path, count, teamdriveid):

        query = self.create_drive_query(folder_id, teamdriveid)
        items = self.drive.ListFile().GetList()
        for item in items:
            count = count + 1
            if count > 10000000000000:
                return False
            file_type = 'folder' if item['mimeType']=='application/vnd.google-apps.folder' else 'file'
            if file_type == 'file':
                #create var with end of file after .
                ext = item['title'].split('.')[-1]
                file_type = self.ext_desc(ext)
            folder_location = None
            url = item['alternateLink'] if 'alternateLink' in item else None
            modified = item['modifiedDate'] if 'modifiedDate' in item else None
            modified_by = item['lastModifyingUser']['displayName'] if 'lastModifyingUser' in item else None
            created = item['createdDate'] if 'createdDate' in item else None
            folder_location = "/" + full_path + "/"
            link = f'=HYPERLINK("{url}", "link")' if url else None
            path = full_path + '/' + item['title']
            temp_path = "/" + path

            self.data.append([item['title'], file_type, folder_location, link, temp_path, url, modified, modified_by, created, self.folders_kvswapped[teamdriveid]])
            self.logger.debug(f'{file_type} {item["title"]} {url} {modified} {modified_by} {created}')

            if file_type == 'folder':
                if item['title'] not in self.titles:
                    self.titles.append(item['title'])
                    try:
                        x = self.getFolderData(item['id'], path, count, teamdriveid)
                        if x == False:
                            return False
                    except:
                        pass
            else:
                self.handle_download(item)
        return True



    def handle_download(self, item):
        #gdrive file type
        #if doc
        if item['mimeType'] == 'application/vnd.google-apps.document':
            self.drive.auth.service.files().export_media(fileId=item['id'], mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document').execute()
        elif item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            self.drive.auth.service.files().export_media(fileId=item['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet').execute()
        elif item['mimeType'] == 'application/vnd.google-apps.presentation':
            self.drive.auth.service.files().export_media(fileId=item['id'], mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation').execute()
        elif item['mimeType'] == 'application/vnd.google-apps.drawing':
            self.drive.auth.service.files().export_media(fileId=item['id'], mimeType='application/vnd.openxmlformats-officedocument.drawingml.sheet').execute()
        elif item['mimeType'] == 'application/vnd.google-apps.form':
            self.drive.auth.service.files().export_media(fileId=item['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet').execute()
        elif item['mimeType'] == 'application/vnd.google-apps.script':
            self.drive.auth.service.files().export_media(fileId=item['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet').execute()
        elif item['mimeType'] == 'application/vnd.google-apps.fusiontable':
            self.drive.auth.service.files().export_media(fileId=item['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet').execute()
        elif item['mimeType'] == 'application/vnd.google-apps.folder':
            pass
        else:
            item.GetContentFile(item['title'])
        
        

    def create_drive_query(self, folder_id:str, teamdriveid:str) -> dict:
        return {'q':f"'trashed=false"}


if __name__ == "__main__":
    wwgdrivelocals = WWG_GDrive_to_xlsx_locals()
    from loguru import logger
    wwgdrivelocals.load_self({"log":logger})
    save_loc = "Z:\\Dev\\projects\\OninO\\GDRIVE"
    secret_loc = "Z:\\Dev\\projects\\OninO\\GDRIVE\\client_secrets.json"
    wwgdrivelocals.main(save_loc, secret_loc)



            



