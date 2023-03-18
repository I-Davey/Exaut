from __important.PluginInterface import PluginInterface
from __important.PluginInterface import Types as T
import io
import sys
import pandas as pd
import numpy as np
import folium
from PyQt6 import QtWidgets
#qtsignal
from PyQt6.QtCore import pyqtSignal

#webengine
class w3w_map(PluginInterface):
    load = True
    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}
    types = T.source
    type_types = {"source":{"type":"drag_drop_file", "description":"please select the csv file", "optional":False}, "__Name":"W3W Streamlit Map"}

    callname = "w3w_map"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, filepath) -> bool:
        import what3words

        w3w = what3words.Geocoder("T9PTXHI8")

        all_coords = []
        #open csv file
        #read csv file
        #csg = [w3w_name, w3w]
        #read excel with sheet w3w_map
        locnames_w3w = pd.read_excel(filepath, sheet_name="w3w")
        for index, row in locnames_w3w.iterrows():
            #print(row['w3w_name'], row['w3w'])
            coords = w3w.convert_to_coordinates(row['w3w'])
            all_coords.append([row['w3w_name'], coords['coordinates']['lat'], coords['coordinates']['lng']])
            #define the view the map will have, the zoom level and the center of the map with midpoint
        midpoint = [np.nanmean([x[1] for x in all_coords]), np.nanmean([x[2] for x in all_coords])]

            
        
        folium_map = folium.Map(location=[midpoint[0], midpoint[1]], zoom_start=10)
        for i in range(len(all_coords)):
            folium.Marker([all_coords[i][1], all_coords[i][2]], popup=all_coords[i][0]).add_to(folium_map)
        data = io.BytesIO()
        folium_map.save(data, close_file=False)
        x = self.Popups.custom(Dialog, data, (800, 600))


class Dialog(QtWidgets.QDialog):
    signal = pyqtSignal(tuple)
    _done = False

    def __init__(self,  parent, data, size):
        super().__init__(parent)
        self.setWindowTitle("Webview")
        self.webview = parent.QtWebEngineWidgets.QWebEngineView()
        self.webview.setHtml(data.getvalue().decode("utf-8"))
        self.webview.resize(size[0], size[1])
        self.webview.show()
        self.closeEvent()
        




                
        
 
        


    def closeEvent(self, a0) -> None:
        if not self._done:
            self.signal.emit((True,))
        self.close()
        a0.accept()

