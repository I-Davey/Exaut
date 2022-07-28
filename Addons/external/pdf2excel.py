from __important.PluginInterface import PluginInterface
import tabula
import pandas as pd

class pdf2excel(PluginInterface):
    load = True
    types = {"databasepath":5,"filename":1,"folderpath":0,"source":3,"target":4}
    type_types = {
    "source":{"type":"text", "description":"enter start page", "optional":True},
    "target":{"type":"text", "description":"enter end page", "optional":True},
    "databasepath":{"type":"drag_drop_file", "description":"select pdf"},
    "filename":{"type":"text", "description":"enter new file name"},
    "folderpath":{"type":"drag_drop_file", "description":"select save location"},
    "__Name":"PDF: Save to Excel"}
    callname = "pdf2xcl"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self,  file, savename, saveloc, start = None, end  = None, Popups = None) -> bool:
        with open(file, 'rb') as f:
            #save all pages between start and end, write to savename in saveloc
            #if start and end are not specified, save all pages
            if start and end:
                dfs = tabula.read_pdf(file, pages=list(range(int(start), int(end))))
            elif start and not end:
                dfs = tabula.read_pdf(file, pages=list(range(int(start), int(tabula.read_pdf(file, pages=None).shape[0]))))
            elif not start and end:
                dfs = tabula.read_pdf(file, pages=list(range(1, int(end))))
            else:
                dfs = tabula.read_pdf(file, pages=None)
            #convert dfs == pandas dartaframe save all as different tables within excel document
            for i in range(len(dfs)):
                dfs[i].to_excel(saveloc + "\\" + savename + str(i) + ".xlsx", index = False)
            self.logger.success(f"saved {len(dfs)} tables to: {saveloc + '/' + savename}")
            
           
            
           