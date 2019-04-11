import sqlite3

"""Handles persistent data in the game, including accounts, etc"""

class Database:
    account_db = None
    room_db = None
    player_db = None

    @staticmethod
    def startup():
        # Load the SQL databases
        Database.account_db = sqlite3.connect("accounts.db")
        Database.room_db = sqlite3.connect("rooms.db")
        Database.player_db = sqlite3.connect("players.db")

        # Create account tables if they don't exist
        Database.account_db.execute("CREATE TABLE IF NOT EXISTS player_accounts(name, passhash, salt)")
        Database.room_db.execute("CREATE TABLE IF NOT EXISTS rooms(title, description, connections, items)")
        Database.player_db.execute("CREATE TABLE IF NOT EXISTS players(account_name, character_name, last_room)")

    @staticmethod
    def shutdown():
        # Save and disconnect databases
        Database.account_db.commit()
        Database.account_db.close()

        Database.room_db.commit()
        Database.room_db.close()

        Database.player_db.commit()
        Database.player_db.close()