import customtkinter as CTk

from ActionDataBase import ActionDataBase


class FilterByValueOptionMenu:
    def __init__(self, master, database: ActionDataBase):
        self.database = database

        self.optionmenu = CTk.CTkOptionMenu(master=master,
                                            values=database.table_names,
                                            command=self.show_names)
        self.optionmenu.grid(row=4, column=0, columnspan=1)

        self.scrollbar_frame = CTk.CTkScrollableFrame(master=master, width=300)
        self.scrollbar_frame.grid(row=4, column=1, columnspan=2)

        self.labels = []
        self.entries = []

    def show_names(self, table_name: str) -> None:
        self.clear_lists()
        for i, name in enumerate(self.database.get_columns_name(table_name)):
            label = CTk.CTkLabel(master=self.scrollbar_frame, text=name)
            label.grid(row=i, column=0, sticky="nsew")
            self.labels.append(label)
        self.show_entry(table_name)

    def show_entry(self, table_name: str) -> None:
        for i, name in enumerate(self.database.get_columns_name(table_name)):
            entry = CTk.CTkEntry(master=self.scrollbar_frame, width=200)
            entry.grid(row=i, column=1, sticky="nsew", pady=2, padx=2)
            self.entries.append(entry)
        self.scrollbar_frame.configure(
            width=(self.entries[0].cget("width") + len(max(label.cget("text") for label in self.labels) * 9) + 35))

    def get_table_and_values(self) -> list[str, list]:
        table = self.optionmenu.get()
        values = []
        key = False
        for i, entry in enumerate(self.entries):
            if entry.get() != "":
                key = True
                values.append([self.labels[i].cget("text"), entry.get()])
        if not key:
            return [None, None]
        return [table, values]

    def clear_lists(self) -> None:
        for label in self.labels:
            label.destroy()
        self.labels.clear()

        for entry in self.entries:
            entry.destroy()
        self.entries.clear()
