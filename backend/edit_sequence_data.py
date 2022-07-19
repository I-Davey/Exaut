from .db.Exaut_sql import  *
from sqlalchemy import select, update, delete, insert

class Edit_Sequence:
    def __init__(self,  readsql, writesql, logger, alert, title):
        self.logger = logger
        self.readsql = readsql
        self.writesql = writesql
        self.alert = alert
        self.title = title
        pass

    def edit_sequence_data(self, button_name, tab_name, source):
        self.logger.info(f'Constructing data for edit sequence "{button_name}" on tab "{tab_name}" in form "{self.title}"')
        buttonseries_data = self.readsql(select(buttonseries.formname, buttonseries.tab, buttonseries.buttonname).where(buttonseries.assignname == source).where(buttonseries.formname == self.title).order_by(buttonseries.runsequence.asc()))
        current_button = self.readsql(select("*").where(buttons.buttonname == button_name).where(buttons.tab == tab_name).where(buttons.formname == self.title), one=True)
        if len(buttonseries_data) == 0:
            self.logger.warning(f"No buttonseries data found for button: {button_name} on tab: {tab_name} in form: {self.title}")

        dict_struct = {}
        dict_struct["buttonseries_data"] = [dict(item._mapping) for item in buttonseries_data]
        dict_struct["current_button"] = dict(current_button._mapping)
        state = "sequence"
        return(dict_struct, state) 
        
    def edit_sequence_update(self, data, buttons_table_dict, batchsequence_table_dict, button_series_table_dict):
        current_button = data["edit"]["button_data"]
        current_tab = current_button["tab"]
        current_form = current_button["formname"]
        current_name = current_button["buttonname"]
        current_assignname = data["sequence"]["current_batch"]["source"]

        if buttons_table_dict["buttonname"] != current_name:
            q = self.writesql(update(buttons).where(buttons.buttonname == current_name).where(buttons.tab == current_tab).where(buttons.formname == current_form).values(buttonname = buttons_table_dict["buttonname"]))
            if not q:
                self.alert(f"Error updating buttonname on tab {current_tab} in form {current_form}")
                return
            q = self.writesql(update(batchsequence).where(batchsequence.buttonname == current_name).where(batchsequence.tab == current_tab).where(batchsequence.formname == current_form).values(buttonname = buttons_table_dict["buttonname"]))
            if not q:
                self.alert(f"Error updating buttonname on tab {current_tab} in form {current_form}")
                return
        #delete all buttonseries data for this button
        q = self.writesql(delete(buttonseries).where(buttonseries.assignname == current_assignname))
        if not q:
            self.alert(f"Error deleting buttonseries on tab {current_tab} in form {current_form}")
            return
        #insert new buttonseries data

        for button_series in button_series_table_dict:
            button_series["formname"] = current_form
            q = self.writesql(insert(buttonseries).values(**button_series))
            if not q:
                self.alert(f"Error inserting buttonseries on tab {current_tab} in form {current_form}")
                return
        return current_tab, current_name
        
    def edit_sequence_save(self, buttons_table_dict, batchsequence_table_dict, button_series_table_dict):




        q = self.writesql(insert(buttons).values(**buttons_table_dict))
        if not q:
            self.alert(f"Error inserting button on tab {buttons_table_dict['tab']} in form {buttons_table_dict['formname']}")
            return
        q = self.writesql(insert(batchsequence).values(**batchsequence_table_dict))
        if not q:
            self.alert(f"Error inserting batchsequence on tab {batchsequence_table_dict['tab']} in form {batchsequence_table_dict['formname']}")
            return


        for button_series in button_series_table_dict:
            q = self.writesql(insert(buttonseries).values(**button_series))
            if not q:
                self.alert(f"Error inserting buttonseries on tab {button_series['tab']} in form {button_series['formname']}")
                return

    def edit_sequence_delete(self, data_dict):
        button_name = data_dict["current_button"]["buttonname"]
        tab_name = data_dict["current_button"]["tab"]
        form_name = data_dict["current_button"]["formname"]

        assignname = data_dict["current_batch"]["source"]

        q = self.writesql(delete(buttons).where(buttons.buttonname == button_name).where(buttons.tab == tab_name).where(buttons.formname == form_name))
        if not q:
            self.alert(f"Error deleting button on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(batchsequence).where(batchsequence.buttonname == button_name).where(batchsequence.tab == tab_name).where(batchsequence.formname == form_name))
        if not q:
            self.alert(f"Error deleting batchsequence on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(buttonseries).where(buttonseries.formname == form_name).where(buttonseries.assignname == assignname))
        if not q:
            self.alert(f"Error deleting buttonseries on tab {tab_name} in form {form_name}")
            return
