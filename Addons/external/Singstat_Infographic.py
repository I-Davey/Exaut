from urllib import request
from __important.PluginInterface import PluginInterface
import re
import yaml
import pandas as pd

class Singstat_Infographic(PluginInterface):
    load = True
    types = {"source":3}
    type_types = {"source":["drag_drop_folder", "Please select save_location"], "__Name":"Singstat Infographic Scraper"}

    callname = "ss_infographic"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}


    def main(self, source, Popups) -> bool: 
        #get 

        data  = request.urlopen("https://www.singstat.gov.sg/modules/infographics/economy").read()
        #split var SectionTwoData = 
        data = data.decode("utf-8")
        data = data.split("var SectionTwoData = ")
        data = data[1]
        #/* Section Three - Real GDP Growth
        data = data.split("/* Section Three - Real GDP Growth")
        data = data[0]
        #remove all /r /b and stuff from data using re.sub
        data = re.sub(r'[\n\r\t]', '', data)
        #$replace \' with "
        data = data.replace("\'", '"')
        #replace all multi spaces
        data = re.sub(r'\s+', ' ', data)
        data = yaml.load(data, Loader=yaml.FullLoader)
        #load data into a json file


        gdp_json = data["chartData"]
        gdp_json_label_data = [x["label"] for x in gdp_json]
        
        
        expenditure_json = data["chartDataExpenditure"]
        expenditure_json_label_data = [x["label"] for x in expenditure_json]
        


        income_json = data["chartDataincome"]
        income_json_label_data = [x["label"] for x in income_json]

        #load the json data into pandas dataframes as different sheets and delete icon column
        df_gdp = pd.DataFrame(gdp_json_label_data, columns=["value", "description", "icon", "position"])
        df_expenditure = pd.DataFrame(expenditure_json_label_data, columns=["value", "description", "icon", "position"])
        df_income = pd.DataFrame(income_json_label_data, columns=["value", "description", "icon", "position"])

        #replace <br> with a space
        df_gdp["description"] = df_gdp["description"].str.replace("<br>", " ")
        df_expenditure["description"] = df_expenditure["description"].str.replace("<br>", " ")
        df_income["description"] = df_income["description"].str.replace("<br>", " ")

        df_gdp["description"] = df_gdp["description"].str.replace("  ", " ")
        df_expenditure["description"] = df_expenditure["description"].str.replace("  ", " ")
        df_income["description"] = df_income["description"].str.replace("  ", " ")


        #drop icon
        df_gdp = df_gdp.drop(columns=["icon"])
        df_expenditure = df_expenditure.drop(columns=["icon"])
        df_income = df_income.drop(columns=["icon"])
        #combine the dataframes with a new column called "type" with value of gdp, expenditure or income
        df_gdp["type"] = "gdp"
        df_expenditure["type"] = "expenditure"
        df_income["type"] = "income"
        #concatenate the dataframes
        df = pd.concat([df_gdp, df_expenditure, df_income])
        
        #drop position
        df = df.drop(columns=["position"])

        #load into excel
        while True:
            try:
                df.to_excel(source + "/singstat_infographic.xlsx")
                self.logger.success("Singstat Infographic Scraper: Saved to " + source + "/singstat_infographic.xlsx")
                return True
            except:
                self.logger.error("Singstat Infographic Scraper: Could not save to " + source + "/singstat_infographic.xlsx")
                x = Popups.yesno("Singstat Infographic Scraper: Could not save to " + source + "/singstat_infographic.xlsx, Would you like to Retry?", "Singstat Infographic Scraper")
                if not x:
                    return False
            

        






        

