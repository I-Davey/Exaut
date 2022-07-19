from .db.Exaut_sql import  *
from sqlalchemy import select, update, delete

class Edit_Button:
    def __init__(self, readsql, writesql, logger,  alert, title, edit_sequence_data):
        self.readsql = readsql
        self.writesql = writesql
        self.logger = logger
        self.alert = alert
        self.title = title
        self.edit_sequence_data = edit_sequence_data
    def edit_button_data(self, button_name, tab_name):
        self.logger.info(f"Constructing data for edit button {button_name} on tab {tab_name} in form {self.title}")
        button_data = self.readsql(select("*").where(buttons.buttonname == button_name).where(buttons.tab == tab_name).where(buttons.formname == self.title), one=True)
        batchsequence_data = self.readsql(select("*").where(batchsequence.buttonname == button_name).where(batchsequence.tab == tab_name).where(batchsequence.formname == self.title))
        #if batchsequence_data None:
        form_data = self.readsql(select(forms.formname).order_by(forms.formname.asc()))
        tab_data = self.readsql(select(tabs.formname, tabs.tab).where(tabs.formname.in_([form.formname for form in form_data])).order_by(tabs.formname.asc(), tabs.tabsequence.asc()))

        dict_struct = {}
        dict_struct["button_data"]        = dict(button_data._mapping)
        dict_struct["batchsequence_data"] = [dict(item._mapping) for item in batchsequence_data] 
        dict_struct["form_data"]          = [dict(item._mapping) for item in form_data]
        dict_struct["tab_data"]           = [dict(item._mapping) for item in tab_data]

        if len(batchsequence_data) == 0:
            self.logger.warning(f"No batchsequence data found for button: {button_name} on tab: {tab_name} in form: {self.title}")
            return(dict_struct, False)
            
        if batchsequence_data[0].type == "assignseries":
            sequence_data, state = self.edit_sequence_data(button_name, tab_name, batchsequence_data[0].source)
            if not state:
                self.alert(F"No assignseries data found for {button_name} on tab {tab_name} in form {self.title}")
            sequence_data["current_batch"] = dict_struct["batchsequence_data"][0]
            dict_struct = {"edit": dict_struct, "sequence": sequence_data}
        else:
            state = "button"

        return dict_struct, state

    def edit_button_update(self, original_data : dict, batchsequence_new : dict, button_new : dict):
        if "edit" in original_data:
            original_data = original_data["edit"]
        button = original_data["button_data"]
        q = self.writesql(update(buttons).where(buttons.buttonname == button["buttonname"]).where(buttons.tab == button["tab"]).where(buttons.formname == self.title).values(**button_new))
        if not q:
            self.alert(f"Error updating button {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return
        q = self.writesql(update(batchsequence).where(batchsequence.buttonname == button["buttonname"]).where(batchsequence.tab == button["tab"]).where(batchsequence.formname == self.title).values(**batchsequence_new))
        if not q:
            self.alert(f"Error updating batchsequence {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return

        q = self.writesql(update(buttonseries).where(buttonseries.buttonname == button["buttonname"]).where(buttonseries.tab == button["tab"]).where(buttonseries.formname == self.title).values(buttonname = button_new["buttonname"],tab = button_new["tab"],formname = button_new["formname"]))
        if not q:
            self.alert(f"Error updating buttonseries {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return

        return button["tab"], button["buttonname"]
    
    def edit_button_delete(self, data : dict):
        if "edit" in data:
            data = data["edit"]
        button = data["button_data"]

        q = self.writesql(delete(buttons).where(buttons.buttonname == button["buttonname"]).where(buttons.tab == button["tab"]).where(buttons.formname == self.title))
        if not q:
            self.alert(f"Error deleting button {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return
        
        q = self.writesql(delete(batchsequence).where(batchsequence.buttonname == button["buttonname"]).where(batchsequence.tab == button["tab"]).where(batchsequence.formname == self.title))
        if not q:
            self.alert(f"Error deleting batchsequence {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return
        
        q = self.writesql(delete(buttonseries).where(buttonseries.buttonname == button["buttonname"]).where(buttonseries.tab == button["tab"]).where(buttonseries.formname == self.title))
        if not q:
            self.alert(f"Error deleting buttonseries {button['buttonname']} on tab {button['tab']} in form {self.title}")
            return

