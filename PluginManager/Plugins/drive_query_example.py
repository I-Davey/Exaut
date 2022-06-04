from .__important.PluginInterface import PluginInterface
import os
import ctypes
import webbrowser
import subprocess
class drive_query_example(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"source":3, "buttonname":11, "target":4}
    type_types = {"url_type":["selection", "Select URL Type", ["Classic URL", "URL OneNote", "URL OneNote Desktop", "URL Telegram",  "URL TradingView", "MS Edge"]], "source":["text", "Enter URL"], "__Name":"URL"}

    callname = "dqe"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def getTypeFunc(self, bseq) -> dict:
        if bseq["url_type"] == "URL OneNote":
            if bseq["source"].find("onenote:")>-1:
                    bseq["source"] =  bseq["source"][bseq["source"].find("onenote:"):]

        
        elif bseq["url_type"] == "URL OneNote Desktop":
            if bseq["source"].find("onenotedesktop:")>-1:
                    bseq["source"] =  bseq["source"][bseq["source"].find("onenotedesktop:"):]
            elif bseq["source"].find("onenote:")>-1:
                    bseq["source"] =  bseq["source"][bseq["source"].find("onenote:"):]
                    #repplace onenote: with onenotedesktop:
                    bseq["source"] = f"onenotedesktop:{bseq['source'][8:]}"

        elif bseq["url_type"] == "URL TradingView":
                    bseq["source"] =  "tradingview: "+bseq["source"]

        elif bseq["url_type"] == "URL Telegram":
            #spit by / and take the last and second lsat items
            split_url = bseq["source"].split("/")
            if len(split_url)>2:
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
 
        #remove type from bseq
        del bseq["url_type"]
        return(bseq)
    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, folderpath, filename, source, buttonname, target ) -> bool:
        
        path = str(folderpath)+"\\"+str(filename)
        if os.path.exists(path)==False:
            if target:
                if os.path.exists(target):
                    try:

                        print(webbrowser.__dict__)
                        #webbrowser.get(target).open(str(source))
                    except Exception as e:
                        self.logger.error(e)
                        return False
            else:
                try:
                    webbrowser.open(str(source))  # Go to example.com
                except Exception as e:
                    ctypes.windll.user32.MessageBoxW(0,path+" does not exist?","Failed url: "+buttonname+"!",0)
                    self.logger.error(e)
        else:

            subprocess.call([path,'-new-tab',str(source)])
