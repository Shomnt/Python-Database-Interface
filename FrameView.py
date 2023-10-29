import customtkinter as CTk
from functools import partial

from ActionDataBase import ActionDataBase
from TabView import TabView


class FrameView(CTk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.buttons = []
        self.data_labels = []

    def show_buttons(self, tab_view: TabView, myDB: ActionDataBase) -> None:
        self.clear_buttons()
        for i, table in enumerate(tab_view.get_checked_items()):
            button = CTk.CTkButton(master=self, text=table, width=50)
            button.configure(
                command=partial(self.show_data,
                                myDB.select_columns(
                                    tab_view.get_active_table(),
                                    tab_view.get_checked_items(),
                                    table
                                )))
            self.buttons.append(button)
            button.grid(row=0, column=i, sticky="nsew")
        self.show_data((myDB.select_columns(tab_view.get_active_table(), tab_view.get_checked_items())))

    def show_data(self, rows: list[tuple]) -> None:
        self.clear_labels()
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                label = CTk.CTkLabel(master=self, text=value, width=50)
                self.data_labels.append(label)
                label.grid(row=(i + 1), column=j)

    def clear_labels(self) -> None:
        for label in self.data_labels:
            label.destroy()
        self.data_labels.clear()

    def clear_buttons(self) -> None:
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()