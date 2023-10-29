import ast

from mysql.connector import connect


class ActionDataBase:
    def __init__(self):
        user = "root"
        password = "20034567iI"
        self.database = "доставка"

        self.mydb = connect(
            host="localhost",
            user=user,
            password=password,
            database=self.database,
        )
        self.cursor = self.mydb.cursor()
        self.table_names, self.dependencies = self.get_relations_dict()

    def select_all(self, table_name: str, filters: list[str] = None, orderBy: str = None) -> list[tuple]:
        command = (f"SELECT * "
                   f"FROM {table_name}")

        if filters is not None:
            command += f" WHERE {' AND '.join(filters)}"

        if orderBy is not None:
            command += f" ORDER BY {orderBy}"

        self.cursor.execute(command)
        return list(self.cursor.fetchall())

    def insert_all(self, table_name: str, values: list) -> None:
        command = (f"INSERT INTO {table_name} "
                   f"VALUES ({', '.join(map(str, values))})")
        self.cursor.execute(command)
        self.mydb.commit()

    def insert_columns(self, table_name: str, columns: list[str], values: list) -> None:
        command = (f"INSERT INTO {table_name} "
                   f"({', '.join(columns)})"
                   f"VALUES ({', '.join(map(str, values))})")
        self.cursor.execute(command)
        self.mydb.commit()

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

    def select_columns(self, tables_list: list[str], columns_list: list[str], orderBy: str = None) -> list[tuple]:
        if not columns_list:
            return []

        way = self.get_full_way(tables_list)
        subcommand = ""
        if not way:
            way.append(tables_list[0])
        else:
            subcommand = self.get_sub_command(tables_list)

        command = (f"SELECT {', '.join(map(str, columns_list))} "
                   f"FROM {', '.join(map(str, way))} "
                   f"{subcommand}")

        if orderBy is not None:
            command += f" ORDER BY {orderBy}"

        self.cursor.execute(command)
        return self.cursor.fetchall()

    def get_sub_command(self, tables_list: list[str]) -> str:
        way = self.get_full_way(tables_list)
        sub_command = "WHERE "
        for i, table_one in enumerate(way):
            for table_two in way[(i+1):]:
                if table_two in self.dependencies[self.table_names.index(table_one)].keys():
                    relation = eval(self.dependencies[self.table_names.index(table_one)].get(table_two))
                    sub_command += f"{table_one}.{relation[0]} = {table_two}.{relation[1]} AND "
        return sub_command[:len(sub_command)-5]

    def get_relation(self, table_one: str, tables_list: list[str], used: list[str]) -> str:
        for table in self.dependencies[self.table_names.index(table_one)].keys():
            if table in tables_list and table not in used:
                return table
        return ""

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