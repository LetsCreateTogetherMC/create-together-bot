import mysql.connector

# @todo
# 1) Add Pagination to show <leaderboard>


class DB:
    def __init__(self, uname, pwd, host, port, db):
        self.db = mysql.connector.connect(
            host=host,
            user=uname,
            passwd=pwd,
            port=port,
            database=db,
            charset="utf8"
        )
        self.cursor = self.db.cursor()

    def init_db(self, db_name: str):
        if not self.table_exists("global"):
            self.create_global_table()

        if not self.table_exists("config"):
            self.create_config_table()

        # self.cursor.execute("SHOW DATABASES")
        # dbs = self.cursor.fetchall()
        # found = False

        # for item in dbs:
        #     if item[0].lower() == db_name.lower():
        #         found = True
        #         break

        # if found:
        #     print("Database Found")
        #     self.cursor.execute(f"USE {db_name}")
        # else:
        #     print("Creating Database...")
        #     self.create_db(db_name)

    def create_db(self, db_name: str) -> None:
        self.cursor.execute(f"CREATE DATABASE {db_name}")
        self.cursor.execute(f"USE {db_name}")
        self.db.commit()

        self.create_global_table()

        # Create Config Table as well
        self.create_config_table()

        print("Database Created!")

    def create_global_table(self) -> None:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(
            f"CREATE TABLE global(leaderboard VARCHAR(100) NOT NULL, symbol VARCHAR(50) DEFAULT ':coin:')")
        self.db.commit()

    def create_config_table(self) -> None:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(
            "CREATE TABLE config(property VARCHAR(50), value VARCHAR(70))")
        self.cursor.executemany(
            "INSERT INTO config VALUES(%s, %s)", [
                ["user_role", "bot-user"],
                ["color_success", "0x0084ff"],
                ["color_error", "0x991b1b"],
                ["broadcast_channel", ""]
            ]
        )
        self.db.commit()

    def create_table(self, name: str, symbol: str = ":coin:") -> dict:
        self.db.ping(reconnect=True, attempts=5)

        if self.table_exists(name):
            return {
                "success": False,
                "message": "Leaderboard Already Exists"
            }

        self.cursor.execute(
            f"CREATE TABLE {name}(user_id BIGINT PRIMARY KEY, user_name VARCHAR(50) NOT NULL, points INT DEFAULT 0)")
        self.cursor.execute(
            f"INSERT INTO global VALUES('{name}', '{symbol}')"
        )
        self.db.commit()
        print(f"Created Table {name}")
        return {
            "success": True,
            "message": f"Created Leaderboard: {name}"
        }

    def add_user_to_table(self, leaderboard: str, user_id: int, user_name: str) -> dict:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(
            f"SELECT * FROM {leaderboard} WHERE user_id = '{user_id}'")
        user = self.cursor.fetchone()

        if user:
            print("User Already Exists!")
            return {
                "success": False,
                "message": f"User {user_name} Already exists in {leaderboard}"
            }

        self.cursor.execute(
            f"INSERT INTO {leaderboard}(user_id, user_name) VALUES('{user_id}', '{user_name}')")
        print("Added User")
        self.db.commit()

        return {
            "success": True,
            "message": f"Created User {user_name} in {leaderboard}"
        }

    def add_points_to_user(self, leaderboard: str, user_id: int, amount: int, user_name: str) -> dict:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(
            f"SELECT * FROM {leaderboard} WHERE user_id = '{user_id}'")
        user = self.cursor.fetchone()

        if not user:
            print(f"User not found in {leaderboard}")
            self.add_user_to_table(leaderboard, user_id, user_name)

        self.cursor.execute(
            f"UPDATE {leaderboard} SET points = points + {amount} WHERE user_id = '{user_id}'")
        self.db.commit()

        symbol = self.get_symbol(leaderboard)
        print(f"Added {amount} {symbol} to {user_id}")

        return {
            "success": True,
            "message": None,
            "symbol": symbol
        }

    def get_leaderboard(self, leaderboard: str) -> dict:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(
            f"SELECT * FROM {leaderboard} ORDER BY points DESC")
        data = self.cursor.fetchall()
        symbol = self.get_symbol(leaderboard)
        return {
            "success": True,
            "message": data,
            "symbol": symbol
        }

    def get_leaderboards(self) -> dict:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()

        return {
            "success": True,
            "message": tables
        }

    def delete_leaderboard(self, leaderboard: str) -> dict:
        self.db.ping(reconnect=True, attempts=5)

        if not self.table_exists(leaderboard):
            return {
                "success": False,
                "message": f"Leaderboard {leaderboard} not found!"
            }

        self.cursor.execute(f"DROP TABLE {leaderboard}")
        self.cursor.execute(
            f"DELETE FROM global WHERE leaderboard LIKE '{leaderboard}'")
        self.db.commit()
        return {
            "success": True,
            "message": f"Deleted Leaderboard {leaderboard}"
        }

    def clear_db(self) -> dict:
        """Deletes all the tables from the database"""

        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()

        for table in tables:
            table_name = table[0]
            if table_name == "config":
                continue

            self.cursor.execute(f"DROP TABLE {table_name}")
        self.db.commit()

        self.create_global_table()

        return {
            "success": True,
            "message": "Deleted all the leaderboards"
        }

    def get_config(self, option: str = "") -> dict:
        self.db.ping(reconnect=True, attempts=5)

        query = "SELECT * FROM config"

        if option != "":
            query += f" WHERE property LIKE '{option}'"

        self.cursor.execute(query)
        values = self.cursor.fetchall()

        if len(values) == 0:
            return {
                "success": False,
                "message": f"Property `{option}` does not exist"
            }

        return {
            "success": True,
            "message": values
        }

    def set_config(self, option: str = "", value: str = "") -> dict:
        self.db.ping(reconnect=True, attempts=5)

        if option == "" or value == "":
            return {
                "success": False,
                "message": "Cannot set empty values"
            }

        self.cursor.execute(
            f"SELECT * FROM config WHERE property LIKE '{option}'")
        res = self.cursor.fetchall()

        if len(res) == 0:
            return {
                "success": False,
                "message": f"Property `{option}` does not exist"
            }

        self.cursor.execute(
            f"UPDATE config SET value = '{value}' WHERE property LIKE '{option}'")
        self.db.commit()

        return {
            "success": True,
            "message": f"Set Property `{option}` to `{value}`"
        }

    # Utils

    def get_symbol(self, leaderboard: str) -> str:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(
            f"SELECT symbol from global WHERE leaderboard LIKE '{leaderboard}'")
        symbol = self.cursor.fetchone()[0]
        return symbol

    def get_single_config(self, option: str = "") -> str:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(
            f"SELECT value FROM config WHERE property LIKE '{option}'")
        value = self.cursor.fetchone()[0]

        return value

    def table_exists(self, table_name: str) -> bool:
        self.db.ping(reconnect=True, attempts=5)

        self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        res = self.cursor.fetchall()

        return bool(len(res) > 0)
