import customtkinter as CTk
from ActionDataBase import ActionDataBase
from TabView import TabView
from ScrollBarHorizontal import ScrollBar


class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1200x600")
        self.title("Basic Database Interface")
        self.resizable(False, True)

        self.myDB = ActionDataBase()

        self.tab_view = TabView(master=self)
        self.tab_view.grid(row=0, column=0, padx=0, pady=0, columnspan=2, sticky="nsew")

        self.btn_select_all = CTk.CTkButton(master=self,
                                            text="select selected",
                                            width=100,
                                            command=self.show_buttons)
        self.btn_select_all.grid(row=1, column=0)

        self.btn_deselect_checkboxes = CTk.CTkButton(master=self,
                                                     text="Clear",
                                                     width=100,
                                                     command=self.clear_checkboxes)
        self.btn_deselect_checkboxes.grid(row=1, column=1)

        self.scrollbar = ScrollBar(master=self, orientation="horizontal")
        self.scrollbar.grid(row=2, column=0)

    def show_buttons(self) -> None:
        self.scrollbar.scrollbar.show_buttons(self.tab_view, self.myDB)

    def clear_checkboxes(self) -> None:
        self.tab_view.clear_checkbox()
