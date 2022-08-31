# %%
import pandas as pd
import openpyxl as xl
import os
import sys
import tempfile
import shutil

# %%
#path to file (folder): C:\Users\idave\OneDrive\GraffitiWipeout
#file name: Sage2Xero.xlsx
#full path: C:\Users\idave\OneDrive\GraffitiWipeout\Sage2Xero.xlsx
#sheet name: MapPandas
#pull in w/ pandas first to test

# %%
#configured vars
folder_path = "C:/Users/idave/OneDrive/GraffitiWipeout/"
file_name_map = "Sage2Xero.xlsx"
file_name_sage_customers = "Sage_Customers.csv"
full_path_name_map = folder_path + file_name_map
full_path_name_sage_customers = folder_path + file_name_sage_customers
sheet_name = "MapPandas"
#import temp folder creator
temp_folder = tempfile.mkdtemp()



# %%
#copy file to temp folder
shutil.copy(full_path_name_map, temp_folder)
shutil.copy(full_path_name_sage_customers, temp_folder)

#create full path to file in temp folder
temp_sage_customers = temp_folder + "\\" + file_name_sage_customers
temp_map = temp_folder + "\\" + file_name_map

# %%
#load temp_map into pandas
df_map = pd.read_excel(temp_map, sheet_name=sheet_name)
sage_example = pd.read_excel(temp_map, sheet_name="Sage")
xero_example = pd.read_excel(temp_map, sheet_name="Xero")
sage_customers = pd.read_csv(temp_sage_customers)




# %%
#map the sage columns to xero columns, ie   sage_column = xero_column
map_cols = {}
for index, row in df_map.iterrows():
    map_cols[row[0]] = row[1]

mapped_df = pd.DataFrame(columns=xero_example.columns)

all_data = []
#go through each row in the sage_customers and map the columns
for index, row in sage_customers.iterrows():
    mapped_row = {}
    for key, value in row.items():
        if key in map_cols:
            mapped_row[map_cols[key]] = value
    all_data.append(mapped_row)
        


# %%
#map all_data to a df
mapped_df = pd.DataFrame(all_data)
mapped_df.to_excel(folder_path + "xero_customers_pandas.xlsx")

mapped_df["FirstName"] = ""
mapped_df["LastName"] = ""

for index, row in mapped_df.iterrows():
    firstname_lastname = row["FirstName|LastName"]

    #drop the firstname and lastname columns
    #split the firstname and lastname
    if type(firstname_lastname) is not str:

        mapped_df.loc[index, "FirstName"] = firstname_lastname
        mapped_df.loc[index, "LastName"] = ""
    else:
        
        name_arr = firstname_lastname.strip().split(" ")
        if len(name_arr) > 1:
            last_name = name_arr[-1]
            first_name = " ".join(name_arr[:-1])
            mapped_df.loc[index, "FirstName"] = first_name
            mapped_df.loc[index, "LastName"] = last_name
        else:
            mapped_df.loc[index, "FirstName"] = firstname_lastname
            mapped_df.loc[index, "LastName"] = ""

    email  = row["EmailAddress"]
    if type(email) is str:
        if ";" in email:
            email_arr = email.split(";")
            mapped_df.loc[index, "EmailAddress"] = email_arr[0]
            mapped_df.loc[index, "Person1FirstName"] = email_arr[1].split("@")[0]
            mapped_df.loc[index, "Person1Email"] = email_arr[1]
    

mapped_df["Website"] = mapped_df["Website"].apply(lambda x: "https://" + x if type(x) == str and "http" not in x.lower() else x)

#drop the firstname and lastname columns
mapped_df.drop(columns=["FirstName|LastName"], inplace=True)
#reorder columns to match exactly that of xero, adding the extra columns

missing_cols = list(set(xero_example.columns) - set(mapped_df.columns))
for col in missing_cols:
    mapped_df[col] = ""
mapped_df = mapped_df[xero_example.columns]

#website = "HTTPS://" + mapped_df["Website"]




#save to folder as xero_customers_example.xlsx
fullpath = folder_path + "xero_customers.csv"
mapped_df.to_csv(fullpath, index=False)


