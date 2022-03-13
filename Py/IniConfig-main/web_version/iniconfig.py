import configparser
import os

class Parse():


    def __init__(self):
        self.config = configparser.ConfigParser()
        configlocation = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '\config.ini')
        #print(configlocation)
        self.config.read(configlocation)

class Generate(Parse):

    def __init__(self, var = None):
        super().__init__()
        default_items = ["type","port","pub_ip"]
        main = self.config["MAIN"]
        pub_ip = main["pub_ip"]
        priv_ip = main["priv_ip"]
        self.data = []
        for item in self.config:
            if item not in ("MAIN", "DEFAULT"):
                other_items = {}
                for sub_item in self.config[item]:
                    if sub_item not in default_items:
                        other_items[sub_item] = self.config[item][sub_item]
                item_details = self.config[item]
                json_arr = {"name":item,"type":item_details["type"], "ip": (pub_ip if int(item_details["pub_ip"]) == True  else priv_ip), "port":int(item_details["port"]) }
                if other_items:
                    json_arr.update(other_items)
                other_items = {}
                self.data.append(json_arr)
        if var:
            for item in self.data:
                if item["name"] == var:
                    self.data = item


        


        
       
"""
def main():
    #first example
    example_call = ConfigExample()
    int_example = example_call.integerexample
    string_example = example_call.stringexample
    print("example integer grabbed from Ini file, first config:", int_example)
    print("example String grabbed from Ini file, first config:", string_example)



if __name__ == "__main__":
    main()
"""

