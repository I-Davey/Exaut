from functools import partial
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
#import QCursor
from PyQt6.QtGui import QCursor
import sys


from .TypeManager.Types_handler import TypeManager, Types

import sys
from PyQt6.QtWidgets import (QPushButton, QDialog, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout,
                             QHBoxLayout, QFrame, QLabel,
                             QApplication, QWidget)

class SectionExpandButton(QPushButton):
    """a QPushbutton that can expand or collapse its section
    """
    def __init__(self, item, text = "", parent = None):
        super().__init__(text, parent)
        self.section = item
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        """toggle expand/collapse of section by clicking
        """
        if self.section.isExpanded():
            self.section.setExpanded(False)
        else:
            self.section.setExpanded(True)


class CollapsibleDialog(QDialog):
    """a dialog to which collapsible sections can be added;
    subclass and reimplement define_sections() to define sections and
        add them as (title, widget) tuples to self.sections
    """
    def __init__(self, get_actions, handle_action_types, handle_select_category, parent = None):
        super().__init__(parent)
        self.handle_type_cat = handle_select_category
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.setIndentation(0)
        self.cats = {}
        self.items ={}
        self.get_actions = get_actions
        self.cats = self.get_actions()
        self.handle_action_types = handle_action_types
        self.sections = []
        self.isexpanded = False
        self.handle_categories()
        self.define_sections()
        self.add_sections()
        #self.tree.itemClicked.connect(partial(handle_action_types, self.items))
        self.tree.itemClicked.connect(partial( self.handle_action_types, self.items))

    def expand(self, *args):
        self.tree.expandAll()
        self.isexpanded = True
    
    def collapse(self, *args):
        self.tree.collapseAll()
        self.isexpanded = False

    def handle_refresh(self):
        """
        handles the refresh action
        """
        #dlete all qtreewidgets in self.tree
        self.sections.clear()
        print("Clearing")
        self.tree.clear()
        print("Cleared")
        self.handle_categories(self.get_actions())
        self.add_sections()
        if self.isexpanded:
            self.tree.expandAll()

        print("Done")



    def add_sections(self):
        """adds a collapsible sections for every 
        (title:str, widget:list) tuple in self.sections
        """
        for (title, widgets) in self.sections:
            button1 = self.add_button(title)
            for widget in widgets:
                
                section1 = self.add_widget(button1, widget[0])
                self.items[str(section1)] = widget[1]
 
                button1.addChild(section1)

    def define_sections(self):
        """reimplement this to define all your sections
        and add them as (title, widget) tuples to self.sections
        """
        return
        widget = QFrame(self.tree)
        layout = QHBoxLayout(widget)
        layout.addWidget(QLabel("Bla"))
        layout.addWidget(QLabel("Blaa"))
        title = "Section 1"
        self.sections.append((title, [widget]))

    def add_button(self, title):
        """creates a QTreeWidgetItem containing a button 
        to expand or collapse its section
        """
        item = QTreeWidgetItem()
        self.tree.addTopLevelItem(item)
        self.tree.setItemWidget(item, 0, SectionExpandButton(item, text = title))
        return item

    def add_widget(self, button, widget):
        """creates a QWidgetItem containing the widget,
        as child of the button-QWidgetItem
        """
        section = QTreeWidgetItem(button)
        section.setDisabled(False)
        #handle Sectopm Click
        
        self.tree.setItemWidget(section, 0, widget)
        return section


    def handle_filter(self, word:str):
        word = word.lower()
        all= self.get_actions()
        for category, items in all.items():
            for name in items.copy():
                if word not in name.lower():
                    #delete item
                    del[all[category][name]]
        for category, items in all.copy().items():
            if len(items) == 0:
                del all[category]
        self.sections.clear()
        self.tree.clear()
        self.handle_categories(all)
        self.add_sections()
        if self.isexpanded:
            self.tree.expandAll()


    def handle_categories(self, cats = None):
        """
        loads all the categories from the json arr and adds them to the tree
        """

        if cats is not None:
            self.cats = cats

        json_cats = self.cats
        for category, items in json_cats.items():
            if category is None:
                category = "<Uncategorized>"
            if items not in (None, {}):
                widgets = []
                for  key, value in items.items():
                    widget = QFrame(self.tree)
                    #addd contextmenu rightclick
                    widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                    widget.customContextMenuRequested.connect(partial(self.handle_contextmenu, key, value))

                    
                    layout = QHBoxLayout(widget)
                    layout.addWidget(QLabel(key))
                    widget.setLayout(layout)
                    widgets.append((widget, key))
                self.sections.append((category, widgets))

    

    def handle_contextmenu(self, key, value):
        #popup context menu with open: select category
        menu = QMenu()
        select_cat = menu.addAction("Select Category")
        #get category from key
        
        select_cat.triggered.connect(partial(self.handle_type_cat, key, value))
        menu.exec(QCursor.pos())



class Actions(QMainWindow):
    def __init__(self, formname, tabname, actions, get_actions, action_save, action_update, action_delete, parent_=None):

        
        super().__init__(parent_)



        
        self.save = action_save
        self.update_action = action_update
        self.delete_action = action_delete
        self.formname = formname
        self.tabname = tabname
        self.return_categories = actions.return_categories
        self.action_change_category = actions.edit_action_category

        self.data = Data(actions.return_plugins_type_map, actions.return_actions_categories_dict, actions.get_type_plugin_map)


        self.parent_ = parent_

        self.variables = self.parent_.api.var_dict
        # set the title of main window

        # set the size of window
        self.Width = 800
        self.height = int(0.618 * self.Width)
        self.resize(self.Width, self.height)
        self.labels = []

        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText('Search')
        self.searchbar.setStyleSheet('''QLineEdit{ border: 1px solid gray; border-radius: 5px; padding: 0px; background: white; }''')
    
        self.categories  = CollapsibleDialog(actions.return_actions_categories_dict, self.handle_action_types, self.handle_select_category)
        self.searchbar.textChanged.connect(self.categories.handle_filter)


        #self.categories.handle_refresh()
        #set categories to expanding
        #fill layout with categories
        self.object_vertical_layout = QVBoxLayout()
        #add padding to object_vertical_layout top
        self.object_vertical_layout.setContentsMargins(0, int(self.height * 0.098), 0, 0)
        #make all closew to gether in middle
        self.object_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.save_button = QPushButton("Save")
        
        #lambda function to set self.mode to "save"
                
        self.save_button.clicked.connect(partial(self.setmode, "save"))
        self.save_button.clicked.connect(self.check_data)

        self.edit_button = QPushButton("Update")
        self.edit_button.clicked.connect(partial(self.setmode, "edit"))
        self.edit_button.clicked.connect(self.check_data)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(partial(self.setmode, "delete"))
        self.delete_button.clicked.connect(self.check_data)
        
        self.save_button.hide()
        self.edit_button.hide()
        self.delete_button.hide()

        self.initUI()

    def refresh_vars(self):
        self.variables = self.parent_.api.var_dict

    def setmode(self, mode):
        self.mode = mode 

    def initUI(self):
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.searchbar)
        #left_layout.addWidget(self.categories)
        layout_parent = QVBoxLayout()
        ###
        #layout_parent.addLayout(left_layout)
        self.pyqt_components_map = []
        layout_parent.addWidget(self.categories)
        

        #fill whole area with left_layout
        left_layout.setSpacing(20)
        #maxwidth 
        left_widget = QWidget()
        left_widget.setLayout(layout_parent)
        left_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.right_widget = QGridLayout()
        refresh_cats = QPushButton("R")
        refresh_cats.clicked.connect(self.categories.handle_refresh)
        refresh_cats.clicked.connect(self.refresh_vars)
        refresh_cats.setToolTip("Refresh Categories")

        expand_all = QPushButton("+")
        expand_all.clicked.connect(self.categories.expand)
        expand_all.setToolTip("Expand all categories")


        collapse_all = QPushButton("-")
        collapse_all.clicked.connect(self.categories.collapse)

        collapse_all.setToolTip("Collapse all categories")
        #make collaps fit to the text
        expand_all.setFixedWidth(int(self.Width * 0.05))
        collapse_all.setFixedWidth(int(self.Width * 0.05))
        refresh_cats.setFixedWidth(int(self.Width * 0.05))


        self.left_items = QHBoxLayout()
        self.left_items.addWidget(refresh_cats)
        self.left_items.addWidget(expand_all)
        self.left_items.addWidget(collapse_all)

        self.left_qvbox = QVBoxLayout()
        self.left_qvbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.left_qvbox.addLayout(self.left_items)
        self.left_qvbox.addWidget(self.searchbar)
        self.left_qvbox.addWidget(left_widget)
        self.left_qvbox.addWidget(QLabel("TAB: " + self.tabname))
        #set max width qvbox

        self.right_items = QVBoxLayout()
        right_items_right = QHBoxLayout()
        right_items_right.addWidget(self.save_button)
        right_items_right.addWidget(self.edit_button)
        right_items_right.addWidget(self.delete_button)
        self.right_items.addLayout(right_items_right)

        self.right_items.addLayout(self.object_vertical_layout)

        self.right_widget.addLayout(self.right_items, 0, 0)

        main_layout = QHBoxLayout()
        
        main_layout.addLayout(self.left_qvbox)
        main_layout.addLayout(self.right_widget)
        main_layout.setStretch(0, 80)
        main_layout.setStretch(1, 200)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


    def clear_rightwidget(self):
        for item, name, optional, dict in self.pyqt_components_map:
            item.setParent(None)
            item.deleteLater()
        for item in self.labels:
            item.setParent(None)
            item.deleteLater()
        self.labels = []
        self.pyqt_components_map = []
        self.save_button.hide()

    def handle_action_types(self, items, action):

        self.clear_rightwidget()
        self.chosen_action = action

        button_layout = QHBoxLayout()
        button_label = QLabel("enter button name")
        button_textbox = QLineEdit()
        button_textbox.setPlaceholderText("button name")
        button_layout.addWidget(button_label)
        button_layout.addWidget(button_textbox)
        self.object_vertical_layout.addLayout(button_layout)
        self.pyqt_components_map.append((button_textbox, "button_name", False, None))
        self.labels.append(button_label)

        description_layout = QHBoxLayout()
        button_description = QLabel("(Optional) enter button description")
        button_description_textbox = QLineEdit()
        button_description_textbox.setPlaceholderText("button description")
        description_layout.addWidget(button_description)
        description_layout.addWidget(button_description_textbox)
        self.object_vertical_layout.addLayout(description_layout)
        self.pyqt_components_map.append((button_description_textbox, "button_description", True, None))
        self.labels.append(button_description)
        
        all_info = self.data.handle_action_types(items, action)
        if all_info[0]:
            for item in all_info[1]:
                pyqt_object = item[0]["type"]
                #if pyqt object is a layout
                if pyqt_object.isWidgetType():
                    if item[0]["optional"]:
                        item[0]["description"] = "(Optional) " + item[0]["description"]

                    label = QLabel(item[0]["description"])
                    layout = QHBoxLayout()
                    layout.addWidget(label)
                    layout.addWidget(pyqt_object)
                    self.object_vertical_layout.addLayout(layout)
                    self.pyqt_components_map.append((pyqt_object, item[1], item[0]["optional"], item))
                    self.labels.append(label)
                else:
                    #get widget at point 0 in item:QLayout
                    widget = item[0]["type"].itemAt(0).widget()
                    widget2 = item[0]["type"].itemAt(1).widget()
                    self.labels.append(widget)
                    self.labels.append(widget2)
                    
                    self.object_vertical_layout.addLayout(pyqt_object)
                    self.pyqt_components_map.append((pyqt_object, item[1], item[0]["optional"], item))
        self.delete_button.hide()
        self.edit_button.hide()
        self.save_button.show()

    def handle_select_category(self, key, value):
        #new popup window
        categories = self.return_categories()
        #popup with dropdown list of categories
        
        selection_text = QLabel("Select a category")
        selection_box = QComboBox()
        selection_box.addItems(categories)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.handle_select_category_ok(key, selection_box.currentText()))
        #dialog box
        dialog = QDialog(self)
        dialog.setWindowTitle("Select a category")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(selection_text)
        dialog.layout().addWidget(selection_box)
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(dialog.close)

        dialog.exec()

    def handle_select_category_ok(self, key, category):
        print("category changed")
        self.action_change_category(key, category)
        self.categories.handle_refresh()

    def check_data(self):
        fail = False
        for item in self.pyqt_components_map:
            if item[3]:
                if not item[3][0]["callback"].validate_result():
                    fail = True
            else:
                x = item[0].text()
                if not item[0].text() and not item[2]:
                    item[0].setStyleSheet("background-color: red")
                    fail = True
                else:
                    item[0].setStyleSheet("background-color: None")
        if fail:
            return False
        else:
            self.handle_save()

    def handle_save(self):
        newmap = {}
        for item in self.pyqt_components_map:
            if item[1] in ("button_name", "button_description"):
                newmap[item[1]] = item[0].text()
            else:
                newmap[item[1]] = item[3][0]["callback"].data
        
        both_value_dict = {"formname": self.formname, "tab": self.tabname, "buttonname": newmap["button_name"]}

        button_value_dict = {}
        button_value_dict.update(both_value_dict)

        button_value_dict["buttonsequence"] = "0"
        button_value_dict["columnnum"] = "0"
        button_value_dict["buttondesc"] = newmap["button_description"]
        self.save_button.hide()
        self.edit_button.show()
        self.delete_button.show()



        del[newmap["button_name"]]
        del[newmap["button_description"]]
        batchsequence_value_dict = {"runsequence":0}
        batchsequence_value_dict.update(both_value_dict)

        for item in newmap:
            batchsequence_value_dict[item] = newmap[item]
        if self.mode == "edit":
            temp_batchsequence_value_dict = self.temp_data[0]
            temp_button_value_dict = self.temp_data[1]
            #delete from buttons dict 
            self.update_action(temp_batchsequence_value_dict, temp_button_value_dict,batchsequence_value_dict, button_value_dict, self.data.chosen_action)
            self.temp_data = batchsequence_value_dict, button_value_dict, self.data.chosen_action
        elif self.mode == "save":
            self.temp_data = batchsequence_value_dict, button_value_dict, self.data.chosen_action
            self.save(button_value_dict, batchsequence_value_dict, self.data.chosen_action)
        elif self.mode == "delete":
            temp_button_value_dict = self.temp_data[1]
            self.delete_action(temp_button_value_dict["formname"], temp_button_value_dict["tab"],temp_button_value_dict["buttonname"])
            self.save_button.show()
            self.delete_button.hide()
            self.edit_button.hide()
        

 
class Data:
    def __init__(self, get_pluginmap, get_actions, get_typemap):
        self.get_pluginmap = get_pluginmap
        self.get_actions = get_actions
        self.get_typemap = get_typemap
        self.pluginmap = self.get_pluginmap()
        self.actions = self.get_actions()
        self.typemap = self.get_typemap()
        self.typemgr = Types()

    def handle_action_types(self, items, action:QTreeWidgetItem):
        #get first child of action
        action = items[str(action)]
        self.chosen_action = action
        """
        returns the type of the action
        """
        data = self.get_pluginmap()
        types = {}
        typemap = self.get_typemap()
        for item, value in data.items():
            if type(typemap[action]) in (list, tuple):
                if item == typemap[action][0]:
                    types = value
            else:
                if item == typemap[action]:
                    types = value
        if types == {}:
            return False, f"No types found for {action}"
        widgets = []

        for key, value in types.items():
            if type(value) is dict:
                type_type = value["type"]
                type_description = value["description"]
                type_args = value["args"] if "args" in value else None
                optional = value["optional"] if "optional" in value else None
            else:
                type_type  = value[0]
                type_description = value[1]
                type_args = value[2] if len(value) > 2 else None
                optional = value[3] if len(value) > 3 else False
            type_data = {"type": type_type, "description": type_description, "args": type_args, "optional": optional}

            if not self.typemgr.exists(type_type):
                return False, f"Type {type_type} does not exist"
            required_params = self.typemgr.getparams(type_type)
            param_list = []

            if required_params is not None:
                for param in required_params:
                    param_list.append(type_data[param])
            callback_, gen_object = self.typemgr.create(type_type,  *param_list, db_key=key)



            if gen_object is not None:
                #if gen_object is iterable
                if isinstance(gen_object, tuple):
                    print("list")
                    type_data["description"] = gen_object[0]
                    type_data["type"] = gen_object[1]
                    type_data["callback"] = callback_

                else:
                    type_data["type"] = gen_object
                    type_data["callback"] = callback_
                widgets.append((type_data, key))
        return(True, widgets)

            
            
    






    

