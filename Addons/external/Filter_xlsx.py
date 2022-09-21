from __important.PluginInterface import PluginInterface

from time import perf_counter
import pandas as pd


class Filter_xlsx(PluginInterface):
    load = False
    types = {"target":4,"keyfile":8}
    type_types = {"target":{"type":"drag_drop_folder", "description":"please select the Target Folder"},"keyfile":{"type":"drag_drop_file", "description":"Please select the excel file to filter"}}

    callname = "filterxlsx"
    hooks_handler = ["log"]



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}





    def main(self,save_loc, pandas_excel_file):
        self.logger.info("Starting Filter_xlsx")
        filter_list = [
            'Growth Activists',
            'Competent Boards',
            'Engine B',
            'finnCap',
            'POV',
            'BUBKA',
            'Planet Groups',
            'Bob Earth',
            'SASB',
            'IMA',
            'D1 Labs',
            'UNGC',
            'The Leipziger Group',
            'Eco-Age',
            'FutureFit',
            'CyberQ',
            'Reaktiv',
            'Reslience Innovation Hub',
            'Green2Gold',
            'Queen of Raw',
            'Abundance',
            'QCA',
            'Alliance',
            'Agreement',
            'Partnership',
            'introducer'
        ]
        for i, filter_item in enumerate(filter_list):
            filter_list[i] = filter_item.lower()
            

        self.filter_list = filter_list
        self.df = None
        self.save_loc = save_loc
        self.pandas_excel_file = pandas_excel_file
        self.set_keys()
        #delete column 0 from self.df
        self.main_func()

    def set_keys(self):
        self.df = pd.read_excel(self.pandas_excel_file)
        #remove the first row (the keys) and get new keys based on next row
        self.df = self.df.rename(columns=self.df.iloc[0])
        self.df.drop(self.df.columns[0], axis=1, inplace=True)
        #add column called Filter
        self.df['Filter'] = ""
        

        #print keys

    def main_func(self):
        #only show files that are in the filter list, use regex to match based on spaces
        self.pandas_excel_file_name = self.pandas_excel_file.split('\\')[-1].split(".")[0]
        bslsh = "\\"
        #ignore case
        #print a random assor

        self.logger.info("Loaded xlsx.. Filtering files")
        self.df = self.df[self.df['File'].str.contains('|'.join(self.filter_list), case=False)]
        self.logger.info("Filtered files.. Adding filter column")
        for index, row in self.df.iterrows():
            #print(row['File'])
            for item in self.filter_list:
                if item.lower() in row['File'].lower():
                    self.df.at[index, 'Filter'] = str(self.df.at[index, 'Filter']) + " " + item
                    break
            else:
                self.df.at[index, 'Filter'] = "No Filter"

        self.logger.info("Saving xlsx")
                   
        self.df.to_excel(self.save_loc + "/" +self.pandas_excel_file_name + "_filtered.xlsx")
        self.logger.success(f"Finished filtering and saved to {self.save_loc + bslsh + self.pandas_excel_file_name + '_filtered.xlsx'}")

