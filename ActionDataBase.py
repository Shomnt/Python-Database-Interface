import ast

from mysql.connector import connect


class ActionDataBase:
    def __init__(self):
        user = "Your login"
        password = "Your password"
        self.database = "Your database name"

        self.mydb = connect(
            host="localhost",
            user=user,
            password=password,
            database=self.database,
        )
        self.cursor = self.mydb.cursor()
        self.table_names, self.dependencies = self.get_relations_dict()
        self.filter_value = None

    def insert_row(self, table_name: str, columns: list[str], values: list) -> None:
        command = (f"INSERT INTO {table_name} "
                   f"({', '.join(columns)}) "
                   f"VALUES ({', '.join(['%s' for _ in range(len(values))])}) ")

        self.cursor.executemany(command, [tuple(values)])
        self.mydb.commit()

    def update_row(self, table_name: str, columns: list[str], values: list) -> None:
        not_none_val = []
        command = f"UPDATE {table_name} SET "
        for i, column in enumerate(columns):
            if values[i] is not None:
                command += f"{column}=%s, "
                not_none_val.append(values[i])
        command = command[:-2]
        command += " WHERE "
        for key in self.get_primary_key(table_name):
            command += f"{key}={values[columns.index(key)]} AND "
        command = command[:-4]
        self.cursor.executemany(command, [tuple(not_none_val)])
        self.mydb.commit()

    def delete_row(self, table_name: str, primary_keys: list, primary_key_values: list) -> None:
        command = (f"DELETE FROM {table_name} "
                   f"{self.delete_subcommand(primary_keys, primary_key_values)}")
        self.cursor.execute(command)
        self.mydb.commit()

    def delete_subcommand(self, primary_keys: list, primary_key_values: list) -> str:
        command = "WHERE "
        for i, primary_key in enumerate(primary_keys):
            command += f"{primary_key}={primary_key_values[i]}"
            if primary_key is not primary_keys[-1]:
                command += " AND "
        return command.strip()

    def get_tables_name(self) -> list[str]:
        command = f"SHOW TABLES"
        self.cursor.execute(command)
        return [str(table[0]) for table in self.cursor.fetchall()]

    def get_columns_name(self, table_name: str) -> list[str]:
        command = f"SHOW COLUMNS FROM {table_name}"
        self.cursor.execute(command)
        return [column[0] for column in self.cursor.fetchall()]

    def get_relations_information(self) -> list[tuple]:
        command = (f"SELECT TABLE_NAME, REFERENCED_TABLE_NAME, COLUMN_NAME, REFERENCED_COLUMN_NAME "
                   f"FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                   f"WHERE REFERENCED_TABLE_SCHEMA='{self.database}'")
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def get_not_null_information(self, table_name: str) -> list[bool]:
        command = f"DESCRIBE {table_name}"
        self.cursor.execute(command)
        can_null = []
        for row in self.cursor.fetchall():
            if row[2] == "NO":
                can_null.append(False)
            else:
                can_null.append(True)
        return can_null

    def get_type_information(self, table_name: str) -> list[str]:
        command = f"DESCRIBE {table_name}"
        self.cursor.execute(command)
        types = []
        for row in self.cursor.fetchall():
            types.append(row[1])
        return types

    def get_primary_key(self, table_name: str) -> list[str]:
        command = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'"
        self.cursor.execute(command)
        keys = []
        for row in self.cursor.fetchall():
            keys.append(row[4])
        return keys

    def get_func_names(self) -> list[str]:
        command = (f"SELECT ROUTINE_NAME "
                   f"FROM information_schema.routines "
                   f"WHERE ROUTINE_SCHEMA = '{self.database}' AND ROUTINE_TYPE = 'FUNCTION'")
        self.cursor.execute(command)
        names = []
        for row in self.cursor.fetchall():
            names.append(row[0])
        return names

    def get_proc_names(self) -> list[str]:
        command = (f"SELECT ROUTINE_NAME "
                   f"FROM information_schema.routines "
                   f"WHERE ROUTINE_SCHEMA = '{self.database}' AND ROUTINE_TYPE = 'PROCEDURE'")
        self.cursor.execute(command)
        names = []
        for row in self.cursor.fetchall():
            names.append(row[0])
        return names

    def get_input_information(self, name: str) -> list[str]:
        command = (f"SELECT PARAMETER_NAME "
                   f"FROM INFORMATION_SCHEMA.PARAMETERS "
                   f"WHERE SPECIFIC_SCHEMA = '{self.database}' AND SPECIFIC_NAME = '{name}' AND PARAMETER_MODE = 'IN'")
        self.cursor.execute(command)
        parametrs = []
        for row in self.cursor.fetchall():
            parametrs.append(row[0])
        return parametrs

    def get_count_out(self, name: str) -> int:
        command = (f"SELECT PARAMETER_NAME "
                   f"FROM INFORMATION_SCHEMA.PARAMETERS "
                   f"WHERE SPECIFIC_SCHEMA = '{self.database}' AND SPECIFIC_NAME = '{name}' AND PARAMETER_MODE = 'OUT'")
        self.cursor.execute(command)
        parametrs = []
        for row in self.cursor.fetchall():
            parametrs.append(row[0])
        return len(parametrs)

    def activate_procedure(self, proc_name: str, input_values: list) -> list:
        time = tuple(input_values)
        for _ in range(self.get_count_out(proc_name)):
            time = time + tuple([0])
        result = self.cursor.callproc(proc_name, time)
        print(list(result)[len(input_values):])
        return list(result)[len(input_values):]

    def activate_function(self, func_name: str, input_values: list) -> list:
        command = f"SELECT {self.database}.{func_name}({', '.join(['%s' for _ in range(len(input_values))])})"
        self.cursor.execute(command, tuple(input_values))
        answer = self.cursor.fetchall()
        print(answer)
        return list(answer)

    def select_columns(self, tables_list: list[str], columns_list: list[str], orderBy: str = None) -> list[tuple]:
        if not columns_list:
            return []

        way = self.get_full_way(tables_list)
        filter_table, filter_values = self.filter_value.get_table_and_values()

        subcommand = ""
        if not way:
            way.append(tables_list[0])
            if filter_table is not None and filter_table not in way:
                way.append(filter_table)
        else:
            if filter_table is not None and filter_table not in way:
                way.append(filter_table)
            subcommand = self.get_sub_command(way)

        if filter_table is not None:
            if subcommand == "":
                subcommand = "WHERE "
            else:
                subcommand += " AND "
            for par in filter_values:
                subcommand += f"{filter_table}.{par[0]} = '{par[1]}' AND "
            subcommand = subcommand[:-5]

        command = (f"SELECT {', '.join(map(str, columns_list))} "
                   f"FROM {', '.join(map(str, way))} "
                   f"{subcommand}")

        if orderBy is not None:
            command += f" ORDER BY {orderBy}"

        if filter_table is not None:
            self.cursor.execute(command)
            return self.cursor.fetchall()
        else:
            self.cursor.execute(command)
            return self.cursor.fetchall()

    def get_sub_command(self, way: list) -> str:
        sub_command = "WHERE "
        for i, table_one in enumerate(way):
            for table_two in way[(i+1):]:
                if table_two in self.dependencies[self.table_names.index(table_one)].keys():
                    relation = eval(self.dependencies[self.table_names.index(table_one)].get(table_two))
                    sub_command += f"{table_one}.{relation[0]} = {table_two}.{relation[1]} AND "
        return sub_command[:len(sub_command)-5]

    def get_relations_dict(self) -> tuple[list[str], list[dict]]:  # примерно 0 оптимизации, надо поправить
        data = self.get_relations_information()
        blanks = []
        blanks_name = []
        used_name = [data[0][0]]
        str_dict = '{'

        for row in data:
            if row[0] != used_name[-1]:
                blanks.append(str_dict)
                blanks_name.append(used_name[-1])
                str_dict = '{'
                used_name.append(row[0])
            if row[1] in blanks_name:
                blanks[blanks_name.index(row[1])] += f'"{row[0]}" : "{[row[3], row[2]]}", '
            str_dict += f'"{row[1]}" : "{[row[2], row[3]]}", '
            if row is data[-1]:
                blanks.append(str_dict)
                blanks_name.append(used_name[-1])
                str_dict = '{'
                used_name.append(row[0])

        second_used_name = []

        data.sort(reverse=False, key=lambda row: row[1])

        for row in data:
            if row[1] in used_name:
                continue
            if len(second_used_name) == 0:
                second_used_name.append(row[1])
            if row[1] != second_used_name[-1]:
                blanks.append(str_dict)
                blanks_name.append(second_used_name[-1])
                str_dict = '{'
                second_used_name.append(row[1])
            str_dict += f'"{row[0]}" : "{[row[3], row[2]]}", '
            if row is data[-1]:
                blanks.append(str_dict)
                blanks_name.append(second_used_name[-1])
                str_dict = '{'
                second_used_name.append(row[1])

        for i, blank in enumerate(blanks):
            blanks[i] = ast.literal_eval(blank + '}')

        return blanks_name, blanks

    def get_way(self, start: str, target: str, used: list) -> list[str]:
        way = []
        used.append(start)

        if target in self.dependencies[self.table_names.index(start)].keys():
            return [start, target]

        for key in self.dependencies[self.table_names.index(start)].keys():
            if key not in used:
                way = [start]
                way += self.get_way(key, target, used)
                if target in way:
                    break

        return way

    def get_full_way(self, tables_list: list[str]) -> list[str]:
        full_way = []
        for i, table_one in enumerate(tables_list):
            for table_two in tables_list[(i + 1):]:
                if all(ele in full_way for ele in tables_list):
                    break
                time = self.get_way(table_one, table_two, used=[])
                full_way = full_way + time
                full_way = list(set(full_way))

        return full_way
