import customtkinter as CTk

from ActionDataBase import ActionDataBase


class UpdateOptionMenu:
    def __init__(self, master, database: ActionDataBase):
        self.database = database

        self.optionmenu = CTk.CTkOptionMenu(master=master,
                                            values=database.table_names,
                                            command=self.show_names)
        self.optionmenu.grid(row=4, column=4, columnspan=1)

        self.scrollbar_frame = CTk.CTkScrollableFrame(master=master, width=300)
        self.scrollbar_frame.grid(row=4, column=5, columnspan=2)

        self.labels = []
        self.entries = []
        self.button = None

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
        self.show_update_button()

    def show_update_button(self) -> None:
        self.button = CTk.CTkButton(master=self.scrollbar_frame, text="Изменить", width=200, command=self.update)
        self.button.grid(row=len(self.labels), column=0, columnspan=2, pady=2, sticky="nsew")

    def update(self) -> None:
        table = self.optionmenu.get()

        values = []

        for i, entry in enumerate(self.entries):
            if entry.get() == "":
                values.append(None)
            else:
                values.append(entry.get())

        self.database.update_row(table, [label.cget("text") for label in self.labels], values)
        for entry in self.entries:
            entry.delete(0, len(entry.get()))

    def clear_lists(self) -> None:
        for label in self.labels:
            label.destroy()
        self.labels.clear()

        for entry in self.entries:
            entry.destroy()
        self.entries.clear()

        if self.button is not None:
            self.button.destroy()
            self.button = None
