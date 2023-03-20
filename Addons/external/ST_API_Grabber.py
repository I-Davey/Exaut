from __important.PluginInterface import PluginInterface
from __important.PluginInterface import Types as T

import requests, json
class ST_API_Grabber(PluginInterface):
    load = True
    #i need save folder, i need save name, i need url, i need url params, i need filter, i need auth token
    types = T.folderpath | T.filename |  T.target | T.databasepath | T.databasename | T.keypath
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}
    type_types = {"folderpath":{"type":"drag_drop_folder", "description":"please select the Save Folder", "optional":False},
                    "filename":{"type":"text", "description":"please enter the Save Name", "optional":False},
                    "target":{"type":"text", "description":"please enter the URL", "optional":False},
                    "databasepath":{"type":"text", "description":"please enter the URL Params", "optional":False},
                    "databasename":{"type":"text", "description":"please enter the Filter", "optional":True},
                    "keypath":{"type":"text", "description":"please enter the Auth Token", "optional":False},
                    }

    callname = "st_api_grabber"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, save_folder, save_name, url, url_params, filter, auth_token) -> bool:
        self.logger.info("Starting")
        if filter: filter = filter.split(",")
        else: filter = []
        url_params = json.loads(url_params)
        Record = Records(url, url_params, auth_token, filter)
        data = Record.start()
        self.logger.info(f"Found {len(data)} records")
        #save to file
        with open(f"{save_folder}/{save_name}.json", "w") as f:
            f.write(json.dumps(data))
        self.logger.info("Finished")

class Records:
    data = []
    params:dict
    url:str
    filters:list


    def __init__(self, url, params, auth_token, filters = []):
        self.url = url
        self.params = params
        self.filters = filters
        self.auth_token = auth_token
        self.no_id = []

    def start(self):
        print(f"URL: {self.url}")
        self.add_url_params()
        self.data = self.get_all_records()
        self.filter()
        if self.filters != []: self.handle_duplicates()
        return self.data
        
    def handle_duplicates(self):
        self.data = list(set(self.data))

    def filter(self):
        #filters = [["k1"]["k2"]]
        #ie data.get("k1").get("k2")
        all_data = self.data
        data = []
        for record in all_data:
            r1 = record
            for key in self.filters:
                if not r1:
                    self.no_id.append(record)
                    break
                r1 = r1.get(key)
            data.append(r1)
        all_data = data
        self.data = all_data

    def get_dict(self, url) -> dict:
        payload={}
        headers = {
        'accept': 'text/json',
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'authorization': f'Basic {self.auth_token}',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return json.loads(response.text)

    def get_page(self):
        page = 1
        while True:
            url1 = self.add_url_params({"page": page})
            data = self.get_dict(url1)
            if data["data"]:
                yield data
            else:
                break
            page += 1

    def get_all_records(self):
        all_records = []
        for page in self.get_page():
            print(f"Page: {page['page']}")
            all_records.extend(page["data"])
        return all_records

    def add_url_params(self, other_params = {}):
        url = self.url + "?"
        for key, value in self.params.items():
            url = url + f"{key}={value}&"
        for key, value in other_params.items():
            url = url + f"{key}={value}&"
        return url[:-1]
