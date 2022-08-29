from .__important.PluginInterface import PluginInterface
import os
import webbrowser
import subprocess
class Run_URL(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"source":3, "buttonname":11, "target":4}
    type_types = {"url_type":["selection", "Select URL Type", ["Classic URL", "URL OneNote Win10", "URL OneNote Desktop", "URL Telegram",  "URL TradingView", "URL Slack", "MS Edge"]], "source":["text", "Enter URL"], "__Name":"URL"}

    callname = "url"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def getTypeFunc(self, bseq, btn) -> dict:
        if bseq["url_type"] == "URL OneNote Win10":
            if bseq["source"].find("onenote:")>-1:
                    bseq["source"] =  bseq["source"][bseq["source"].find("onenote:"):]
                    if btn["buttondesc"] == "section":
                        btn["buttondesc"] = "URL OneNote Win10 -> Section"

        
        elif bseq["url_type"] == "URL OneNote Desktop":
            if bseq["source"].find("onenotedesktop:")>-1:
                    bseq["source"] =  bseq["source"][bseq["source"].find("onenotedesktop:"):]


                    
            elif bseq["source"].find("onenote:")>-1:
                    bseq["source"] =  bseq["source"][bseq["source"].find("onenote:"):]
                    #repplace onenote: with onenotedesktop:
                    bseq["source"] = f"onenotedesktop:{bseq['source'][8:]}"

            if btn["buttondesc"] == "section":
                btn["buttondesc"] = "URL OneNote Desktop -> Section"


        elif bseq["url_type"] == "URL TradingView":
                    bseq["source"] =  "tradingview: "+bseq["source"]

        elif bseq["url_type"] == "URL Slack":
                    if "/client/" in bseq["source"]:
                            if "buttondesc" not in btn:
                                btn["buttondesc"] = "Slack Website URL"

                        
                    elif "/archives/" in bseq["source"]: 
                            if "buttondesc" not in btn:
                                btn["buttondesc"] = "Slack Application URL"

        elif bseq["url_type"] == "URL Telegram":
            #spit by / and take the last and second lsat items
            split_url = bseq["source"].split("/")
            if len(split_url)>2:
                if split_url[-1][0] == "+":
                    group = f"{split_url[-1][1:]}"
                    #open to the group as a chat
                    bseq["source"] = f"tg://join?invite={group}"
                else:
                    post = split_url[-1]
                    channel = split_url[-2]
                    bseq["source"] = f"tg://privatepost?channel={channel}&post={post}"

        elif bseq["url_type"] == "MS Edge":
            bseq["folderpath"] = "C:\Program Files (x86)\Microsoft\Edge\Application"
            bseq["filename"] = "msedge.exe"
            bseq["type"] = "exe"
            bseq["source"] = bseq["source"]
            bseq["target"] = None
            #remove bseq["target"]
            bseq.pop("target")
        
        else:
            if "mail.google" in bseq["source"]:
                btn["buttondesc"] = "Google Mail"
            elif "main.proton" in bseq["source"]:
                btn["buttondesc"] = "Proton Mail"
            elif "drive.google.com/drive/folder" in bseq["source"]:
                btn["buttondesc"] = "GD Folder"
            elif "drive.google.com" in bseq["source"]:
                btn["buttondesc"] = "Google Drive"
            elif "docs.google.com/spreadsheet" in bseq["source"]:
                btn["buttondesc"] = "GD Sheet"
            elif "docs.google.com/presentation" in bseq["source"]:
                btn["buttondesc"] = "GD Slides"
            elif "docs.google.com/document" in bseq["source"]:
                btn["buttondesc"] = "GD Document"
            elif "docs.google.com/form" in bseq["source"]:
                btn["buttondesc"] = "GD Form"
            elif "github.com" in bseq["source"]:
                btn["buttondesc"] = "GitHub"
            
            

        if "buttondesc" not in btn or btn["buttondesc"] == "":
            btn["buttondesc"] = bseq["url_type"]
        #remove type from bseq
        del bseq["url_type"]
        return(bseq, btn)
    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, folderpath, filename, source, buttonname, target , ) -> bool:
        
        path = str(folderpath)+"\\"+str(filename)
        if os.path.exists(path)==False:
            if target:
                if os.path.exists(target):
                    try:

                        print(webbrowser.__dict__)
                        #webbrowser.get(target).open(str(source))
                    except Exception as e:
                        self.logger.error(e)
            else:
                try:
                    webbrowser.open(str(source))  # Go to example.com
                except Exception as e:
                    self.Popups.alert(path+" does not exist?","Failed url: "+buttonname+"!")

                    self.logger.error(e)
        else:

            subprocess.call([path,'-new-tab',str(source)])
