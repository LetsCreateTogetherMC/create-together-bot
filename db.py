import os
import mysql.connector

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("OS_PASSWORD")

# @todo
# 1) Add Show Leaderboards - DONE
# 2) Add delete <leaderboard>
# 3) Add Pagination to show <leaderboard>

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="nem14@NemesisDataBase",
    charset="utf8"
)
cursor = db.cursor()


def init_db(db_name: str) -> None:
    cursor.execute("SHOW DATABASES")
    dbs = cursor.fetchall()
    found = False

    for item in dbs:
        if item[0].lower() == db_name.lower():
            found = True
            break

    if found:
        print("Database Found")
        cursor.execute(f"USE {db_name}")
    else:
        print("Creating Database...")
        create_db(db_name)


def create_db(db_name: str) -> None:
    cursor.execute(f"CREATE DATABASE {db_name}")
    cursor.execute(f"USE {db_name}")
    db.commit()

    create_global_table()

    print("Database Created!")


def create_global_table() -> None:
    cursor.execute(
        f"CREATE TABLE global(leaderboard VARCHAR(100) NOT NULL, symbol VARCHAR(50) DEFAULT ':coin:')")
    db.commit()


def create_table(name: str, symbol: str = ":coin:") -> dict:
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        if table[0] == name.lower():
            return {
                "success": False,
                "message": "Leaderboard Already Exists"
            }

    cursor.execute(
        f"CREATE TABLE {name}(user_id BIGINT PRIMARY KEY, user_name VARCHAR(50) NOT NULL, points INT DEFAULT 0)")
    cursor.execute(
        f"INSERT INTO global VALUES('{name}', '{symbol}')"
    )
    db.commit()
    print(f"Created Table {name}")
    return {
        "success": True,
        "message": f"Created Leaderboard: {name}"
    }


def add_user_to_table(leaderboard: str, user_id: int, user_name: str) -> dict:
    cursor.execute(
        f"SELECT * FROM {leaderboard} WHERE user_id = '{user_id}'")
    user = cursor.fetchone()

    if user:
        print("User Already Exists!")
        return {
            "success": False,
            "message": f"User {user_name} Already exists in {leaderboard}"
        }

    cursor.execute(
        f"INSERT INTO {leaderboard}(user_id, user_name) VALUES('{user_id}', '{user_name}')")
    print("Added User")
    db.commit()

    return {
        "success": True,
        "message": f"Created User {user_name} in {leaderboard}"
    }


def add_points_to_user(leaderboard: str, user_id: int, amount: int, user_name: str) -> dict:
    cursor.execute(
        f"SELECT * FROM {leaderboard} WHERE user_id = '{user_id}'")
    user = cursor.fetchone()

    if not user:
        print(f"User not found in {leaderboard}")
        add_user_to_table(leaderboard, user_id, user_name)

    cursor.execute(f"UPDATE {leaderboard} SET points = points + {amount}")
    db.commit()

    symbol = get_symbol(leaderboard)
    print(f"Added {amount} {symbol} to {user_id}")

    return {
        "success": True,
        "message": None,
        "symbol": symbol
    }


def get_leaderboard(leaderboard: str) -> dict:
    cursor.execute(f"SELECT * FROM {leaderboard} ORDER BY points")
    data = cursor.fetchall()
    symbol = get_symbol(leaderboard)
    return {
        "success": True,
        "message": data,
        "symbol": symbol
    }


def get_leaderboards() -> dict:
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    return {
        "success": True,
        "message": tables
    }


def delete_leaderboard(leaderboard: str) -> dict:
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    found = False

    for table in tables:
        if table[0] == leaderboard.lower():
            found = True
            break

    if not found:
        return {
            "success": False,
            "message": f"Leaderboard {leaderboard} not found!"
        }

    cursor.execute(f"DROP TABLE {leaderboard}")
    cursor.execute(
        f"DELETE FROM global WHERE leaderboard LIKE '{leaderboard}'")
    db.commit()
    return {
        "success": True,
        "message": f"Deleted Leaderboard {leaderboard}"
    }


def clear_db() -> dict:
    """Deletes all the tables from the database"""
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE {table_name}")
    db.commit()

    create_global_table()

    return {
        "success": True,
        "message": "Deleted all the leaderboards"
    }

# Utils


def get_symbol(leaderboard: str) -> str:
    cursor.execute(
        f"SELECT symbol from global WHERE leaderboard LIKE '{leaderboard}'")
    symbol = cursor.fetchone()[0]
    return symbol
