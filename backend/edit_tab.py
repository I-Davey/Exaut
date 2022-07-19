from .db.Exaut_sql import  *
from sqlalchemy import select, update, delete

class Edit_Tab:
    def __init__(self, writesql, logger):
        self.writesql = writesql
        self.logger = logger
        pass

    def edit_tab_delete(self, tab_name, form_name):
        print(tab_name)
        print(form_name)
        q = self.writesql(delete(tabs).where(tabs.tab == tab_name).where(tabs.formname == form_name))
        if not q:
            self.alert(f"Error deleting tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(buttons).where(buttons.tab == tab_name).where(buttons.formname == form_name))
        if not q:
            self.alert(f"Error deleting buttons on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(batchsequence).where(batchsequence.tab == tab_name).where(batchsequence.formname == form_name))
        if not q:
            self.alert(f"Error deleting batchsequence on tab {tab_name} in form {form_name}")
            return
        q = self.writesql(delete(buttonseries).where(buttonseries.tab == tab_name).where(buttonseries.formname == form_name))
        if not q:
            self.alert(f"Error deleting buttonseries on tab {tab_name} in form {form_name}")
            return

    def edit_tab_update(self, tab_name, form_name, data):
        new_tab_name = data["tab"]
        q = self.writesql(update(tabs).where(tabs.tab == tab_name).where(tabs.formname == form_name).values(**data))
        if not q:
            self.alert(f"Error updating tab {tab_name} in form {form_name}")
            return
        q = self.writesql(update(buttons).where(buttons.tab == tab_name).where(buttons.formname == form_name).values(**{"tab": new_tab_name}))
        if not q:
            self.alert(f"Error updating buttons on tab {tab_name} in form {form_name}")
            return

        q = self.writesql(update(batchsequence).where(batchsequence.tab == tab_name).where(batchsequence.formname == form_name).values(**{"tab": new_tab_name}))
        if not q:
            self.alert(f"Error updating batchsequence on tab {tab_name} in form {form_name}")
            return

        q = self.writesql(update(buttonseries).where(buttonseries.tab == tab_name).where(buttonseries.formname == form_name).values(**{"tab": new_tab_name}))
        if not q:
            self.alert(f"Error updating buttonseries on tab {tab_name} in form {form_name}")
            return
