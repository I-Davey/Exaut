from __important.PluginInterface import PluginInterface

import pyperclip

class on_link_fixer(PluginInterface):
    load = True
    types = {"source":3}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}
    type_types = {"source":["selection", "Select URL Type", ["OneNote App", "OneNote Desktop"]], "__Name":"Onenote Link Fixer"}
    callname = "1nlinkfix"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, source, Popups) -> bool:
        while True:
            summary = Popups.data_entry(f"{source} Url Fixer", f"(output: {source}) Please Enter Onenote Url:")
            if summary == None:
                break
            if source == "OneNote App":
                if summary.find("onenote:")>-1:
                        summary =  summary[summary.find("onenote:"):]

            
            elif source in "OneNote Desktop":
                if summary.find("onenotedesktop:")>-1:
                        summary =  summary[summary.find("onenotedesktop:"):]
                elif summary.find("onenote:")>-1:
                        summary =  summary[summary.find("onenote:"):]
                        #repplace onenote: with onenotedesktop:
                        summary = f"onenotedesktop:{summary[8:]}"
            pyperclip.copy(summary)
            self.logger.success(f"Copied {summary} to clipboard")
            

