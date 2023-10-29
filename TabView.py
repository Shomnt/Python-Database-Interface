import customtkinter as CTk
from ActionDataBase import ActionDataBase


class TabView(CTk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.active_table_names = []
        self.active_column_names = []
        self.mydb = ActionDataBase()

        self.table_names = self.mydb.get_tables_name()
        self.all_check_box = []

        for table in self.table_names:
            table_name = table
            table_name = table_name.replace("_", " ")
            table_name = table_name.replace(table_name[0], table_name[0].upper(), 1)
            self.add(table_name)

            checkbox_list = []

            for i, column in enumerate(self.mydb.get_columns_name(table)):
                column = column.replace("_", " ")
                column = column.replace(column[0], column[0].upper(), 1)
                checkbox = CTk.CTkCheckBox(master=self.tab(table_name), text=column)
                checkbox.grid(row=len(checkbox_list) % 5,
                              column=len(checkbox_list) // 5,
                              padx=(0, 0),
                              pady=(0, 10),
                              sticky="nsew")
                checkbox_list.append(checkbox)

            self.all_check_box.append(checkbox_list)

    def get_checked_items(self) -> list[str]:
        self.active_column_names = []
        for i, table_name in enumerate(self.table_names):
            for checkbox in self.all_check_box[i]:
                if checkbox.get() == 1:
                    column_name = checkbox.cget("text")
                    column_name = column_name.replace(" ", "_")
                    column_name = column_name.replace(column_name[0], column_name[0].lower(), 1)
                    self.active_column_names.append(table_name + "." + column_name)
        return self.active_column_names

    def get_active_table(self) -> list[str]:
        self.active_table_names = []
        for i in self.active_column_names:
            t = i.split(".")[0]
            if t not in self.active_table_names:
                self.active_table_names.append(t)
        return self.active_table_names

    def clear_checkbox(self) -> None:
        for checkboxes in self.all_check_box:
            for checkbox in checkboxes:
                checkbox.deselect()
