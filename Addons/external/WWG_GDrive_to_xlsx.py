from __important.PluginInterface import PluginInterface

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pandas import DataFrame
import threading
import os
from time import perf_counter


class WWG_GDrive_to_xlsx(PluginInterface):
    load = True
    types = {"target":4,"keyfile":8}
    type_types = {"target":{"type":"drag_drop_folder", "description":"please select the Target Folder"},"keyfile":{"type":"drag_drop_file", "description":"please select the secret file"}}

    callname = "wwgdrive"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}





    def main(self,save_loc, secret_loc):
        start_time = perf_counter()
        filename = "\\WWG_GDrive.xlsx"
        save_loc = save_loc.replace("/", "\\")
        secret_loc = secret_loc.replace("/", "\\")
        #secret_loc = file, get the folder the file is in
        curdir = os.getcwd()
        os.chdir('\\'.join(secret_loc.split('\\')[0:-1]))

        
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()

        folders = {'1. wwg': '0AOG66lUCLaTtUk9PVA', '2. client & partner accounts': '0AIYHFwOssZQlUk9PVA', '3. projects': '0AAElCGhMRwuvUk9PVA', '4. business development': '0AJHm2j8iDozAUk9PVA', '5. marketing': '0ABdxz7Lx5bjlUk9PVA', '6. success': '0AM_bLyoeGm83Uk9PVA', '7. sustainability': '0AAnRIXoVay5dUk9PVA', '12. executive committee': '0AMYkgv6Pnp5qUk9PVA', '15. g17eco': '0AHaqiGXyRb4TUk9PVA', '19. wwg academy': '0AG3bMM83nciQUk9PVA', 'ct light': '0ADPFl5O78BFcUk9PVA', 'project tracker app': '0ANnua7IDH2boUk9PVA', 'project ubuntu': '0AKcdgIqiIH15Uk9PVA', 'sustainability reseach': '0AO5QxsK4LVw3Uk9PVA'}        #Parse('SHARED FOLDERS').cfg
        self.folders_kvswapped = {v: k for k, v in folders.items()}
        #Parse('SHARED FOLDERS').cfg
        self.logger.debug(folders)




        self.drive = GoogleDrive(gauth)
        folder = "19. wwg academy"
        folder_id = folders[folder]
        """
        query  = create_drive_query(folder_id)
        items = drive.ListFile(query).GetList()
        self.logger.debug(folder)
        self.logger.debug(items[0])
        for item in items:
            file_type = 'folder' if item['mimeType']=='application/vnd.google-apps.folder' else 'file'
            folder_location = None
            url = item['alternateLink']
            modified = item['modifiedDate']
            modified_by = item['lastModifyingUser']['displayName']
            created = item['createdDate']
            self.logger.debug(f'{file_type} {item["title"]} {url} {modified} {modified_by} {created}')
        """


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
        items = self.drive.ListFile(query).GetList()
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
                try:
                    x = self.getFolderData(item['id'], path, count, teamdriveid)
                    if x == False:
                        return False
                except:
                    pass
        return True


    def create_drive_query(self, folder_id:str, teamdriveid:str) -> dict:
        return {'q':f"'{folder_id}' in parents and trashed=false", 'corpora': 'teamDrive', 'teamDriveId': f'{teamdriveid}', 'includeTeamDriveItems': True, 'supportsTeamDrives': True}



            



