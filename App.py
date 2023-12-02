import customtkinter as CTk
from ActionDataBase import ActionDataBase
from AddOptionMenu import AddOptionMenu
from DeleteOptionMenu import DeleteOptionMenu
from FilterByValueOptionMenu import FilterByValueOptionMenu
from FuncOptionMenu import FuncOptionMenu
from ProcOptionMenu import ProcOptionMenu
from TabView import TabView
from ScrollBarHorizontal import ScrollBar
from UpdateOptionMenu import UpdateOptionMenu


class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1500x750")
        self.title("Basic Database Interface")
        self.resizable(True, True)

        self.myDB = ActionDataBase()

        self.tab_view = TabView(master=self)
        self.tab_view.grid(row=0, column=0, padx=0, pady=0, columnspan=2, sticky="nsw")

        self.btn_select_all = CTk.CTkButton(master=self,
                                            text="select selected",
                                            width=150,
                                            command=self.show_buttons)
        self.btn_select_all.grid(row=1, column=0)

        self.btn_deselect_checkboxes = CTk.CTkButton(master=self,
                                                     text="Clear",
                                                     width=150,
                                                     command=self.clear_checkboxes)
        self.btn_deselect_checkboxes.grid(row=1, column=1)

        self.scrollbar = ScrollBar(master=self, orientation="horizontal")
        self.scrollbar.grid(row=2, column=0, columnspan=3)

        self.option_menu = AddOptionMenu(self, self.myDB)
        self.delete_option_menu = DeleteOptionMenu(self, self.myDB)
        self.update_option_menu = UpdateOptionMenu(self, self.myDB)
        self.filter_option_menu = FilterByValueOptionMenu(self, self.myDB)
        self.myDB.filter_value = self.filter_option_menu
        self.func_optionmenu = FuncOptionMenu(self, self.myDB)
        self.proc_optionmenu = ProcOptionMenu(self, self.myDB)

    def show_buttons(self) -> None:
        self.scrollbar.scrollbar.show_buttons(self.tab_view, self.myDB)

    def clear_checkboxes(self) -> None:
        self.tab_view.clear_checkbox()
